# scraper/core/browser.py

from scraper.logging_config import get_logger
import os
import shutil
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from typing import Optional

logger = get_logger(__name__)

def get_driver() -> Optional[webdriver.Firefox]:
    """Initializes and returns a Selenium WebDriver instance (no proxy)."""
    logger.info("🚀 [START] Initializing Selenium WebDriver...")

    geckodriver_path: Optional[str] = os.getenv("GECKODRIVER_PATH") or shutil.which("geckodriver")
    if not geckodriver_path:
        logger.error("❌ WebDriver (geckodriver) not found! Make sure it's installed.")
        return None

    logger.info(f"📌 Using WebDriver Path: {geckodriver_path}")

    options = Options()
    headless_mode: bool = os.getenv("USE_HEADLESS", "1") == "1"
    options.set_preference("browser.tabs.remote.autostart", False)
    if headless_mode:
        options.add_argument("-headless")

    try:
        service = Service(geckodriver_path)
        driver = webdriver.Firefox(service=service, options=options)
        logger.info(
            f"✅ WebDriver initialized (Firefox {driver.capabilities.get('browserVersion', '?')})"
        )
        return driver

    except Exception as e:
        logger.error(f"❌ WebDriver initialization failed: {e}")

        if headless_mode:
            logger.warning("⚠️ Retrying in GUI mode (headless disabled)...")
            options = Options()
            try:
                driver = webdriver.Firefox(service=service, options=options)
                logger.info(
                    f"✅ WebDriver initialized in GUI mode (Firefox {driver.capabilities.get('browserVersion', '?')})"
                )
                return driver
            except Exception as e:
                logger.error(f"❌ WebDriver failed again in GUI mode: {e}")

    return None

def close_driver(driver: Optional[webdriver.Firefox]) -> None:
    """Closes the WebDriver instance if it exists."""
    if driver:
        logger.info("🔄 Closing WebDriver...")
        driver.quit()
        logger.info("✅ WebDriver successfully closed.")
