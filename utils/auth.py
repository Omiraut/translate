"""
API Key Authentication Module
Provides secure API key validation and management
"""

import os
import hashlib
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from fastapi import Header, HTTPException, Depends
from utils.exceptions import (
    APIKeyMissingError,
    APIKeyInvalidError,
    APIKeyExpiredError,
    PermissionDeniedError,
)


class APIKeyManager:
    """Manages API key validation and storage"""

    def __init__(self):
        """Initialize API Key Manager"""
        # Load API keys from environment or use default
        self.api_keys = self._load_api_keys()
        self.key_metadata = self._load_key_metadata()

    def _load_api_keys(self) -> Dict[str, str]:
        """
        Load API keys from environment variables
        Format: API_KEYS_JSON='{"key1": "description", "key2": "description"}'
        Or individual keys: API_KEY_DEV=xxx, API_KEY_PROD=yyy
        """
        api_keys = {}

        # Try to load from JSON format
        api_keys_json = os.getenv("API_KEYS_JSON", "{}")
        try:
            import json
            api_keys.update(json.loads(api_keys_json))
        except:
            pass

        # Load individual keys
        # Default development key (for testing)
        default_key = "sk-test-translation-api-local-dev-v1.0.0"
        api_keys.setdefault("sk-test-translation-api-local-dev-v1.0.0", "Local Development Key")

        # Load from environment variables (API_KEY_* pattern)
        for key, value in os.environ.items():
            if key.startswith("API_KEY_"):
                env_key = value
                if env_key:
                    api_keys[env_key] = f"Key from {key}"

        return api_keys

    def _load_key_metadata(self) -> Dict[str, Dict]:
        """
        Load metadata for API keys (expiration, rate limits, etc.)
        Can be extended to load from database or config file
        """
        return {
            # Default development key - never expires
            "sk-test-translation-api-local-dev-v1.0.0": {
                "name": "Local Development Key",
                "created_at": datetime.now().isoformat(),
                "expires_at": None,  # Never expires
                "rate_limit": 1000,  # Very high for dev
                "active": True,
            }
        }

    def validate_api_key(self, api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Validate API key
        Returns: (is_valid, error_message)
        """
        if not api_key:
            raise APIKeyMissingError()

        if api_key not in self.api_keys:
            raise APIKeyInvalidError(key_hint=api_key[:10] + "..." if len(api_key) > 10 else api_key)

        # Check if key is active
        metadata = self.key_metadata.get(api_key, {})
        if not metadata.get("active", True):
            raise PermissionDeniedError("API key is inactive")

        # Check if key has expired
        expires_at = metadata.get("expires_at")
        if expires_at:
            expiry_date = datetime.fromisoformat(expires_at)
            if datetime.now() > expiry_date:
                raise APIKeyExpiredError(expiry_date=expires_at)

        return True, None

    def get_key_metadata(self, api_key: str) -> Dict:
        """Get metadata for an API key"""
        return self.key_metadata.get(api_key, {})

    def is_key_active(self, api_key: str) -> bool:
        """Check if key is active"""
        metadata = self.key_metadata.get(api_key, {})
        return metadata.get("active", True)

    def get_rate_limit(self, api_key: str) -> int:
        """Get rate limit for API key (requests per minute)"""
        metadata = self.key_metadata.get(api_key, {})
        return metadata.get("rate_limit", 60)  # Default 60 req/min

    def add_api_key(self, api_key: str, name: str, rate_limit: int = 60, expires_at: Optional[str] = None):
        """Add a new API key"""
        self.api_keys[api_key] = name
        self.key_metadata[api_key] = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "rate_limit": rate_limit,
            "active": True,
        }

    def deactivate_api_key(self, api_key: str):
        """Deactivate an API key"""
        if api_key in self.key_metadata:
            self.key_metadata[api_key]["active"] = False

    def activate_api_key(self, api_key: str):
        """Activate an API key"""
        if api_key in self.key_metadata:
            self.key_metadata[api_key]["active"] = True

    def list_api_keys(self) -> Dict:
        """List all API keys (without sensitive data)"""
        return {
            key: {
                "name": self.key_metadata.get(key, {}).get("name", "Unknown"),
                "active": self.key_metadata.get(key, {}).get("active", True),
                "created_at": self.key_metadata.get(key, {}).get("created_at"),
                "expires_at": self.key_metadata.get(key, {}).get("expires_at"),
            }
            for key in self.api_keys.keys()
        }


# Global API Key Manager instance
api_key_manager = APIKeyManager()


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Dependency for FastAPI to verify API key
    Usage: Add parameter to endpoint: verify_api_key: str = Depends(verify_api_key)
    """
    if not x_api_key:
        raise APIKeyMissingError()

    try:
        api_key_manager.validate_api_key(x_api_key)
        return x_api_key
    except Exception as e:
        raise e


def require_api_key(api_key: str = Depends(verify_api_key)):
    """
    Dependency to require API key for an endpoint
    Usage: Add to endpoint: api_key: str = Depends(require_api_key)
    """
    return api_key
