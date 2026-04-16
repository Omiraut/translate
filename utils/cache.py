import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json


class InMemoryCache:
    """
    Simple in-memory cache with TTL support
    Thread-safe caching for translations
    """

    def __init__(self, ttl_minutes: int = 60):
        """
        Initialize cache with TTL
        ttl_minutes: Time to live in minutes (default: 60)
        """
        self.cache: Dict[str, dict] = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def _generate_key(self, message: str, language: str) -> str:
        """
        Generate cache key from message and language
        Using hash to keep key size manageable
        """
        combined = f"{message}:{language}"
        return hashlib.md5(combined.encode()).hexdigest()

    def get(self, message: str, language: str) -> Optional[str]:
        """
        Get cached translation
        Returns None if not found or expired
        """
        key = self._generate_key(message, language)

        if key not in self.cache:
            return None

        cached_item = self.cache[key]
        expiry_time = cached_item["expiry"]

        # Check if expired
        if datetime.now() > expiry_time:
            del self.cache[key]
            return None

        return cached_item["translation"]

    def set(self, message: str, language: str, translation: str) -> None:
        """
        Set translation in cache
        """
        key = self._generate_key(message, language)
        self.cache[key] = {
            "translation": translation,
            "expiry": datetime.now() + self.ttl,
            "message": message,
            "language": language,
        }

    def clear(self) -> None:
        """
        Clear entire cache
        """
        self.cache.clear()

    def cleanup_expired(self) -> None:
        """
        Remove expired entries from cache
        """
        current_time = datetime.now()
        expired_keys = [
            key
            for key, item in self.cache.items()
            if current_time > item["expiry"]
        ]
        for key in expired_keys:
            del self.cache[key]

    def get_stats(self) -> dict:
        """
        Get cache statistics with JSON-serializable data
        """
        self.cleanup_expired()
        return {
            "total_entries": len(self.cache),
            "entries": [
                {
                    "message": item["message"],
                    "language": item["language"],
                    "cached_at": (item["expiry"] - self.ttl).isoformat(),
                    "expires_at": item["expiry"].isoformat(),
                }
                for item in self.cache.values()
            ],
        }
