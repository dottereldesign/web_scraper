# scraper/actions.py
import logging
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

def hover_over_dropdowns(driver):
    """Simulates hovering over dropdown menus to trigger them."""
    logging.info("🖱️ Simulating hover over dropdowns...")

    dropdowns = driver.find_elements(By.CSS_SELECTOR, ".dropdown, .submenu, .nav-item")
    actions = ActionChains(driver)

    for menu in dropdowns:
        try:
            actions.move_to_element(menu).perform()
            time.sleep(1)  # Allow menu to appear
            logging.info(f"✅ Hovered over dropdown: {menu.text}")
        except Exception as e:
            logging.warning(f"⚠️ Failed to hover over dropdown: {e}")
