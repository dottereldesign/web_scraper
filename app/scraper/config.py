# scraper/config.py
import os

MAX_PAGES = 50
HEADLESS_MODE = os.getenv("USE_HEADLESS", "1") == "1"
TIMEOUT = 20000  # 20 seconds
PROXY_RETRY_ATTEMPTS = 3
USER_AGENT_POOL_SIZE = 20
