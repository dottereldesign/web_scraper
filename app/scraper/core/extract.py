# scraper/extract.py
from scraper.logging_config import logging

import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import asyncio
from playwright.async_api import async_playwright  # ✅ Add this import

from scraper.utils import (
    get_random_headers,
    get_random_proxy,
    format_url,
    random_throttle,
    async_random_throttle,
)

from .storage import (
    get_storage_path,
    save_extracted_text,
)  # ✅ Import storage functions
import re  # ✅ Import regex module


# ✅ Store the first clean extraction
stored_text = None
last_extraction_time = 0
last_url = ""

BASE_DIR = "extracted_data"  # ✅ Base directory where all extracted files will be saved


async def async_extract_text(url):
    """Extract text from a webpage asynchronously using Playwright."""
    logging.info(f"🔍 Extracting text from: {url}")
    url = format_url(url)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(extra_http_headers=get_random_headers())
        page = await context.new_page()

        try:
            await page.goto(url, timeout=20000, wait_until="networkidle")
            await asyncio.sleep(2)  # Allow time for full page load

            page_source = await page.content()
            if not page_source:
                logging.error("❌ No HTML content retrieved.")
                return "Error: No HTML content retrieved."

            extracted_text = parse_page_text(page_source)

            # Save extracted text
            save_extracted_text(url, extracted_text)

            return extracted_text

        except Exception as e:
            logging.error(f"❌ Error extracting text: {e}")
            return f"Error extracting text: {e}"

        finally:
            await browser.close()


def parse_page_text(html):
    if not html:
        logging.error("❌ Received empty HTML content.")
        return "Error: No HTML content received."

    logging.info("🛠️ Parsing page HTML with BeautifulSoup...")
    soup = BeautifulSoup(html, "lxml")

    logging.info("🧹 Removing unnecessary elements...")
    try:
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
            tag.decompose()
    except Exception as e:
        logging.error(f"❌ Error while removing sections: {e}")

    logging.info("🔎 Extracting meaningful text elements...")
    try:
        main_content = soup.find("div", id="wsite-content") or soup.find(
            "div", class_="wsite-section-content"
        )

        if not main_content:
            logging.warning("⚠️ No identifiable main content found.")
            return "Error: No meaningful text found on the page."

        text_elements = main_content.find_all(
            ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th", "span", "div"]
        )
        logging.info(f"📄 Found {len(text_elements)} text elements in main content.")

        text_list = []
        seen_paragraphs = set()  # ✅ Track paragraphs to remove duplicates
        prev_line = ""  # ✅ Track previous line for funder duplicates

        for el in text_elements:
            extracted_text = el.get_text(separator=" ", strip=True)

            # ✅ Ignore empty or very short text (likely noise)
            if not extracted_text or len(extracted_text) < 5:
                continue

            # ✅ Skip file-related metadata
            if any(
                keyword in extracted_text.lower()
                for keyword in [
                    "file size:",
                    "file type:",
                    "download file",
                    "pdf",
                ]
            ):
                continue

            # ✅ Remove lines that are just a number followed by "kb"
            if re.match(r"^\d+\s*kb$", extracted_text.lower()):
                logging.info(f"🚀 Skipping file size reference: {extracted_text}")
                continue

            # ✅ Remove duplicate funders
            if extracted_text == prev_line:
                continue
            prev_line = extracted_text

            # ✅ Normalize case & spacing for duplicate detection
            normalized_text = " ".join(extracted_text.split()).lower()

            # ✅ If this text has already been seen, it's a duplicate → skip it
            if normalized_text in seen_paragraphs:
                continue

            text_list.append(extracted_text)
            seen_paragraphs.add(normalized_text)

        # ✅ Keep only the second instance with proper line breaks
        if len(text_list) > 1 and text_list[0].startswith(text_list[1][:30]):
            logging.info(
                "🚀 Removing first duplicated block, keeping formatted version."
            )
            text_list.pop(0)  # Remove first instance (less readable)

        # ✅ Remove last "Contact" word if it's alone at the end
        if text_list and text_list[-1].strip().lower() == "contact":
            logging.info("🚀 Removing unnecessary 'Contact' at the end.")
            text_list.pop()

        # ✅ Join paragraphs with newlines for readability
        text = "\n\n".join(text_list)

        if not text.strip():
            logging.warning("⚠️ Extracted text is empty.")
            return "Error: Extracted text is empty."

        logging.info(f"✅ Successfully extracted text ({len(text)} characters).")
        return text.strip()

    except Exception as e:
        logging.error(f"❌ Error while extracting text: {e}")
        return f"Error: Exception encountered while extracting text: {e}"
