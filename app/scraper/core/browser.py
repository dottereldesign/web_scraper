# scraper/browser.py
from scraper.logging_config import logging

import os  # ✅ Import os for environment variables
import shutil  # ✅ Import shutil to check if WebDriver exists
from selenium import webdriver  # ✅ Import Selenium WebDriver to control a browser
from selenium.webdriver.firefox.options import (
    Options,
)  # ✅ Import Firefox-specific options
from selenium.webdriver.firefox.service import Service


def get_driver():
    """Initializes and returns a Selenium WebDriver instance."""
    logging.info("🚀 [START] Initializing Selenium WebDriver...")

    # ✅ Check if 'geckodriver' is installed
    geckodriver_path = os.getenv("GECKODRIVER_PATH", shutil.which("geckodriver"))
    if not geckodriver_path:
        logging.error("❌ WebDriver (geckodriver) not found! Make sure it's installed.")
        return None

    logging.info(f"📌 Using WebDriver Path: {geckodriver_path}")

    options = Options()
    headless_mode = (
        os.getenv("USE_HEADLESS", "1") == "1"
    )  # ✅ Default: Headless enabled
    options.headless = headless_mode

    try:
        service = Service(geckodriver_path)
        driver = webdriver.Firefox(service=service, options=options)
        logging.info(
            f"✅ WebDriver initialized (Firefox {driver.capabilities['browserVersion']})"
        )
        return driver  # ✅ Return the WebDriver instance

    except Exception as e:
        logging.error(f"❌ WebDriver initialization failed: {e}")

        # ✅ If headless mode failed, retry with GUI mode
        if headless_mode:
            logging.warning("⚠️ Retrying in GUI mode (headless disabled)...")
            options.headless = False
            try:
                driver = webdriver.Firefox(
                    executable_path=geckodriver_path, options=options
                )
                logging.info(
                    f"✅ WebDriver initialized in GUI mode (Firefox {driver.capabilities['browserVersion']})"
                )
                return driver
            except Exception as e:
                logging.error(f"❌ WebDriver failed again in GUI mode: {e}")

    return None  # ✅ Return None if WebDriver fails


def close_driver(driver):
    """Closes the WebDriver instance if it exists."""
    if driver:
        logging.info("🔄 Closing WebDriver...")
        driver.quit()
        logging.info("✅ WebDriver successfully closed.")
