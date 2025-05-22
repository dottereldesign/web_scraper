# app/scraper/logging_config.py
import logging
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    # Remove ALL handlers so we don't stack up duplicates
    for h in logger.handlers[:]:
        logger.removeHandler(h)
    # Add our preferred handler every time
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # Set level to DEBUG for max output (change to INFO if too noisy)
    logger.setLevel(logging.DEBUG)
    # Let logs propagate up, unless this is the root
    if name:
        logger.propagate = True
    else:
        logger.propagate = False
    return logger
