from typing import Tuple, List

# Supported language codes and their names
SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "mr": "Marathi",
    "gu": "Gujarati",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
}


class ValidationError(Exception):
    """Custom validation exception"""

    pass


def validate_message(message: str) -> Tuple[bool, str]:
    """
    Validate message content
    Returns: (is_valid, error_message)
    """
    if not message:
        return False, "Message cannot be empty"

    if not isinstance(message, str):
        return False, "Message must be a string"

    if len(message.strip()) == 0:
        return False, "Message cannot contain only whitespace"

    if len(message) > 10000:
        return False, "Message is too long (max 10000 characters)"

    return True, ""


def validate_language(language: str) -> Tuple[bool, str]:
    """
    Validate language code
    Returns: (is_valid, error_message)
    """
    if not language:
        return False, "Language code cannot be empty"

    if not isinstance(language, str):
        return False, "Language code must be a string"

    language = language.lower().strip()

    if language not in SUPPORTED_LANGUAGES:
        supported = ", ".join(SUPPORTED_LANGUAGES.keys())
        return False, f"Unsupported language code '{language}'. Supported: {supported}"

    return True, ""


def validate_request(message: str, language: str) -> Tuple[bool, str]:
    """
    Validate complete request
    Returns: (is_valid, error_message)
    """
    # Validate message
    is_valid, error = validate_message(message)
    if not is_valid:
        return False, error

    # Validate language
    is_valid, error = validate_language(language)
    if not is_valid:
        return False, error

    return True, ""


def get_supported_languages() -> dict:
    """
    Get list of all supported languages
    """
    return SUPPORTED_LANGUAGES
