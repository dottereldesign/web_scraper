# scraper/core/playwright_scraper.py

import asyncio
from collections import deque
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright

from .base import BaseScraper
from scraper.utils.headers import get_random_headers
from scraper.utils.throttling import async_random_throttle
from scraper.core.storage import save_text, save_image, save_file
from scraper.logging_config import get_logger

from typing import Any, Dict, List, Optional, Set, Callable

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

        async with _browser_semaphore:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(extra_http_headers=self.headers or get_random_headers())

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

                            image_urls = await page.eval_on_selector_all(
                                "img", "elements => elements.map(e => e.src)"
                            )
                            for img_url in image_urls:
                                img_url = urljoin(url, img_url)
                                save_image(domain, img_url)

                            file_urls = await page.eval_on_selector_all(
                                "a", "elements => elements.map(e => e.href)"
                            )
                            for file_url in file_urls:
                                if file_url.endswith(
                                    (".pdf", ".docx", ".zip", ".pptx", ".xlsx", ".txt")
                                ):
                                    file_url = urljoin(url, file_url)
                                    save_file(domain, file_url)

                            await async_random_throttle()
                            count += 1

                            if status_callback and status_key:
                                status_callback(status_key, f"Crawled {count} of {self.max_pages}")

                        except Exception as e:
                            logger.error(f"❌ Error loading {url}: {e}", exc_info=True)
                            if status_callback and status_key:
                                status_callback(status_key, f"Error: {e}")
                        finally:
                            if page is not None:
                                await page.close()
                finally:
                    await context.close()
                    await browser.close()
