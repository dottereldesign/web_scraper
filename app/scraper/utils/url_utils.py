# scraper/utils/url_utils.py
from scraper.logging_config import logging

from urllib.parse import urlparse


def format_url(url):
    """Ensure URL has 'https://' if missing."""
    logging.info(f"🌐 Formatting URL: {url}")
    parsed_url = urlparse(url)

    if not parsed_url.scheme:
        formatted_url = "https://" + url
        logging.info(f"🔗 No scheme detected. Updated URL: {formatted_url}")
        return formatted_url

    return url
