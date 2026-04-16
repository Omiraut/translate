"""
Translation API Service
A production-ready REST API for translating text using free libraries
With comprehensive authentication, error handling, and security features
"""

import os
from typing import Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import traceback

from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

from translator.service import TranslationService
from utils.logger import setup_logger, log_request, log_response, log_error
from utils.validator import get_supported_languages
from utils.auth import verify_api_key, api_key_manager, require_api_key
from utils.exceptions import (
    TranslationAPIException,
    APIKeyMissingError,
    APIKeyInvalidError,
    APIKeyExpiredError,
    PermissionDeniedError,
    ValidationError,
    TranslationError,
    RateLimitError,
    IPRateLimitError,
    APIKeyRateLimitError,
    InvalidRequestFormatError,
    InternalServerError,
)

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger(__name__)

# Configuration
REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "True").lower() == "true"

# Initialize FastAPI app
app = FastAPI(
    title="Translation API",
    description="Production-ready translation API with API key authentication, comprehensive error handling, and caching",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-API-Key"],  # Allow API Key header
)

# Initialize translation service
translation_service = TranslationService(cache_ttl_minutes=60)

# Rate limiting configuration
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW_MINUTES = int(os.getenv("RATE_LIMIT_WINDOW_MINUTES", "1"))

# Store request timestamps per IP and API Key
request_history = defaultdict(list)  # For IP-based rate limiting
api_key_history = defaultdict(list)  # For API key-based rate limiting


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class TranslationRequest(BaseModel):
    """Translation request model"""

    message: str
    language: str

    class Config:
        json_schema_extra = {
            "example": {"message": "Hi", "language": "hi"}
        }


class TranslationResponse(BaseModel):
    """Translation response model"""

    status: bool
    code: int
    message: str
    data: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": True,
                "code": 200,
                "message": "Translation successful",
                "data": {
                    "converted_text": "नमस्ते",
                    "language": "hi",
                    "cached": False,
                },
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: str
    version: str


class LanguageListResponse(BaseModel):
    """Language list response"""

    status: bool
    code: int
    data: dict


# ============================================================================
# MIDDLEWARE & RATE LIMITING
# ============================================================================


def get_client_ip(request: Request) -> str:
    """
    Extract client IP from request
    Handles X-Forwarded-For header for proxied requests
    """
    if request.headers.get("x-forwarded-for"):
        return request.headers.get("x-forwarded-for").split(",")[0].strip()
    return request.client.host


def check_ip_rate_limit(ip: str) -> Tuple[bool, Optional[int]]:
    """
    Check if IP has exceeded rate limit
    Returns: (is_allowed, remaining_seconds)
    """
    now = datetime.now()
    cutoff_time = now - timedelta(minutes=RATE_LIMIT_WINDOW_MINUTES)

    # Clean old entries
    request_history[ip] = [
        timestamp for timestamp in request_history[ip]
        if timestamp > cutoff_time
    ]

    # Check limit
    if len(request_history[ip]) >= RATE_LIMIT_REQUESTS:
        # Calculate remaining time until oldest request expires
        oldest_request = request_history[ip][0]
        remaining = int((oldest_request + timedelta(minutes=RATE_LIMIT_WINDOW_MINUTES) - now).total_seconds())
        return False, max(0, remaining)

    # Add current request
    request_history[ip].append(now)
    return True, None


def check_api_key_rate_limit(api_key: str) -> Tuple[bool, Optional[int]]:
    """
    Check if API key has exceeded rate limit
    Returns: (is_allowed, remaining_seconds)
    """
    try:
        rate_limit = api_key_manager.get_rate_limit(api_key)
    except:
        rate_limit = RATE_LIMIT_REQUESTS

    now = datetime.now()
    cutoff_time = now - timedelta(minutes=1)  # 1-minute window for API keys

    # Clean old entries
    api_key_history[api_key] = [
        timestamp for timestamp in api_key_history[api_key]
        if timestamp > cutoff_time
    ]

    # Check limit
    if len(api_key_history[api_key]) >= rate_limit:
        # Calculate remaining time
        oldest_request = api_key_history[api_key][0]
        remaining = int((oldest_request + timedelta(minutes=1) - now).total_seconds())
        return False, max(0, remaining)

    # Add current request
    api_key_history[api_key].append(now)
    return True, None


