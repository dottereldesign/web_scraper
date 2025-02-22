# scraper/utils.py
import logging
from urllib.parse import urlparse

def setup_logging():
    """Configures logging for the project."""
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[handler])

def format_url(url):
    """Ensure URL has 'https://' if missing."""
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = "https://" + url  # ✅ Prepend https:// if no scheme is found
    return url
