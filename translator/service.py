"""
Translation service with caching and error handling
"""

import logging
from typing import Tuple, Dict, Any
from utils.cache import InMemoryCache
from utils.validator import validate_request
from translator.fallback import translate_with_fallback

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Main translation service with caching and fallback logic
    """

    def __init__(self, cache_ttl_minutes: int = 60):
        """
        Initialize translation service
        
        Args:
            cache_ttl_minutes: Cache TTL in minutes
        """
        self.cache = InMemoryCache(ttl_minutes=cache_ttl_minutes)
        self.translation_count = 0

    async def translate(
        self, message: str, language: str
    ) -> Dict[str, Any]:
        """
        Translate message to target language with caching
        
        Args:
            message: Text to translate
            language: Target language code
        
        Returns:
            Dictionary with translated text and metadata
        
        Raises:
            ValueError: If validation fails
            Exception: If translation fails
        """

        # Validate input
        is_valid, error_msg = validate_request(message, language)
        if not is_valid:
            raise ValueError(error_msg)

        # Check cache first
        cached_translation = self.cache.get(message, language)
        if cached_translation:
            logger.info(
                f"Cache hit for: '{message[:50]}...' -> {language}"
            )
            return {
                "converted_text": cached_translation,
                "language": language,
                "cached": True,
            }

        # Perform translation
        try:
            translated_text, library_used = await translate_with_fallback(
                message, language
            )

            # Cache the result
            self.cache.set(message, language, translated_text)

            # Increment counter
            self.translation_count += 1

            logger.info(
                f"Translation successful: '{message[:50]}...' -> {language} using {library_used}"
            )

            return {
                "converted_text": translated_text,
                "language": language,
                "cached": False,
                "library": library_used,
            }

        except Exception as e:
            logger.error(
                f"Translation failed for '{message[:50]}...' -> {language}: {str(e)}"
            )
            raise

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        """
        return self.cache.get_stats()

    def clear_cache(self) -> None:
        """
        Clear all cached translations
        """
        self.cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get service statistics
        """
        return {
            "total_translations": self.translation_count,
            "cache_stats": self.get_cache_stats(),
        }
