"""
Custom exception classes for the Translation API
Provides structured error handling for all expected scenarios
"""

from typing import Optional, Dict, Any


class TranslationAPIException(Exception):
    """Base exception for Translation API"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


# ============================================================================
# AUTHENTICATION ERRORS (40x)
# ============================================================================


class AuthenticationError(TranslationAPIException):
    """Base authentication error"""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class APIKeyMissingError(AuthenticationError):
    """API key is missing from request"""

    def __init__(self):
        super().__init__(
            message="API key is required. Provide X-API-Key header.",
            details={"required_header": "X-API-Key"},
        )


class APIKeyInvalidError(AuthenticationError):
    """API key is invalid or not recognized"""

    def __init__(self, key_hint: Optional[str] = None):
        details = {"hint": key_hint} if key_hint else {}
        super().__init__(
            message="Invalid API key provided",
            details=details,
        )


class APIKeyExpiredError(AuthenticationError):
    """API key has expired"""

    def __init__(self, expiry_date: Optional[str] = None):
        details = {"expiry_date": expiry_date} if expiry_date else {}
        super().__init__(
            message="API key has expired",
            details=details,
        )


class PermissionDeniedError(TranslationAPIException):
    """User does not have permission to access resource"""

    def __init__(self, message: str = "Permission denied", resource: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="PERMISSION_DENIED",
            details={"resource": resource} if resource else {},
        )


# ============================================================================
# VALIDATION ERRORS (400)
# ============================================================================


class ValidationError(TranslationAPIException):
    """Base validation error"""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if field:
            error_details["field"] = field
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=error_details,
        )


class EmptyMessageError(ValidationError):
    """Message is empty"""

    def __init__(self):
        super().__init__(
            message="Message cannot be empty",
            field="message",
        )


class MessageTooLongError(ValidationError):
    """Message exceeds maximum length"""

    def __init__(self, length: int, max_length: int = 10000):
        super().__init__(
            message=f"Message is too long (max {max_length} characters)",
            field="message",
            details={"length": length, "max_length": max_length},
        )


class WhitespaceOnlyMessageError(ValidationError):
    """Message contains only whitespace"""

    def __init__(self):
        super().__init__(
            message="Message cannot contain only whitespace",
            field="message",
        )


class InvalidLanguageCodeError(ValidationError):
    """Language code is invalid or unsupported"""

    def __init__(self, language: str, supported_languages: Optional[list] = None):
        details = {}
        if supported_languages:
            details["supported_languages"] = supported_languages
        super().__init__(
            message=f"Unsupported language code '{language}'",
            field="language",
            details=details,
        )


class MissingLanguageError(ValidationError):
    """Language code is missing"""

    def __init__(self):
        super().__init__(
            message="Language code is required",
            field="language",
        )


class InvalidRequestFormatError(ValidationError):
    """Request body format is invalid"""

    def __init__(self, details: Optional[Dict] = None):
        super().__init__(
            message="Invalid request format. Expected JSON with 'message' and 'language' fields.",
            details=details,
        )


class MissingRequiredFieldError(ValidationError):
    """Required field is missing from request"""

    def __init__(self, field: str):
        super().__init__(
            message=f"Required field '{field}' is missing",
            field=field,
        )


class InvalidDataTypeError(ValidationError):
    """Data type is invalid"""

    def __init__(self, field: str, expected_type: str, received_type: str):
        super().__init__(
            message=f"Field '{field}' must be {expected_type}, got {received_type}",
            field=field,
            details={"expected_type": expected_type, "received_type": received_type},
        )


# ============================================================================
# TRANSLATION ERRORS (500)
# ============================================================================


class TranslationError(TranslationAPIException):
    """Base translation service error"""

    def __init__(
        self,
        message: str = "Translation failed",
        original_error: Optional[Exception] = None,
        details: Optional[Dict] = None,
    ):
        error_details = details or {}
        if original_error:
            error_details["original_error"] = str(original_error)
        super().__init__(
            message=message,
            status_code=500,
            error_code="TRANSLATION_ERROR",
            details=error_details,
        )


class TranslationServiceUnavailableError(TranslationError):
    """Translation service is unavailable"""

    def __init__(self, service_name: str = "translation service"):
        super().__init__(
            message=f"The {service_name} is currently unavailable. Please try again later.",
            details={"service": service_name},
        )


class DeepTranslatorError(TranslationError):
    """deep-translator service failed"""

    def __init__(self, original_error: Exception):
        super().__init__(
            message="deep-translator service failed",
            original_error=original_error,
            details={"service": "deep-translator"},
        )


class GoogleTransError(TranslationError):
    """googletrans service failed"""

    def __init__(self, original_error: Exception):
        super().__init__(
            message="googletrans service failed",
            original_error=original_error,
            details={"service": "googletrans"},
        )


class BothTranslatorsFailedError(TranslationError):
    """Both primary and fallback translators failed"""

    def __init__(self, primary_error: Exception, fallback_error: Exception):
        super().__init__(
            message="Both translation services failed. Please try again later.",
            details={
                "primary_error": str(primary_error),
                "fallback_error": str(fallback_error),
            },
        )


class TranslationTimeoutError(TranslationError):
    """Translation request timed out"""

    def __init__(self, timeout_seconds: int = 30):
        super().__init__(
            message=f"Translation request timed out after {timeout_seconds} seconds",
            details={"timeout_seconds": timeout_seconds},
        )


class TranslationNetworkError(TranslationError):
    """Network error during translation"""

    def __init__(self, original_error: Exception):
        super().__init__(
            message="Network error occurred during translation. Please check your internet connection.",
            original_error=original_error,
            details={"error_type": type(original_error).__name__},
        )


# ============================================================================
# RATE LIMITING ERRORS (429)
# ============================================================================


class RateLimitError(TranslationAPIException):
    """Rate limit exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        remaining_seconds: Optional[int] = None,
        details: Optional[Dict] = None,
    ):
        error_details = details or {}
        if remaining_seconds:
            error_details["retry_after_seconds"] = remaining_seconds
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details=error_details,
        )


