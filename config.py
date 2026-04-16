"""
Production Configuration and Settings
Use this file to manage environment-specific settings
"""

import os
from typing import Optional
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings:
    """Application Settings"""

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == Environment.DEVELOPMENT

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "False").lower() == "true"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    RATE_LIMIT_WINDOW_MINUTES: int = int(os.getenv("RATE_LIMIT_WINDOW_MINUTES", "1"))

    # Cache
    CACHE_TTL_MINUTES: int = int(os.getenv("CACHE_TTL_MINUTES", "60"))

    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # API Info
    API_TITLE: str = "Translation API"
    API_DESCRIPTION: str = "Free and open-source translation API"
    API_VERSION: str = "1.0.0"

    # Features
    ENABLE_CACHE: bool = True
    ENABLE_RATE_LIMIT: bool = True
    ENABLE_LOGGING: bool = True

    @classmethod
    def get_config(cls) -> dict:
        """Get all settings as dictionary"""
        return {
            "environment": cls.ENVIRONMENT,
            "debug": cls.DEBUG,
            "host": cls.HOST,
            "port": cls.PORT,
            "rate_limit_requests": cls.RATE_LIMIT_REQUESTS,
            "rate_limit_window_minutes": cls.RATE_LIMIT_WINDOW_MINUTES,
            "cache_ttl_minutes": cls.CACHE_TTL_MINUTES,
            "cors_origins": cls.CORS_ORIGINS,
            "log_level": cls.LOG_LEVEL,
        }


# Create singleton instance
settings = Settings()
