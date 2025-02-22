# scraper/browser.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def get_driver():
    """Initializes and returns a Selenium WebDriver instance."""
    options = Options()
    options.headless = False  # Set to True for headless mode
    return webdriver.Firefox(options=options)
