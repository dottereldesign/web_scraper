# scraper/extract.py
import logging
import time
import os
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from .utils import format_url

# ✅ Store the first clean extraction
stored_text = None
last_extraction_time = 0
last_url = ""
BASE_DIR = "extracted_data"  # ✅ Base directory where all extracted files will be saved


def extract_text(url):
    global last_extraction_time, last_url

    current_time = time.time()

    # ✅ Prevent skipping different pages (only block same URL within 3 seconds)
    if url == last_url and (current_time - last_extraction_time) < 3:
        logging.warning("⚠️ Duplicate extraction request ignored.")
        return None

    last_url = url
    last_extraction_time = current_time

    logging.info(f"🔍 [START] Extracting text from: {url}")
    url = format_url(url)

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(url, timeout=20000)
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            page_source = page.content()
            if not page_source:
                logging.error("❌ No HTML content retrieved.")
                return "Error: No HTML content retrieved."

            # ✅ Print the full HTML source for debugging

            extracted_text = parse_page_text(page_source)

            if "Error:" in extracted_text:
                logging.error("🚨 Extraction failed, skipping save.")
                return extracted_text  # Avoid saving errors

            # ✅ Get website folder name & save file
            website_folder, file_name = get_storage_path(url)
            save_extracted_text(extracted_text, website_folder, file_name)

            return extracted_text  # ✅ Return extracted text

        except Exception as e:
            logging.error(f"❌ Error extracting text: {e}")
            return f"Error extracting text: {e}"

        finally:
            browser.close()


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

        for el in text_elements:
            extracted_text = el.get_text(separator=" ", strip=True)

            # ✅ Ignore empty or very short text (likely noise)
            if not extracted_text or len(extracted_text) < 5:
                continue

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


def get_storage_path(url):
    """
    ✅ Extracts the website name from the URL and determines the folder & file name.
    - Home page (`/`) → `home.txt`
    - Other pages (`/contact`) → `contact.txt`
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc  # Get domain (e.g., "www.example.com")

    # ✅ Remove 'www.' and TLD (.com, .org, .net, etc.)
    domain = domain.replace("www.", "").split(".")[0]

    # ✅ Get route and create filename
    path = parsed_url.path.strip("/")  # Remove leading & trailing `/`
    file_name = f"{path}.txt" if path else "home.txt"  # Default to "home.txt" for `/`

    # ✅ Create folder path
    folder_path = os.path.join(BASE_DIR, domain)

    # ✅ Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)

    logging.info(f"📂 Website folder created: {folder_path}")
    logging.info(f"📄 File will be saved as: {file_name}")

    return folder_path, file_name


def save_extracted_text(text, folder_path, file_name):
    """✅ Save the extracted text to a file inside the website folder"""
    try:
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        logging.info(f"📂 Extracted text saved to {file_path}")
    except Exception as e:
        logging.error(f"❌ Error saving extracted text: {e}")
