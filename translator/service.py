"""
Translation service with caching and error handling
"""

import logging
from typing import Tuple, Dict, Any, List
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
        Supports semicolon-separated messages for batch translation
        
        Args:
            message: Text to translate (can contain semicolons for batch)
            language: Target language code
        
        Returns:
            Dictionary with translated text and metadata
        
        Raises:
            ValueError: If validation fails
            Exception: If translation fails
        """

        # Check if message contains semicolons for batch translation
        if ";" in message:
            return await self.translate_batch(message, language)

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

    async def translate_batch(
        self, message: str, language: str
    ) -> Dict[str, Any]:
        """
        Translate multiple messages separated by semicolons
        
        Args:
            message: Text with semicolon-separated phrases
            language: Target language code
        
        Returns:
            Dictionary with translated phrases and metadata
        """
        # Split by semicolon and strip whitespace
        phrases = [phrase.strip() for phrase in message.split(";")]
        phrases = [p for p in phrases if p]  # Remove empty strings
        
        if not phrases:
            raise ValueError("No valid phrases found after splitting by semicolon")
        
        # Validate language once
        is_valid, error_msg = validate_request("test", language)
        if not is_valid:
            raise ValueError(error_msg)
        
        translations = []
        cached_count = 0
        
        try:
            for phrase in phrases:
                # Validate individual phrase
                is_valid, error_msg = validate_request(phrase, language)
                if not is_valid:
                    logger.warning(f"Skipping invalid phrase: '{phrase}' - {error_msg}")
                    continue
                
                # Check cache first
                cached_translation = self.cache.get(phrase, language)
                if cached_translation:
                    translations.append({
                        "original": phrase,
                        "translated": cached_translation,
                        "cached": True,
                    })
                    cached_count += 1
                    logger.info(f"Cache hit for: '{phrase[:50]}...' -> {language}")
                else:
                    # Perform translation
                    translated_text, library_used = await translate_with_fallback(
                        phrase, language
                    )
                    
                    # Cache the result
                    self.cache.set(phrase, language, translated_text)
                    
                    # Increment counter
                    self.translation_count += 1
                    
                    translations.append({
                        "original": phrase,
                        "translated": translated_text,
                        "cached": False,
                        "library": library_used,
                    })
                    logger.info(
                        f"Translation successful: '{phrase[:50]}...' -> {language} using {library_used}"
                    )
            
            # Return formatted response
            return {
                "converted_text": translations,
                "language": language,
                "cached": False,
                "batch_mode": True,
                "total_phrases": len(translations),
                "cached_from_batch": cached_count,
            }
        
        except Exception as e:
            logger.error(f"Batch translation failed: {str(e)}")
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
