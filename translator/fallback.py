"""
Fallback translation logic
Tries deep-translator first, then googletrans
"""

from typing import Tuple
import logging

logger = logging.getLogger(__name__)


async def translate_with_fallback(
    text: str, target_language: str
) -> Tuple[str, str]:
    """
    Translate text with fallback mechanism
    
    Args:
        text: Text to translate
        target_language: Target language code (e.g., 'hi', 'mr')
    
    Returns:
        Tuple of (translated_text, library_used)
        library_used: 'deep-translator' or 'googletrans'
    
    Raises:
        Exception: If both translation libraries fail
    """

    # Try deep-translator first (preferred)
    try:
        from deep_translator import GoogleTranslator

        translator = GoogleTranslator(source="auto", target=target_language)
        result = translator.translate(text)

        logger.info(f"Translated using deep-translator: {text[:50]} -> {target_language}")
        return result, "deep-translator"

    except Exception as e:
        logger.warning(f"deep-translator failed: {str(e)}")

    # Fallback to googletrans
    try:
        from googletrans import Translator

        translator = Translator()
        result = translator.translate(text, src_lang="auto", dest_lang=target_language)
        translated_text = result.get("text") if isinstance(result, dict) else result.text

        logger.info(f"Translated using googletrans: {text[:50]} -> {target_language}")
        return translated_text, "googletrans"

    except Exception as e:
        logger.error(f"googletrans also failed: {str(e)}")
        raise Exception(
            f"Translation failed with both libraries. Error: {str(e)}"
        )
