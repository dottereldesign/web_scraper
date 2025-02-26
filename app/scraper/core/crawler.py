# scraper/crawler.py
from playwright.async_api import async_playwright
import asyncio
from collections import deque
import logging
from urllib.parse import urljoin, urlparse
from scraper.utils.url_utils import format_url


from scraper.utils import get_random_headers, get_random_proxy, async_random_throttle
from scraper.core.storage import save_text, save_image, save_file


async def normalize_url(base_url, link):
    """Convert relative links to absolute URLs and normalize them."""
    full_url = urljoin(base_url, link)
    parsed_url = urlparse(full_url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"


async def async_bfs_crawl(start_url, max_pages=50):
    """Crawl using Async Playwright (Breadth-First Search)"""
    start_url = format_url(start_url)  # Ensure URL is formatted correctly

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(extra_http_headers=get_random_headers())

        queue = deque([(start_url, None)])  # BFS queue (URL, Parent)
        visited = set()
        graph = {}

        while queue and len(visited) < max_pages:
            url, parent = queue.popleft()
            url = format_url(url)

            if url in visited:
                continue  # Skip already visited URLs

            logging.info(f"🔍 Visiting: {url}")
            visited.add(url)
            graph[url] = []

            try:
                page = await context.new_page()
                proxy = await get_random_proxy()  # Fetch async proxy

                await page.goto(url, timeout=20000, wait_until="networkidle")
                await asyncio.sleep(2)  # Add randomized delay

                # Extract text content
                page_text = await page.inner_text("body")
                await save_text(url, page_text)

                # Extract images
                image_urls = await page.eval_on_selector_all(
                    "img", "elements => elements.map(e => e.src)"
                )
                for img_url in image_urls:
                    img_url = urljoin(url, img_url)
                    await save_image(url, img_url)

                # Extract files
                file_urls = await page.eval_on_selector_all(
                    "a", "elements => elements.map(e => e.href)"
                )
                for file_url in file_urls:
                    if file_url.endswith(
                        (".pdf", ".docx", ".zip", ".pptx", ".xlsx", ".txt")
                    ):
                        file_url = urljoin(url, file_url)
                        await save_file(url, file_url)

                await async_random_throttle()  # Apply async throttling

            except Exception as e:
                logging.error(f"❌ Error loading {url}: {e}")

            finally:
                await page.close()

        await browser.close()
