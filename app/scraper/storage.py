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


def download_file(url, file_path):
    """Helper function to download a file."""
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            logging.info(f"✅ Downloaded file: {file_path}")
        else:
            logging.error(
                f"❌ Failed to download file: {url} (Status Code: {response.status_code})"
            )
    except Exception as e:
        logging.error(f"❌ Error downloading {url}: {e}")


def save_image(domain, img_url):
    """Download and save an image."""
    parsed_url = urlparse(img_url)
    file_name = os.path.basename(parsed_url.path)
    if not file_name:
        return  # Skip images without filenames

    file_path = os.path.join(get_storage_path(domain, "images"), file_name)

    if os.path.exists(file_path):
        logging.info(f"⚠️ Image already exists, skipping: {file_path}")
        return

    download_file(img_url, file_path)


def save_file(domain, file_url):
    """Download and save a document or compressed file."""
    parsed_url = urlparse(file_url)
    file_name = os.path.basename(parsed_url.path)
    if not file_name:
        return

    file_path = os.path.join(get_storage_path(domain, "files"), file_name)

    if os.path.exists(file_path):
        logging.info(f"⚠️ File already exists, skipping: {file_path}")
        return

    download_file(file_url, file_path)
