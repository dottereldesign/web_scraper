# scraper/browser.py
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def get_driver():
    """Initializes and returns a Selenium WebDriver instance."""
    logging.info("🚀 [START] Initializing Selenium WebDriver...")

    options = Options()
    options.headless = True  # ✅ Headless mode for server environments

    driver = webdriver.Firefox(options=options)
    logging.info("✅ WebDriver successfully initialized.")

    return driver
