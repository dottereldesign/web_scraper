# scraper/utils/url_utils.py
import re
from urllib.parse import urlparse

from scraper.logging_config import logging


def format_url(url: str) -> str:
    """Ensure URL has 'https://' if missing."""
    logging.info(f"🌐 Formatting URL: {url}")
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        formatted_url = "https://" + url
        logging.info(f"🔗 No scheme detected. Updated URL: {formatted_url}")
        return formatted_url
    return url


def is_valid_url(url: str) -> bool:
    """
    Checks if the provided string is a valid URL (scheme, netloc, basic domain).
    """
    if not isinstance(url, str) or not url:
        return False
    url = url.strip()
    # Accept either http(s)://domain or just domain
    if not re.match(r"^(https?://)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", url):
        return False
    parsed = urlparse(format_url(url))
    if parsed.scheme not in ("http", "https"):
        return False
    if not parsed.netloc or "." not in parsed.netloc:
        return False
    # Optional: further restrict/allow only certain domains, etc.
    return True
