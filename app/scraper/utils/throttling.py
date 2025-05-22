# app/scraper/utils/throttling.py
import asyncio
import random
import time

from scraper.logging_config import logging

last_sleep_time = 1.5  # ✅ Base delay for normal requests


def random_throttle(status_code=None):
    """Adaptive throttle mechanism with exponential backoff & jitter."""
    global last_sleep_time

    base_delay = 1.5  # ✅ Base delay for normal requests
    max_delay = 15.0  # ✅ Increased Max delay to be more cautious
    jitter = random.uniform(0.1, 3.0)  # ✅ More aggressive randomization

    if status_code in {429, 503}:  # ✅ Too Many Requests / Server Overloaded
        last_sleep_time = min(last_sleep_time * 2, max_delay)  # Exponential backoff
        logging.warning(f"⚠️ Server returned {status_code}. Increasing throttle time!")
    elif status_code == 200:  # ✅ Successful response
        last_sleep_time = max(base_delay, last_sleep_time * 0.9)  # Reduce wait time
    else:
        last_sleep_time = base_delay  # Reset if unknown response

    sleep_time = last_sleep_time + jitter  # ✅ Final calculated sleep time
    logging.info(f"⏳ Throttling request: Sleeping for {sleep_time:.2f} seconds...")
    time.sleep(sleep_time)


async def async_random_throttle(status_code=None):
    """Asynchronous version of adaptive throttle mechanism."""
    global last_sleep_time

    base_delay = 1.5
    max_delay = 15.0
    jitter = random.uniform(0.1, 3.0)

    if status_code in {429, 503}:
        last_sleep_time = min(last_sleep_time * 2, max_delay)
        logging.warning(f"⚠️ Server returned {status_code}. Increasing throttle time!")
    elif status_code == 200:
        last_sleep_time = max(base_delay, last_sleep_time * 0.9)
    else:
        last_sleep_time = base_delay

    sleep_time = last_sleep_time + jitter
    logging.info(f"⏳ Async Throttling request: Sleeping for {sleep_time:.2f} seconds...")
    await asyncio.sleep(sleep_time)
