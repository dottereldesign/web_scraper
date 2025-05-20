# scraper/core/playwright_scraper.py
import asyncio
from collections import deque
from typing import Callable, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import async_playwright

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
        start_url = start_url if start_url.startswith("http") else f"http://{start_url}"
        domain = urlparse(start_url).netloc
        queue = deque([(start_url, None)])
        visited: Set[str] = set()
        graph: Dict[str, List[str]] = {}
        count = 0
        image_count = 0
        file_count = 0

        seen_images: Set[str] = set()
        seen_files: Set[str] = set()

        async with _browser_semaphore:
            async with async_playwright() as p:
                # STEP 1: HEADFUL MODE (headless=False)
                browser = await p.chromium.launch(headless=False)  # <---- CHANGED
                context = await browser.new_context(
                    extra_http_headers=self.headers or get_random_headers()
                )

                try:
                    while queue and len(visited) < self.max_pages:
                        url, parent = queue.popleft()
                        if url in visited:
                            continue

                        logger.info(f"🔍 Visiting: {url}")
                        visited.add(url)
                        graph[url] = []

                        page = None
                        try:
                            page = await context.new_page()
                            await page.goto(url, timeout=20000, wait_until="networkidle")
                            await asyncio.sleep(2)

                            page_text = await page.inner_text("body")
                            save_text(domain, url, page_text)

                            # --- Get image/file URLs ---
                            image_urls = await page.eval_on_selector_all(
                                "img", "elements => elements.map(e => e.src)"
                            )
                            file_urls = await page.eval_on_selector_all(
                                "a", "elements => elements.map(e => e.href)"
                            )
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
                            image_urls_filtered = [urljoin(url, i) for i in image_urls if i]

                            # --- Download images/files concurrently ---
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

                            await async_random_throttle()
                            count += 1

                            # --- Progress reporting: now includes files/images ---
                            if status_callback and status_key:
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
                                status_callback(status_key, f"Error: {pe}")
                        except Exception as e:
                            logger.error(
                                f"❌ Unexpected error loading {url}: {e}",
                                exc_info=True,
                            )
                            if status_callback and status_key:
                                status_callback(status_key, f"Error: {e}")
                        finally:
                            if page is not None:
                                await page.close()
                finally:
                    await context.close()
                    await browser.close()
