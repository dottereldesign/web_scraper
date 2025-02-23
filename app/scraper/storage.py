# app/scraper/storage.py
import os
import logging
from urllib.parse import urlparse

BASE_DIR = "extracted_data"  # ✅ Base directory where extracted files are saved


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
