# scraper/crawler.py
import logging
import os
import time
import random
from collections import deque
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from .storage import save_text, save_image, save_file
from .utils import format_url, get_random_headers, get_random_proxy, random_throttle


def normalize_url(base_url, link):
    """Converts relative links to absolute URLs and normalizes."""
    full_url = urljoin(base_url, link)
    parsed_url = urlparse(full_url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"  # Remove query params


def bfs_crawl(start_url, max_pages=50):
    """Crawl entire site using BFS while maintaining link hierarchy."""
    start_url = format_url(start_url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            extra_http_headers=get_random_headers()
        )  # ✅ Set rotating User-Agent

        queue = deque([(start_url, None)])
        visited = set()
        graph = {}

        domain = urlparse(start_url).netloc.replace("www.", "").split(".")[0]
        base_folder = os.path.join("extracted_data", domain)

        while queue and len(visited) < max_pages:
            url, parent = queue.popleft()
            url = format_url(url)

            if url in visited:
                continue

            print(f"🔍 Visiting: {url}")
            visited.add(url)
            graph[url] = []

            try:
                page = context.new_page()
                proxy = get_random_proxy()  # ✅ Apply proxy if available

                page.goto(url, timeout=20000, wait_until="networkidle")
                time.sleep(random.uniform(2, 4))  # ✅ Additional randomized delay

                # ✅ Extract page content BEFORE closing the page
                page_text = page.inner_text("body")
                save_text(domain, url, page_text)

                # ✅ Extract images
                image_urls = page.eval_on_selector_all(
                    "img", "elements => elements.map(e => e.src)"
                )
                for img_url in image_urls:
                    img_url = urljoin(url, img_url)
                    save_image(domain, img_url)

                # ✅ Extract downloadable files
                file_urls = page.eval_on_selector_all(
                    "a", "elements => elements.map(e => e.href)"
                )
                for file_url in file_urls:
                    if file_url.endswith(
                        (".pdf", ".docx", ".zip", ".pptx", ".xlsx", ".txt")
                    ):
                        file_url = urljoin(url, file_url)
                        save_file(domain, file_url)

                random_throttle()  # ✅ Throttle requests randomly

            except Exception as e:
                print(f"❌ Error loading {url}: {e}")

            finally:
                if "page" in locals():
                    page.close()
