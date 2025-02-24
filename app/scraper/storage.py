# app/scraper/storage.py
import os
import logging
import requests
from urllib.parse import urlparse

BASE_DIR = "extracted_data"  # Base storage directory


def get_storage_path(domain, file_type="text"):
    """Returns the correct path for storing extracted data."""
    folder_path = os.path.join(BASE_DIR, domain, file_type)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def save_text(domain, url, text):
    """Save extracted text from a page."""
    file_name = urlparse(url).path.strip("/").replace("/", "_") or "home"
    file_path = os.path.join(get_storage_path(domain, "text"), f"{file_name}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    logging.info(f"📂 Saved text: {file_path}")


def save_extracted_text(text, domain, file_name):
    """Save extracted text to a file."""
    file_path = os.path.join(get_storage_path(domain, "text"), f"{file_name}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    logging.info(f"📂 Saved extracted text: {file_path}")


def save_image(domain, img_url):
    """Download and save an image."""
    file_name = os.path.basename(urlparse(img_url).path)
    file_path = os.path.join(get_storage_path(domain, "images"), file_name)  # ✅ FIXED

    try:
        response = requests.get(img_url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            logging.info(f"🖼️ Saved image: {file_path}")
    except Exception as e:
        logging.error(f"❌ Failed to download image {img_url}: {e}")


def save_file(domain, file_url):
    """Download and save a file (PDF, DOCX, etc.)."""
    file_name = os.path.basename(urlparse(file_url).path)
    file_path = os.path.join(get_storage_path(domain, "files"), file_name)  # ✅ FIXED

    try:
        response = requests.get(file_url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            logging.info(f"📄 Saved file: {file_path}")
    except Exception as e:
        logging.error(f"❌ Failed to download file {file_url}: {e}")
