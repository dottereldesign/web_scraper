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

# ✅ Set up logging
formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[handler])


def extract_links(driver):
    """Extract all visible links from the page."""
    logging.info("🔍 Extracting links from the page source...")
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = {}

    # ✅ Avoid adding empty or duplicate links
    for a in soup.find_all("a", href=True):
        link_text = a.get_text(strip=True)
        if link_text and link_text not in links:
            links[link_text] = urljoin(driver.current_url, a["href"])

    logging.info(f"✅ Extracted {len(links)} links from the page.")
    return links


def detect_navbar(url):
    """Detects navbar links efficiently without unnecessary repeated requests."""
    logging.info(f"🔍 Starting Navbar Detection for: {url}")

    try:
        # ✅ Configure Selenium WebDriver (headless mode)
        options = Options()
        options.headless = True
        service = Service(log_path=os.devnull)
        driver = webdriver.Firefox(service=service, options=options)
        logging.info("✅ WebDriver initialized successfully.")

        # ✅ Load page ONCE
        logging.info(f"🌍 Loading URL: {url}")
        driver.get(url)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
        logging.info("✅ Page loaded successfully.")

        # ✅ Wait for navbar elements (ONLY ONCE)
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav, header, div")))
            logging.info("✅ Navbar elements detected in DOM.")
        except Exception:
            logging.warning("⚠️ Navbar elements not found. Exiting early.")
            driver.quit()
            return {"error": "Navbar not detected."}  # ✅ Stop execution

        # ✅ Expand dropdowns (ONLY IF THEY EXIST)
        dropdown_buttons = driver.find_elements(By.CSS_SELECTOR, "button, .dropdown-toggle, a[aria-haspopup='true']")
        if dropdown_buttons:
            logging.info(f"🔽 Found {len(dropdown_buttons)} dropdown elements.")
            for button in dropdown_buttons:
                if button.is_displayed() and button.is_enabled():
                    try:
                        driver.execute_script(
                            "arguments[0].dispatchEvent(new Event('mouseenter', { bubbles: true }));", button
                        )
                        time.sleep(0.5)  # ✅ Small delay for UI updates
                        logging.info(f"✅ Hovered over dropdown: {button.text}")
                    except Exception:
                        logging.warning(f"⚠️ Could not hover dropdown: {button.text}")

        # ✅ Extract links (ONLY ONCE)
        all_links = extract_links(driver)

        # ✅ CLOSE SELENIUM IMMEDIATELY AFTER
        driver.quit()
        logging.info("✅ WebDriver session closed.")

        logging.info(f"🔗 Found {len(all_links)} total links after dropdown expansion.")
        return {"navbar_links": [{"name": name, "url": url} for name, url in all_links.items()]}

    except Exception as e:
        logging.error(f"❌ Error during Navbar Detection: {e}")
        return {"error": str(e)}
