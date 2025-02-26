# scraper/utils/proxies.py
from scraper.logging_config import logging

import os
import random
import requests
import asyncio
import aiohttp

# ✅ Load Proxies from ENV or use defaults
FREE_PROXIES = (
    os.getenv("PROXIES", "").split(",")
    if os.getenv("PROXIES")
    else [
        "http://51.158.165.18:8811",
        "http://45.77.201.54:3128",
        "http://185.39.50.2:1337",
        "http://103.216.51.203:8191",
    ]
)


async def is_proxy_alive(proxy):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.google.com", proxy=proxy, timeout=5
            ) as response:
                return response.status == 200
    except Exception:
        return False


async def get_working_proxies():
    """Return a list of working proxies (Compatible with Python 3.8)."""
    tasks = [is_proxy_alive(proxy) for proxy in FREE_PROXIES]  # ✅ Proper async call
    results = await asyncio.gather(*tasks)
    return [proxy for proxy, alive in zip(FREE_PROXIES, results) if alive]


async def get_random_proxy():
    """Return a working proxy from the list asynchronously with retries."""
    attempts = 3  # ✅ Retry up to 3 times
    for attempt in range(attempts):
        working_proxies = await get_working_proxies()
        if working_proxies:
            proxy = random.choice(working_proxies)
            logging.info(f"🛡️ Using Proxy: {proxy}")
            return {"http": proxy, "https": proxy}
        logging.warning(
            f"⚠️ No working proxies found! Retrying ({attempt+1}/{attempts})..."
        )
        await asyncio.sleep(2**attempt)  # Exponential backoff

    logging.error("❌ Failed to find a working proxy after multiple attempts.")
    return None