from typing import Tuple

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware - checks both IP and API key
    Skips health check and documentation endpoints
    """
    # Skip rate limiting for non-API endpoints
    if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)

    client_ip = get_client_ip(request)
    api_key = request.headers.get("X-API-Key")

    try:
        # Check API key rate limit if provided
        if api_key:
            is_allowed, remaining = check_api_key_rate_limit(api_key)
            if not is_allowed:
                logger.warning(f"API key rate limit exceeded: {api_key[:10]}...")
                raise APIKeyRateLimitError(
                    api_key_hint=api_key[:10] + "..." if len(api_key) > 10 else api_key,
                    requests_limit=api_key_manager.get_rate_limit(api_key),
                    remaining_seconds=remaining or 0,
                )
        else:
            # Check IP-based rate limit
            is_allowed, remaining = check_ip_rate_limit(client_ip)
            if not is_allowed:
                logger.warning(f"IP rate limit exceeded: {client_ip}")
                raise IPRateLimitError(
                    ip=client_ip,
                    requests_limit=RATE_LIMIT_REQUESTS,
                    window_minutes=RATE_LIMIT_WINDOW_MINUTES,
                    remaining_seconds=remaining or 0,
                )

        response = await call_next(request)
        return response

    except RateLimitError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "status": False,
                "code": e.status_code,
                "message": e.message,
                "data": e.details,
            },
        )
    except Exception as e:
        logger.error(f"Rate limit middleware error: {str(e)}", exc_info=True)
        response = await call_next(request)
        return response


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns service status and version
    """
    logger.info("Health check requested")
    return HealthResponse(
        status="ok",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
    )


