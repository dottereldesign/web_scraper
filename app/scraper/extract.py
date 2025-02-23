# scraper/extract.py
import logging
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .browser import get_driver
import time
from .utils import format_url


def extract_text(url):
    """
    Extracts all meaningful text from a webpage using Selenium and BeautifulSoup.

    Steps:
    1. Formats the URL to ensure it has "https://"
    2. Initializes the Selenium WebDriver
    3. Opens the webpage in a headless browser
    4. Waits for the page to fully load
    5. Extracts the page source HTML
    6. Parses and cleans the HTML to extract readable text
    7. Returns the extracted text
    """

    logging.info(f"🔍 [START] Extracting text from: {url}")

    # Ensure URL has "https://" if missing
    url = format_url(url)
    logging.info(f"🔗 Formatted URL: {url}")

    # Initialize Selenium WebDriver (Headless Firefox)
    driver = get_driver()

    try:
        logging.info("🌍 Opening website in browser...")
        driver.get(url)

        # Wait until JavaScript-rendered content is fully loaded
        logging.info("⏳ Waiting for page to fully load...")
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Extra delay to allow any remaining JavaScript to execute
        logging.info("⏳ Extra buffer sleep for JS-heavy pages...")
        time.sleep(3)

        logging.info("✅ Page loaded successfully.")

        # Extract the page source (HTML)
        page_source = driver.page_source

        if not page_source:
            logging.error("❌ Empty page source received.")
            return "Error: No HTML content retrieved."

        logging.info(f"📝 Raw page source length: {len(page_source)} characters")

        # Parse and clean the extracted HTML
        text = parse_page_text(page_source)
        logging.info(f"✅ Extracted {len(text)} characters.")

    except Exception as e:
        logging.error(f"❌ Error extracting text: {e}")
        text = f"Error extracting text: {e}"

    finally:
        # Close the WebDriver to free resources
        driver.quit()
        logging.info("✅ WebDriver closed.")

    return text


def parse_page_text(html):
    """
    Parses the page HTML using BeautifulSoup to extract meaningful text.

    Steps:
    1. Removes unnecessary sections like navigation, headers, footers, scripts, and styles
    2. Removes hidden elements (display: none, aria-hidden)
    3. Extracts text from paragraphs, headings, lists, tables, spans, and divs
    4. Joins the extracted text and returns it in a clean format
    """

    if not html:
        logging.error("❌ Received empty HTML content.")
        return "Error: No HTML content received."

    logging.info("🛠️ Parsing page HTML with BeautifulSoup...")
    soup = BeautifulSoup(html, "lxml")

    logging.info(
        "🧹 Removing unnecessary sections (nav, header, footer, scripts, styles, forms, buttons, menus)..."
    )

    try:
        # Remove elements that typically contain non-content sections
        for tag in soup.find_all(
            [
                "nav",
                "header",
                "footer",
                "aside",
                "script",
                "style",
                "form",
                "button",
                "iframe",
                "noscript",
            ]
        ):
            logging.debug(f"🚮 Removing {tag.name} element.")
            tag.decompose()

        # Remove elements with specific classes (menus, empty containers, video embeds, etc.)
        for tag in soup.find_all(
            class_=[
                "wsite-menu-default",
                "wsite-youtube",
                "wsite-cart-contents",
                "wsite-section-elements",
                "container",
            ]
        ):
            logging.debug(f"🚮 Removing class-based element: {tag.name}")
            tag.decompose()

    except Exception as e:
        logging.error(f"❌ Error while removing sections: {e}")

    logging.info("🧹 Removing hidden elements (display: none, aria-hidden)...")

    try:
        for tag in soup.find_all(style=True):
            # Get the 'style' attribute safely (avoid NoneType errors)
            style = tag.get("style", "")
            if isinstance(style, str) and "display: none" in style:
                logging.debug(f"🚮 Removing hidden element: {tag.name}")
                tag.decompose()

        for tag in soup.find_all(attrs={"aria-hidden": "true"}):
            logging.debug(f"🚮 Removing aria-hidden element: {tag.name}")
            tag.decompose()

    except Exception as e:
        logging.error(f"❌ Error while removing hidden elements: {e}")

    logging.info(
        "🔎 Extracting meaningful text elements (p, h1-h6, li, td, th, span, div)..."
    )

    try:
        # Extract text from paragraphs, headings, lists, tables, spans, links, and **divs**
        text_elements = soup.find_all(
            ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th", "span", "div"]
        )

        if not text_elements:
            logging.warning("⚠️ No text elements found on the page.")
            return "Error: No readable text found on the page."

        logging.info(f"📄 Found {len(text_elements)} text elements on the page.")

        text_list = []
        for el in text_elements:
            extracted_text = el.get_text(
                separator=" ", strip=True
            )  # Preserve line breaks
            if (
                extracted_text and len(extracted_text) > 5
            ):  # Ignore very short text (e.g., menu items)
                text_list.append(extracted_text)
                logging.debug(
                    f"✅ Extracted text: {extracted_text[:50]}..."
                )  # Preview of extracted text

        # Join extracted text with double newlines for readability
        text = "\n\n".join(text_list)

        if not text:
            logging.warning("⚠️ Extracted text is empty.")
            return "Error: Extracted text is empty."

        logging.info(f"✅ Extracted {len(text)} characters of text.")
        return text.strip()

    except Exception as e:
        logging.error(f"❌ Error while extracting text: {e}")
        return f"Error: Exception encountered while extracting text: {e}"
