# scraper/core/crawler.py
from playwright._impl._api_structures import ProxySettings  # For type checking (if needed)
import asyncio
from collections import deque
from urllib.parse import urljoin, urlparse
from scraper.utils.url_utils import format_url
from scraper.utils.headers import get_random_headers
from scraper.utils.proxies import get_random_proxy
from scraper.utils.throttling import async_random_throttle
from scraper.core.storage import save_text, save_image, save_file
from scraper.logging_config import get_logger
from typing import Any, Dict, List, Optional, Set, Callable
from playwright.async_api import async_playwright


logger = get_logger(__name__)

MAX_CONCURRENT_BROWSERS = 2
_browser_semaphore = asyncio.Semaphore(MAX_CONCURRENT_BROWSERS)

async def normalize_url(base_url: str, link: str) -> str:
    full_url = urljoin(base_url, link)
    parsed_url = urlparse(full_url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

async def async_bfs_crawl(
    start_url: str,
    max_pages: int = 50,
    status_key: Optional[str] = None,
    status_callback: Optional[Callable[[str, str], None]] = None,
) -> None:
    start_url = format_url(start_url)
    domain = urlparse(start_url).netloc

    queue = deque([(start_url, None)])
    visited: Set[str] = set()
    graph: Dict[str, List[str]] = {}

    count = 0

    async with _browser_semaphore:
        # --- Get a proxy string, if available ---
        proxy_config = await get_random_proxy()
        proxy_settings = None
        if proxy_config and "http" in proxy_config:
            proxy_settings = {"server": proxy_config["http"]}
            logger.info(f"🛡️ Using Proxy for Playwright: {proxy_settings['server']}")

        async with async_playwright() as p:
            # Correct launch args (proxy, headless)
            if proxy_settings:
            # Use type: ignore to skip Pyright warning, as the structure is correct at runtime
                browser = await p.chromium.launch(headless=True, proxy=proxy_settings) # type: ignore
            else:
                browser = await p.chromium.launch(headless=True)

            context = await browser.new_context(extra_http_headers=get_random_headers())

            try:
                while queue and len(visited) < max_pages:
                    url, parent = queue.popleft()
                    url = format_url(url)

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
                            status_callback(status_key, f"Crawled {count} pages...")

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
