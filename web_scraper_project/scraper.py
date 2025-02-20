# scraper.py
import cv2
import numpy as np
import logging
import os
import re
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ✅ Set up logging
logging.basicConfig(format="%(asctime)s - [%(levelname)s] - %(message)s", level=logging.DEBUG)

# ✅ Comprehensive list of navbar-related class and ID names (including rare cases)
NAVBAR_KEYWORDS = [
    "menu", "navbar", "nav", "topbar", "header", "main-menu",
    "navigation", "site-menu", "mobile-menu", "sidebar", "menubar",
    "wsite-menu-default", "wsite-nav", "nav-wrapper", "nav-bar", "nav-links",
    "menu-wrapper", "menu-list", "nav-container", "main-navigation",
    "header-nav", "top-menu", "side-menu", "bottom-menu", "menu-items"
]

def detect_navbar(url):
    """Detect navigation bars visually using OpenCV and extract links with Selenium."""
    logging.info(f"🔍 Starting Navbar Detection for: {url}")

    try:
        # ✅ Configure Selenium WebDriver (headless mode)
        options = Options()
        options.headless = True  
        service = Service(log_path=os.devnull)  # Suppress logs
        driver = webdriver.Firefox(service=service, options=options)
        driver.get(url)

        # ✅ Wait for navbar elements to load
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "nav, header, div"))
            )
            logging.info("✅ Navbar elements detected in DOM.")
        except Exception:
            logging.warning("⚠️ Navbar elements not found in initial page load.")

        # ✅ Take screenshot
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)

        # ✅ Extract only relevant navbar links
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()  # Close Selenium

        navbar_links = []
        navbar_containers = []

        # ✅ Search for <nav> and <header> elements
        navbar_containers.extend(soup.find_all(["nav", "header"]))

        # ✅ Search for <div> elements with relevant class or id names using regex
        for div in soup.find_all("div"):
            class_names = " ".join(div.get("class", [])).lower()
            id_name = div.get("id", "").lower()

            # ✅ Match class/id if it contains variations of "nav" or "menu"
            if any(re.search(rf"\b{keyword}\b", class_names) or re.search(rf"\b{keyword}\b", id_name) for keyword in NAVBAR_KEYWORDS):
                navbar_containers.append(div)

        # ✅ Extract links, handling nested spans properly
        for container in navbar_containers:
            for a_tag in container.find_all("a", href=True):
                full_url = urljoin(url, a_tag['href'])
                
                # ✅ Extract inner text, ignoring spans with `aria-hidden="true"`
                link_text = " ".join([t.strip() for t in a_tag.find_all(text=True) if not a_tag.find_parent(attrs={"aria-hidden": "true"})])
                
                if link_text:  # Only store if text exists
                    navbar_links.append((link_text, full_url))

        navbar_links = list(set(navbar_links))  # Remove duplicates

        # ✅ Use OpenCV to detect navbar structure visually
        image = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
        edges = cv2.Canny(image, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=100, maxLineGap=10)

        navbar_detected = lines is not None  # If OpenCV detects horizontal structures

        if navbar_detected:
            logging.info(f"✅ Navbar detected visually. Found {len(navbar_links)} links.")
            logging.info(f"🔗 Extracted Navbar Links: {navbar_links}")
        else:
            logging.warning("⚠️ No navbar detected visually.")

        return {
            "navbar_detected": navbar_detected,
            "navbar_links": navbar_links
        }

    except Exception as e:
        logging.error(f"❌ Error during Navbar Detection: {e}")
        return {"error": str(e)}
