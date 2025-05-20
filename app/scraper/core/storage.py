# scraper/core/storage.py
import os
from scraper.logging_config import get_logger
import requests
from urllib.parse import urlparse
from typing import Optional
from scraper.utils.headers import get_random_headers  # Add this import at top

logger = get_logger(__name__)

BASE_DIR = "extracted_data"  # Base storage directory

def get_storage_path(domain: str, file_type: str = "text") -> str:
    """Returns the correct path for storing extracted data."""
    folder_path = os.path.join(BASE_DIR, domain, file_type)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def save_text(domain: str, url: str, text: str) -> None:
    """Save extracted text from a page."""
    file_name = urlparse(url).path.strip("/").replace("/", "_") or "home"
    file_path = os.path.join(get_storage_path(domain, "text"), f"{file_name}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    logger.info(f"📂 Saved text: {file_path}")

def download_file(url: str, file_path: str) -> None:
    """Helper function to download a file."""
    try:
        headers = get_random_headers()  # <-- NEW LINE
        response = requests.get(url, headers=headers, stream=True, timeout=10)  # <-- Use headers
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            logger.info(f"✅ Downloaded file: {file_path}")
        else:
            logger.error(
                f"❌ Failed to download file: {url} (Status Code: {response.status_code})"
            )
    except Exception as e:
        logger.error(f"❌ Error downloading {url}: {e}")

def save_image(domain: str, img_url: str) -> None:
    """Download and save an image."""
    parsed_url = urlparse(img_url)
    file_name = os.path.basename(parsed_url.path)
    if not file_name:
        return  # Skip images without filenames

    file_path = os.path.join(get_storage_path(domain, "images"), file_name)

    if os.path.exists(file_path):
        logger.info(f"⚠️ Image already exists, skipping: {file_path}")
        return

    download_file(img_url, file_path)



def save_file(domain: str, file_url: str) -> None:
    """Download and save a document or compressed file."""
    parsed_url = urlparse(file_url)
    file_name = os.path.basename(parsed_url.path)
    if not file_name:
        logger.warning(f"⚠️ Skipping file with no basename: {file_url}")
        return

    file_path = os.path.join(get_storage_path(domain, "files"), file_name)

    if os.path.exists(file_path):
        logger.info(f"⚠️ File already exists, skipping: {file_path}")
        return

    download_file(file_url, file_path)

