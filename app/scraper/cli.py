# scraper/cli.py
import argparse
import asyncio

from scraper.config import SCRAPER_CLS
from scraper.utils.url_utils import format_url, is_valid_url  # NEW: import

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Scraper CLI")
    parser.add_argument("url", help="URL to start scraping")
    parser.add_argument("--max-pages", type=int, default=50, help="Max pages to crawl")

    args = parser.parse_args()
    url = args.url.strip()
    if not is_valid_url(url):
        print("ERROR: Please enter a valid URL (e.g., example.com or https://example.com).")
        exit(1)
    url = format_url(url)
    scraper = SCRAPER_CLS(max_pages=args.max_pages)
    asyncio.run(scraper.crawl(url))
