# scraper/extract.py
import logging
import os
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# ✅ File Extensions to Detect
FILE_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip", ".rar", ".mp3", ".mp4"}

def log_links(links, depth=0):
    """Log links in hierarchical format."""
    logging.info(f"📝 Logging {len(links)} extracted links...")
    for link in links:
        indent = "➜ " * depth  # Indentation for children
        logging.info(f"{indent}{link['name']} ({link['url']})")

        if link["children"]:
            log_links(link["children"], depth + 1)

def extract_links(driver):
    """Extracts all website links and categorizes files separately."""
    logging.info("🔍 [START] Extracting all website links...")

    root_links = []
    file_links = []  # ✅ Separate list for file links

    all_links = driver.find_elements(By.TAG_NAME, "a")
    logging.info(f"🔗 Found {len(all_links)} total links on the page.")

    for a in all_links:
        try:
            link_text = a.text.strip()
            link_url = a.get_attribute("href")

            if not link_text or not link_url:
                logging.debug("⏩ Skipping empty link.")
                continue  # Skip empty links

            parsed_url = urlparse(link_url)
            file_ext = os.path.splitext(parsed_url.path)[1].lower()

            # ✅ If it's a file, store it separately
            if file_ext in FILE_EXTENSIONS:
                logging.info(f"📂 Detected file link: {link_text} ({file_ext})")
                file_links.append({"name": link_text, "url": link_url})
                continue

            link_data = {"name": link_text, "url": link_url, "children": [], "depth": 0}
            root_links.append(link_data)

        except Exception as e:
            logging.warning(f"⚠️ Error processing link: {e}")

    logging.info(f"✅ Link extraction completed. Found {len(root_links)} standard links and {len(file_links)} file links.")
    return {"navbar_links": root_links, "file_links": file_links}

# ✅ Standard Text Extraction (All Text)
def extract_text(driver):
    """Extracts all visible text content from the page while preserving structure."""
    logging.info("📜 [START] Extracting all text content from the page...")

    soup = BeautifulSoup(driver.page_source, "lxml")
    logging.info("🔄 Parsed page source with BeautifulSoup.")

    # ✅ Exclude common repetitive elements like headers, footers, and menus
    unwanted_tags = ["nav", "header", "footer", "aside", "script", "style"]
    for unwanted in soup.find_all(unwanted_tags):
        unwanted.decompose()  # Remove unwanted elements from the soup
    logging.info(f"🗑️ Removed {len(unwanted_tags)} unwanted sections (headers, footers, scripts, etc.).")

    # ✅ Extract visible text from paragraphs, headings, and key divs
    extracted_text = []
    for el in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "span", "div"]):
        if el.get_text(strip=True):  # ✅ Ensure it's not empty
            extracted_text.append(el.get_text(strip=True))

    text_content = "\n\n".join(extracted_text)
    logging.info(f"✅ Text extraction completed. Extracted {len(text_content)} characters.")

    return text_content

# ✅ Advanced Visible Text Extraction (Avoids Hidden Elements)
def extract_visible_text(driver):
    """Extracts only visible text from the page while avoiding hidden content."""
    logging.info("📜 [START] Extracting visible text content from the page...")

    soup = BeautifulSoup(driver.page_source, "lxml")
    logging.info("🔄 Parsed page source with BeautifulSoup.")

    # ✅ Remove unwanted sections like nav, header, footer, and hidden elements
    unwanted_tags = ["nav", "header", "footer", "aside", "script", "style"]
    for unwanted in soup.find_all(unwanted_tags):
        unwanted.decompose()
    logging.info(f"🗑️ Removed {len(unwanted_tags)} unwanted sections.")

    # ✅ Extract text but **skip elements that are hidden via CSS**
    extracted_text = []
    for el in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "span", "div"]):
        if el.get_text(strip=True) and el.has_attr("style"):
            style = el["style"].lower()
            if "display:none" in style or "visibility:hidden" in style:
                logging.debug(f"⏩ Skipping hidden element: {el.name}")
                continue  # ✅ Skip hidden elements
        
        extracted_text.append(el.get_text(strip=True))

    text_content = "\n\n".join(extracted_text)
    logging.info(f"✅ Visible text extraction completed. Extracted {len(text_content)} characters.")

    return text_content
