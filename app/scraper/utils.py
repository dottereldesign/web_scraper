# scraper/utils.py
import logging
import random
import time
from urllib.parse import urlparse
from fake_useragent import UserAgent
import requests

# ✅ User-Agent Rotation
ua = UserAgent()

# ✅ Free Proxy List (Optional: Use paid proxies for stability)
FREE_PROXIES = [
    "http://51.158.165.18:8811",
    "http://45.77.201.54:3128",
    "http://185.39.50.2:1337",
    "http://103.216.51.203:8191",
]


def format_url(url):
    """Ensure URL has 'https://' if missing."""
    logging.info(f"🌐 Formatting URL: {url}")
    parsed_url = urlparse(url)

    if not parsed_url.scheme:
        formatted_url = "https://" + url
        logging.info(f"🔗 No scheme detected. Updated URL: {formatted_url}")
        return formatted_url

    return url


def get_random_headers():
    """Generate random headers with a rotating User-Agent."""
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }
    logging.info(f"🔀 Using User-Agent: {headers['User-Agent']}")
    return headers


def get_random_proxy():
    """Return a random proxy from the free list."""
    if not FREE_PROXIES:
        return None  # No proxy used
    proxy = random.choice(FREE_PROXIES)
    logging.info(f"🛡️ Using Proxy: {proxy}")
    return {"http": proxy, "https": proxy}


def random_throttle():
    """Sleep for a random time between requests to prevent blocking."""
    delay = random.uniform(1.5, 4.0)  # Random delay between 1.5s and 4s
    logging.info(f"⏳ Throttling request: Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)
