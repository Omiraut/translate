import logging
import json
from datetime import datetime
from pathlib import Path


def setup_logger(name: str, log_level=logging.INFO) -> logging.Logger:
    """
    Setup logger with file and console handlers
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # File handler
    file_handler = logging.FileHandler(log_dir / "translation_api.log")
    file_handler.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


def log_request(logger: logging.Logger, method: str, endpoint: str, data: dict, ip: str):
    """
    Log incoming request
    """
    logger.info(
        f"REQUEST - Method: {method} | Endpoint: {endpoint} | IP: {ip} | Data: {json.dumps(data)}"
    )


def log_response(logger: logging.Logger, endpoint: str, status_code: int, response: dict):
    """
    Log outgoing response
    """
    logger.info(
        f"RESPONSE - Endpoint: {endpoint} | Status: {status_code} | Data: {json.dumps(response)}"
    )


def log_error(logger: logging.Logger, error_msg: str, exception: Exception = None):
    """
    Log error with exception traceback
    """
    if exception:
        logger.error(f"ERROR - {error_msg}", exc_info=True)
    else:
        logger.error(f"ERROR - {error_msg}")
