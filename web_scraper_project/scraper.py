# scraper.py
import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import lxml  # Import lxml
from selenium.webdriver.common.by import By


# ✅ Set up logging
formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[handler])


def get_link_data(a, driver, depth=0):
    """Create a structured dictionary for a given link."""
    link_text = a.get_text(strip=True)
    link_url = urljoin(driver.current_url, a["href"])

    if not link_text:  # ✅ Skip empty links
        return None

    return {
        "name": link_text,
        "url": link_url,
        "children": [],
        "depth": depth  # ✅ Store depth instead of padding-left
    }


def log_links(links, depth=0):
    """Log links in hierarchical format."""
    for link in links:
        indent = "➜ " * depth  # Indentation for children
        logging.info(f"{indent}{link['name']} ({link['url']})")

        if link["children"]:
            log_links(link["children"], depth + 1)


def extract_links(driver):
    """Extracts links using XPath for accurate parent-child detection."""
    logging.info("🔍 Extracting all website links using XPath...")

    link_map = {}
    root_links = []

    all_links = driver.find_elements(By.TAG_NAME, "a")
    for a in all_links:
        try:
            link_text = a.text.strip()
            link_url = a.get_attribute("href")

            if not link_text or not link_url:
                continue  # Skip empty links

            # ✅ Check if the link is inside a <li> (if exists)
            try:
                parent_element = a.find_element(By.XPATH, "./ancestor::li")
                parent_link = parent_element.find_element(By.XPATH, ".//a")
                parent_url = parent_link.get_attribute("href")

                if parent_url in link_map:
                    parent_data = link_map[parent_url]
                    link_data = {"name": link_text, "url": link_url, "children": [], "depth": parent_data["depth"] + 1}
                    parent_data["children"].append(link_data)
                    logging.info(f"✅ Child detected: {link_text} under {parent_data['name']}")
                    continue  # Don't add as root
            except Exception:
                # ✅ No <li> parent found, continue as root link
                pass

            # ✅ If no parent found, add as root
            link_data = {"name": link_text, "url": link_url, "children": [], "depth": 0}
            root_links.append(link_data)
            link_map[link_url] = link_data

        except Exception as e:
            logging.warning(f"⚠️ Error processing link: {e}")

    logging.info("\n🌍 Full Website Link Structure:")
    log_links(root_links)
    return root_links


def detect_navbar(url):
    """Extracts navbar links without intercepting AJAX requests."""
    logging.info(f"🔍 Starting website link detection for: {url}")

    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)  # Standard Selenium WebDriver

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
        logging.info("✅ Page loaded successfully.")

        structured_links = extract_links(driver)

    finally:
        driver.quit()
    
    return {"navbar_links": structured_links}
