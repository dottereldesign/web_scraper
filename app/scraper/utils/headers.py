# scraper/utils/headers.py
from scraper.logging_config import logging

import random
from fake_useragent import UserAgent

# ✅ Try initializing UserAgent
try:
    ua = UserAgent()
    USER_AGENTS = [ua.random for _ in range(20)]
except Exception as e:
    logging.error(f"❌ Failed to initialize UserAgent: {e}")
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
    ]


def get_random_headers():
    """Generate random headers with a rotating User-Agent."""
    user_agent = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": user_agent,
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }
    logging.info(f"🔀 Using User-Agent: {headers['User-Agent']}")
    return headers