@app.get("/languages", response_model=LanguageListResponse, tags=["Languages"])
async def list_languages(request: Request):
    """
    Get list of supported languages
    """
    client_ip = get_client_ip(request)
    log_request(logger, "GET", "/languages", {}, client_ip)

    try:
        languages = get_supported_languages()
        response = {
            "status": True,
            "code": 200,
            "data": languages,
        }
        log_response(logger, "/languages", 200, response)
        return response
    except Exception as e:
        log_error(logger, f"Error fetching languages: {str(e)}", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/translate", response_model=TranslationResponse, tags=["Translation"])
async def translate(request_data: TranslationRequest, request: Request):
    """
    Translate text to target language
    
    **Supports both single and batch translations:**
    - Single message: Translates a single text
    - Batch mode: Separate messages with semicolon (;) to translate multiple phrases
      Example: "Hello;Good morning;Welcome" will translate each phrase separately

    **Request Body:**
    - message: Text to translate (can contain semicolons for multiple phrases)
    - language: Target language code (e.g., 'hi', 'mr', 'gu')

    **Response:**
    - status: Success flag
    - code: HTTP status code
    - message: Status message
    - data: Translated text and metadata
      - For batch mode: Array of objects with original, translated, and cached fields
      - For single mode: String with translated text
    """
    client_ip = get_client_ip(request)
    request_payload = {"message": request_data.message, "language": request_data.language}
    log_request(logger, "POST", "/translate", request_payload, client_ip)

    try:
        # Call translation service
        result = await translation_service.translate(
            request_data.message, request_data.language.lower()
        )

        response = {
            "status": True,
            "code": 200,
            "message": "Translation successful",
            "data": result,
        }

        log_response(logger, "/translate", 200, response)
        return response

    except ValueError as e:
        # Validation error
        error_message = str(e)
        logger.warning(f"Validation error: {error_message}")

        response = {
            "status": False,
            "code": 400,
            "message": error_message,
            "data": None,
        }
        log_response(logger, "/translate", 400, response)
        raise HTTPException(status_code=400, detail=error_message)

    except Exception as e:
        # Translation error
        error_message = f"Translation failed: {str(e)}"
        log_error(logger, error_message, e)

        response = {
            "status": False,
            "code": 500,
            "message": error_message,
            "data": None,
        }
        log_response(logger, "/translate", 500, response)
        raise HTTPException(status_code=500, detail=error_message)


@app.get("/stats", tags=["Statistics"])
async def get_stats(request: Request):
    """
    Get service statistics
    Includes cache stats and translation count
    """
    client_ip = get_client_ip(request)
    log_request(logger, "GET", "/stats", {}, client_ip)

    try:
        stats = translation_service.get_stats()
        response = {
            "status": True,
            "code": 200,
            "message": "Statistics retrieved",
            "data": stats,
        }
        log_response(logger, "/stats", 200, response)
        return response
    except Exception as e:
        log_error(logger, f"Error fetching stats: {str(e)}", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/cache/clear", tags=["Cache Management"])
async def clear_cache(request: Request):
    """
    Clear the translation cache
    Admin endpoint to clear all cached translations
    """
    client_ip = get_client_ip(request)
    log_request(logger, "POST", "/cache/clear", {}, client_ip)

    try:
        translation_service.clear_cache()
        response = {
            "status": True,
            "code": 200,
            "message": "Cache cleared successfully",
            "data": None,
        }
        log_response(logger, "/cache/clear", 200, response)
        return response
    except Exception as e:
        log_error(logger, f"Error clearing cache: {str(e)}", e)
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# ERROR HANDLERS
# ============================================================================


# ============================================================================
# COMPREHENSIVE ERROR HANDLERS
# ============================================================================


@app.exception_handler(TranslationAPIException)
async def translation_api_exception_handler(request: Request, exc: TranslationAPIException):
    """Handle custom Translation API exceptions"""
    log_error(logger, f"{exc.error_code}: {exc.message}", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "code": exc.status_code,
            "message": exc.message,
            "error_code": exc.error_code,
            "data": exc.details if exc.details else None,
        },
    )


@app.exception_handler(APIKeyMissingError)
async def api_key_missing_handler(request: Request, exc: APIKeyMissingError):
    """Handle missing API key errors"""
    logger.warning(f"Missing API key from IP: {get_client_ip(request)}")
    return JSONResponse(
        status_code=401,
        content={
            "status": False,
            "code": 401,
            "message": exc.message,
            "error_code": "API_KEY_MISSING",
            "data": exc.details,
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(APIKeyInvalidError)
async def api_key_invalid_handler(request: Request, exc: APIKeyInvalidError):
    """Handle invalid API key errors"""
    logger.warning(f"Invalid API key from IP: {get_client_ip(request)}")
    return JSONResponse(
        status_code=401,
        content={
            "status": False,
            "code": 401,
            "message": exc.message,
            "error_code": "API_KEY_INVALID",
            "data": exc.details,
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(APIKeyExpiredError)
async def api_key_expired_handler(request: Request, exc: APIKeyExpiredError):
    """Handle expired API key errors"""
    logger.warning(f"Expired API key from IP: {get_client_ip(request)}")
    return JSONResponse(
        status_code=401,
        content={
            "status": False,
            "code": 401,
            "message": exc.message,
            "error_code": "API_KEY_EXPIRED",
            "data": exc.details,
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(PermissionDeniedError)
async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
    """Handle permission denied errors"""
    logger.warning(f"Permission denied for IP: {get_client_ip(request)}")
    return JSONResponse(
        status_code=403,
        content={
            "status": False,
            "code": 403,
            "message": exc.message,
            "error_code": "PERMISSION_DENIED",
            "data": exc.details,
        },
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle validation errors"""
    logger.info(f"Validation error: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={
            "status": False,
            "code": 400,
            "message": exc.message,
            "error_code": "VALIDATION_ERROR",
            "data": exc.details,
        },
    )


@app.exception_handler(TranslationError)
async def translation_error_handler(request: Request, exc: TranslationError):
    """Handle translation service errors"""
    logger.error(f"Translation error: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "code": 500,
            "message": exc.message,
            "error_code": "TRANSLATION_ERROR",
            "data": exc.details,
        },
    )


@app.exception_handler(RateLimitError)
async def rate_limit_error_handler(request: Request, exc: RateLimitError):
    """Handle rate limit errors"""
    logger.warning(f"Rate limit error: {exc.message}")
    return JSONResponse(
        status_code=429,
        content={
            "status": False,
            "code": 429,
            "message": exc.message,
            "error_code": "RATE_LIMIT_EXCEEDED",
            "data": exc.details,
        },
        headers={"Retry-After": str(exc.details.get("retry_after_seconds", 60))},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "code": exc.status_code,
            "message": str(exc.detail),
            "error_code": "HTTP_ERROR",
            "data": None,
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors"""
    logger.error(f"Value error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={
            "status": False,
            "code": 400,
            "message": str(exc),
            "error_code": "VALUE_ERROR",
            "data": None,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other unhandled exceptions"""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "code": 500,
            "message": "An unexpected error occurred. Please try again later.",
            "error_code": "INTERNAL_ERROR",
            "data": {"error_type": type(exc).__name__},
        },
    )


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Called on application startup"""
    logger.info("=" * 50)
    logger.info("Translation API Service Starting...")
    logger.info(f"Rate limit: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW_MINUTES} minute(s)")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Called on application shutdown"""
    logger.info("=" * 50)
    logger.info("Translation API Service Shutting Down...")
    logger.info(f"Total translations: {translation_service.translation_count}")
    logger.info("=" * 50)


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "True").lower() == "true"

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )
