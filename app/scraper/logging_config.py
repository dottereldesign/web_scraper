# scraper/logging_config.py
import logging
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Returns a logger instance with the given name. Sets up basic stream handler if not already configured.

    Args:
        name (Optional[str]): Name for the logger. If None, gets the root logger.
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

# Usage everywhere: `from scraper.logging_config import get_logger`