class IPRateLimitError(RateLimitError):
    """Rate limit exceeded for IP address"""

    def __init__(self, ip: str, requests_limit: int, window_minutes: int, remaining_seconds: int):
        super().__init__(
            message=f"Rate limit exceeded. Max {requests_limit} requests per {window_minutes} minute(s)",
            remaining_seconds=remaining_seconds,
            details={
                "ip": ip,
                "limit": requests_limit,
                "window_minutes": window_minutes,
            },
        )


class APIKeyRateLimitError(RateLimitError):
    """Rate limit exceeded for API key"""

    def __init__(self, api_key_hint: str, requests_limit: int, remaining_seconds: int):
        super().__init__(
            message=f"API key rate limit exceeded. Max {requests_limit} requests per minute",
            remaining_seconds=remaining_seconds,
            details={
                "api_key": api_key_hint,
                "limit": requests_limit,
            },
        )


# ============================================================================
# CACHE ERRORS (500)
# ============================================================================


class CacheError(TranslationAPIException):
    """Base cache error"""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="CACHE_ERROR",
            details={"original_error": str(original_error)} if original_error else {},
        )


class CacheNotFoundError(CacheError):
    """Cache entry not found"""

    def __init__(self, cache_key: Optional[str] = None):
        super().__init__(
            message="Cache entry not found",
            original_error=Exception(f"Key: {cache_key}") if cache_key else None,
        )


class CacheClearError(CacheError):
    """Error clearing cache"""

    def __init__(self, original_error: Exception):
        super().__init__(
            message="Error clearing cache",
            original_error=original_error,
        )


# ============================================================================
# CONFIGURATION ERRORS (500)
# ============================================================================


class ConfigurationError(TranslationAPIException):
    """Configuration is invalid or incomplete"""

    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="CONFIGURATION_ERROR",
            details={"config_key": config_key} if config_key else {},
        )


class MissingConfigurationError(ConfigurationError):
    """Required configuration is missing"""

    def __init__(self, config_key: str):
        super().__init__(
            message=f"Required configuration '{config_key}' is missing",
            config_key=config_key,
        )


# ============================================================================
# INTERNAL ERRORS (500)
# ============================================================================


class InternalServerError(TranslationAPIException):
    """Unexpected internal server error"""

    def __init__(self, original_error: Exception, message: str = "Internal server error"):
        super().__init__(
            message=message,
            status_code=500,
            error_code="INTERNAL_ERROR",
            details={"error_type": type(original_error).__name__, "error": str(original_error)},
        )


class DatabaseError(TranslationAPIException):
    """Database operation failed"""

    def __init__(self, original_error: Exception, operation: Optional[str] = None):
        super().__init__(
            message="Database operation failed",
            status_code=500,
            error_code="DATABASE_ERROR",
            details={
                "operation": operation,
                "error": str(original_error),
            },
        )


# ============================================================================
# NOT FOUND ERRORS (404)
# ============================================================================


class NotFoundError(TranslationAPIException):
    """Resource not found"""

    def __init__(self, resource_type: str, resource_id: Optional[str] = None):
        super().__init__(
            message=f"{resource_type} not found",
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class EndpointNotFoundError(NotFoundError):
    """Endpoint not found"""

    def __init__(self, endpoint: str):
        super().__init__(
            resource_type="Endpoint",
            resource_id=endpoint,
        )
