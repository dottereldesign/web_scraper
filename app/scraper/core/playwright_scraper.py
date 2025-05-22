# app/scraper/core/playwright_scraper.py
import asyncio
import json
import re
from collections import deque
from typing import Callable, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

from playwright.async_api import Error as PlaywrightError  # type: ignore
from playwright.async_api import async_playwright  # type: ignore

from scraper.core.storage import async_save_file, async_save_image, save_text
from scraper.logging_config import get_logger
from scraper.utils.headers import get_random_headers
from scraper.utils.throttling import async_random_throttle

from .base import BaseScraper

logger = get_logger(__name__)
MAX_CONCURRENT_BROWSERS = 2
_browser_semaphore = asyncio.Semaphore(MAX_CONCURRENT_BROWSERS)


class PlaywrightScraper(BaseScraper):
    async def crawl(
        self,
        start_url: str,
        status_key: Optional[str] = None,
        status_callback: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        logger.info(f"🚀 Starting crawl with start_url: {start_url}")
        start_url = start_url if start_url.startswith("http") else f"http://{start_url}"
        domain = urlparse(start_url).netloc
        logger.info(f"🌐 Domain parsed: {domain}")
        queue = deque([(start_url, None)])
        visited: Set[str] = set()
        graph: Dict[str, List[str]] = {}
        count = 0
        image_count = 0
        file_count = 0

        seen_images: Set[str] = set()
        seen_files: Set[str] = set()

        logger.info("🔒 Waiting for browser semaphore...")
        async with _browser_semaphore:
            logger.info("✅ Acquired browser semaphore!")
            async with async_playwright() as p:
                logger.info("🎭 Launching Chromium browser (headless=False)...")
                browser = await p.chromium.launch(headless=False)
                logger.info("🌱 Creating new browser context...")
                context = await browser.new_context(
                    extra_http_headers=self.headers or get_random_headers()
                )

                try:
                    while queue and len(visited) < self.max_pages:
                        logger.info(f"📚 Queue state: {list(queue)}")
                        url, parent = queue.popleft()
                        logger.info(f"➡️ Popped URL from queue: {url}")
                        if url in visited:
                            logger.info(f"⏭️ Already visited {url}, skipping...")
                            continue

                        logger.info(f"🔍 Visiting: {url}")
                        visited.add(url)
                        graph[url] = []

                        page = None
                        try:
                            logger.info("📝 Opening new page/tab in browser...")
                            page = await context.new_page()
                            logger.info(
                                f"🌍 Navigating to {url} (timeout=20000ms, wait_until='networkidle')..."
                            )
                            await page.goto(url, timeout=20000, wait_until="networkidle")
                            logger.info("⏱️ Waiting 2 seconds for page render...")
                            await asyncio.sleep(2)

                            logger.info("📰 Extracting page text from <body>...")
                            page_text = await page.inner_text("body")
                            logger.info(f"🗂️ Saving page text for {url} ...")
                            save_text(domain, url, page_text)

                            # --- Get image/file URLs ---
                            logger.info("🖼️ Collecting image URLs (img[src])...")
                            image_urls = await page.eval_on_selector_all(
                                "img", "elements => elements.map(e => e.src)"
                            )
                            logger.info(f"🖼️ Found {len(image_urls)} image URLs.")

                            logger.info("📄 Collecting file URLs (a[href])...")
                            file_urls = await page.eval_on_selector_all(
                                "a", "elements => elements.map(e => e.href)"
                            )
                            logger.info(f"📄 Found {len(file_urls)} file URLs (all).")

                            doc_exts = (
                                ".pdf",
                                ".docx",
                                ".zip",
                                ".pptx",
                                ".xlsx",
                                ".txt",
                            )
                            file_urls_filtered = [
                                urljoin(url, f)
                                for f in file_urls
                                if f and f.lower().endswith(doc_exts)
                            ]
                            logger.info(
                                f"📄 Filtered {len(file_urls_filtered)} downloadable files."
                            )

                            image_urls_filtered = [urljoin(url, i) for i in image_urls if i]
                            logger.info(
                                f"📄 Filtered {len(image_urls_filtered)} images for download."
                            )

                            # --- Download images/files concurrently ---
                            logger.info(
                                f"⏬ Downloading images ({len(image_urls_filtered)}) and files ({len(file_urls_filtered)})..."
                            )
                            img_tasks = [
                                async_save_image(domain, img_url, seen_images)
                                for img_url in image_urls_filtered
                            ]
                            file_tasks = [
                                async_save_file(domain, file_url, seen_files)
                                for file_url in file_urls_filtered
                            ]

                            img_results = await asyncio.gather(*img_tasks, return_exceptions=True)
                            file_results = await asyncio.gather(*file_tasks, return_exceptions=True)
                            image_count += sum(1 for r in img_results if r is True)
                            file_count += sum(1 for r in file_results if r is True)
                            logger.info(
                                f"✅ Downloaded new images: {image_count}, new files: {file_count}"
                            )

                            logger.info("⏳ Throttling for random delay...")
                            await async_random_throttle()
                            count += 1

                            # --- Progress reporting: now includes files/images ---
                            if status_callback and status_key:
                                logger.info("📢 Reporting progress update via callback...")
                                status_callback(
                                    status_key,
                                    (
                                        f"Crawled {count} of {self.max_pages} | "
                                        f"Images: {image_count} | Files: {file_count}"
                                    ),
                                )

                        except PlaywrightError as pe:
                            logger.error(
                                f"❌ Playwright error loading {url}: {pe}",
                                exc_info=True,
                            )
                            if status_callback and status_key:
                                logger.info("📢 Reporting Playwright error via callback...")
                                status_callback(status_key, f"Error: {pe}")
                        except Exception as e:
                            logger.error(
                                f"❌ Unexpected error loading {url}: {e}",
                                exc_info=True,
                            )
                            if status_callback and status_key:
                                logger.info("📢 Reporting generic error via callback...")
                                status_callback(status_key, f"Error: {e}")
                        finally:
                            if page is not None:
                                logger.info(f"🔒 Closing page for {url} ...")
                                await page.close()
                finally:
                    logger.info("🔒 Closing browser context and browser...")
                    await context.close()
                    await browser.close()
                    logger.info("🛑 Crawl finished.")
