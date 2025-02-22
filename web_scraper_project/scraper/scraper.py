# scraper/scraper.py
import logging
from .utils import format_url, setup_logging
from .browser import get_driver
from .extract import extract_links, extract_text, extract_visible_text
from .actions import hover_over_dropdowns
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Initialize logging
setup_logging()

def detect_navbar(url, use_visible_text=False):
    """Extracts website links, files, and all text from the page."""
    logging.info(f"🔍 [START] Website link detection for: {url}")

    # ✅ Format URL before proceeding
    url = format_url(url)
    logging.info(f"🌐 Formatted URL: {url}")

    # ✅ Initialize WebDriver
    driver = get_driver()
    logging.info("🖥️ WebDriver initialized successfully.")

    try:
        # ✅ Open the website
        logging.info("🌍 Opening website in browser...")
        driver.get(url)

        # ✅ Wait until page fully loads
        logging.info("⏳ Waiting for page to fully load...")
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logging.info("✅ Page loaded successfully.")

        # ✅ Start interaction with dropdowns
        logging.info("🖱️ Hovering over dropdown menus...")
        hover_over_dropdowns(driver)

        # ✅ Extract all links
        logging.info("🔗 Extracting all links from the page...")
        structured_links = extract_links(driver)
        logging.info(f"✅ Link extraction complete. Found {len(structured_links['navbar_links'])} navbar links and {len(structured_links['file_links'])} file links.")

        # ✅ Extract page text
        logging.info("📜 Extracting page text content...")
        if use_visible_text:
            logging.info("🧐 Using **VISIBLE TEXT ONLY** mode...")
            page_text = extract_visible_text(driver)
        else:
            logging.info("📖 Extracting **ALL TEXT**, including hidden sections...")
            page_text = extract_text(driver)

        logging.info(f"✅ Text extraction complete. Extracted {len(page_text)} characters.")

    except Exception as e:
        logging.error(f"❌ An error occurred during scraping: {e}")

    finally:
        logging.info("🛑 Closing WebDriver session...")
        driver.quit()
        logging.info("✅ WebDriver closed.")

    logging.info("🎯 [FINISHED] Website scraping completed.")

    return {
        "navbar_links": structured_links["navbar_links"],
        "file_links": structured_links["file_links"],
        "page_text": page_text  # ✅ Include extracted text in the response
    }
