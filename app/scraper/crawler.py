# scraper/crawler.py
import logging
import os
import json
import time
from collections import deque
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from .storage import save_text, save_image, save_file  # ✅ Ensure save_text exists
from .utils import format_url  # ✅ Import format_url


def normalize_url(base_url, link):
    """Converts relative links to absolute URLs and normalizes."""
    full_url = urljoin(base_url, link)
    parsed_url = urlparse(full_url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"  # Remove query params


def bfs_crawl(start_url, max_pages=50):
    """Crawl entire site using BFS while maintaining link hierarchy."""
    start_url = format_url(start_url)  # ✅ Ensure URL has HTTPS

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        queue = deque([(start_url, None)])  # (current_page, parent_page)
        visited = set()
        graph = {}

        domain = urlparse(start_url).netloc.replace("www.", "").split(".")[0]
        base_folder = os.path.join("extracted_data", domain)

        while queue and len(visited) < max_pages:
            url, parent = queue.popleft()
            url = format_url(url)  # ✅ Ensure every URL is valid

            if url in visited:
                continue

            print(f"🔍 Visiting: {url}")
            visited.add(url)
            graph[url] = []

            try:
                page = context.new_page()
                page.goto(url, timeout=20000)
                page.wait_for_load_state("networkidle")
                time.sleep(2)

                # ✅ Extract page content BEFORE closing the page
                page_text = page.inner_text("body")
                save_text(domain, url, page_text)

                # ✅ Extract and save images
                images = page.eval_on_selector_all(
                    "img", "elements => elements.map(e => e.src)"
                )
                for img_url in images:
                    save_image(domain, urljoin(url, img_url))

                # ✅ Extract and save files (PDFs, etc.)
                files = page.eval_on_selector_all(
                    "a", "elements => elements.map(e => e.href)"
                )
                for file_url in files:
                    if file_url.endswith((".pdf", ".docx", ".zip")):
                        save_file(domain, urljoin(url, file_url))

            except Exception as e:
                print(f"❌ Error loading {url}: {e}")  # ✅ Handle error properly

            finally:
                if "page" in locals():
                    page.close()  # ✅ Close the page at the end
