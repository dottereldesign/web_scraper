# scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from collections import defaultdict
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import logging
import time

# ✅ Set up logging for structured debugging
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    level=logging.DEBUG
)

def build_tree(urls):
    """Convert list of URLs into a directory tree structure."""
    tree = defaultdict(dict)
    
    for url in urls:
        parts = urlparse(url).path.strip("/").split("/")
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
    
    return tree

def detect_navbar(url):
    """Detect navigation bars visually using OpenCV."""
    logging.info(f"🔍 Starting Navbar Detection for: {url}")
    
    try:
        # ✅ Define desired capabilities to suppress excessive logging
        d = DesiredCapabilities.FIREFOX
        d["goog:loggingPrefs"] = {"browser": "WARNING", "driver": "WARNING"}

        driver = webdriver.Firefox(desired_capabilities=d)
        driver.get(url)
        
        logging.info("✅ Page loaded successfully, screenshot taken.")
        
        # Take full-page screenshot
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        driver.quit()

        # Load image in grayscale
        image = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)

        # Edge detection (finds structured elements)
        edges = cv2.Canny(image, 50, 150)

        # Find horizontal structures (likely navbars)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=100, maxLineGap=10)

        if lines is not None:
            logging.info("✅ Navbar detected visually using OpenCV.")
        else:
            logging.warning("⚠️ No navbar detected visually.")
        
        return lines is not None

    except Exception as e:
        logging.error(f"❌ Error during Navbar Detection: {e}")
        return False



def extract_navbar_links(soup, url):
    """Extracts links found inside the <nav> and <header> elements."""
    logging.info(f"🔍 Extracting Navbar Links from {url}")

    navbar_links = []
    nav_elements = soup.find_all(["nav", "header"])

    if not nav_elements:
        logging.warning("⚠️ No <nav> or <header> elements found in page structure.")

    for nav in nav_elements:
        for a_tag in nav.find_all("a", href=True):
            full_url = urljoin(url, a_tag['href'])
            navbar_links.append(full_url)

    navbar_links = list(set(navbar_links))  # Remove duplicates

    if navbar_links:
        logging.info(f"✅ Found {len(navbar_links)} Navbar Links: {navbar_links}")
    else:
        logging.warning("⚠️ No Navbar Links Found!")

    return navbar_links

def scrape_website(url):
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        logging.info(f"🌐 Fetching website: {url}")
        start_time = time.time()

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        load_time = time.time() - start_time
        logging.info(f"✅ Website loaded in {load_time:.2f} seconds")

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract all unique links
        all_links = set()
        for a_tag in soup.find_all("a", href=True):
            full_url = urljoin(url, a_tag['href'])
            parsed = urlparse(full_url)

            # Keep only internal links
            if parsed.netloc == urlparse(url).netloc:
                all_links.add(full_url)

        logging.info(f"🔗 Found {len(all_links)} total internal links.")

        # Convert links to a tree structure
        tree_structure = build_tree(all_links)

        # Detect if a navbar is present visually
        navbar_detected = detect_navbar(url)

        # Extract actual navbar links
        navbar_links = extract_navbar_links(soup, url)

        logging.info(f"✅ Scraping Completed Successfully!")

        return {
            "title": soup.title.string if soup.title else "No title found",
            "tree": tree_structure,
            "navbar_detected": navbar_detected,
            "navbar_links": navbar_links  # Return extracted navbar links
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Request Error: {e}")
        return {"error": str(e)}
