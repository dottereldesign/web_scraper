# scraper/utils.py
import logging
import sys
from urllib.parse import urlparse

def setup_logging():
    """Configures logging for the project."""
    if not logging.getLogger().hasHandlers():  # ✅ Prevent duplicate logging setup
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format="%(asctime)s - [%(levelname)s] - %(message)s")
    logging.info("✅ Logging setup completed.")

def format_url(url):
    """Ensure URL has 'https://' if missing."""
    logging.info(f"🌐 Formatting URL: {url}")

    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        formatted_url = "https://" + url  # ✅ Prepend https:// if no scheme is found
        logging.info(f"🔗 No scheme detected. Updated URL: {formatted_url}")
        return formatted_url

    logging.info(f"✅ URL is correctly formatted: {url}")
    return url
