# scraper/core/storage.py
import asyncio
from pathlib import Path
from typing import Optional, Set
from urllib.parse import urlparse

import aiohttp
from aiohttp import ClientError

from scraper.logging_config import get_logger
from scraper.utils.headers import get_random_headers

logger = get_logger(__name__)

BASE_DIR = Path("extracted_data")  # Base storage directory

def get_storage_path(domain: str, file_type: str = "text") -> Path:
    """Returns the correct path for storing extracted data."""
    folder_path = BASE_DIR / domain / file_type
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path

def safe_file_name_from_url(url: str) -> str:
    """
    Create a safe file name from full URL (path + query),
    prevents overwrites for /foo?a=1 vs /foo?a=2.
    """
    parsed = urlparse(url)
    path_part = parsed.path.strip("/").replace("/", "_") or "home"
    query_part = parsed.query
    if query_part:
        import hashlib
        qhash = hashlib.sha1(query_part.encode("utf-8")).hexdigest()[:8]
        path_part = f"{path_part}__{qhash}"
    return path_part

def save_text(domain: str, url: str, text: str) -> None:
    """Save extracted text from a page. Consistent emoji and layout."""
    file_name = safe_file_name_from_url(url)
    file_path = get_storage_path(domain, "text") / f"{file_name}.txt"
    file_path.write_text(text, encoding="utf-8")
    logger.info(f"           📂 Saved page text: {file_path}")

async def async_download_file(url: str, file_path: Path) -> bool:
    """Download a file asynchronously. Styled emoji logs for each outcome."""
    headers = get_random_headers()
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    try:
                        with open(file_path, "wb") as f:
                            async for chunk in resp.content.iter_chunked(1024):
                                f.write(chunk)
                        logger.info(f"✅ Downloaded file: {file_path}")
                        return True
                    except OSError as fe:
                        logger.error(f"💾❌ File write error: {file_path} — {fe}")
                else:
                    logger.error(f"🌐❌ Failed to download (HTTP {resp.status}): {url}")
    except ClientError as ce:
        logger.error(f"🔌❌ aiohttp client error: {url} — {ce}")
    except asyncio.TimeoutError:
        logger.error(f"⏰❌ Timeout when downloading: {url}")
    except Exception as e:
        logger.error(f"💥❌ Unexpected error downloading {url}: {e}")
    return False

async def async_save_image(
    domain: str, img_url: str, seen_images: Optional[Set[str]] = None
) -> bool:
    """Download and save an image asynchronously, logs with clear emoji/status."""
    parsed_url = urlparse(img_url)
    file_name = Path(parsed_url.path).name
    if not file_name:
        logger.warning(f"🖼️⚠️ Skipping image (no filename): {img_url}")
        return False

    if seen_images is not None and img_url in seen_images:
        logger.info(f"🖼️⚠️ Duplicate image, skipping: {img_url}")
        return False

    file_path = get_storage_path(domain, "images") / file_name

    if file_path.exists():
        logger.info(f"🖼️⚠️ Image already exists, skipping: {file_path}")
        if seen_images is not None:
            seen_images.add(img_url)
        return False

    success = await async_download_file(img_url, file_path)
    if seen_images is not None and success:
        seen_images.add(img_url)
    return success

async def async_save_file(
    domain: str, file_url: str, seen_files: Optional[Set[str]] = None
) -> bool:
    """
    Download and save a document or compressed file asynchronously.
    Consistent emoji logs for status.
    """
    parsed_url = urlparse(file_url)
    file_name = Path(parsed_url.path).name
    if not file_name:
        logger.warning(f"📄⚠️ Skipping file (no filename): {file_url}")
        return False

    if seen_files is not None and file_url in seen_files:
        logger.info(f"📄⚠️ Duplicate file, skipping: {file_url}")
        return False

    file_path = get_storage_path(domain, "files") / file_name

    if file_path.exists():
        logger.info(f"📄⚠️ File already exists, skipping: {file_path}")
        if seen_files is not None:
            seen_files.add(file_url)
        return False

    success = await async_download_file(file_url, file_path)
    if seen_files is not None and success:
        seen_files.add(file_url)
    return success
