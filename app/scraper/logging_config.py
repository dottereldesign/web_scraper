# scraper/logging_config.py
import logging
from typing import Optional

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Returns a logger instance with the given name, using a friendly, readable formatter.

    Args:
        name (Optional[str]): Logger name. If None, gets the root logger.
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        # Unified time, level, name, message style (matches your other logs)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
