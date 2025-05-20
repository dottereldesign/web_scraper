# scraper/cli.py
import argparse
import asyncio
from scraper.config import SCRAPER_CLS  # <-- Use config-based selector

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Scraper CLI")
    parser.add_argument("url", help="URL to start scraping")
    parser.add_argument("--max-pages", type=int, default=50, help="Max pages to crawl")

    args = parser.parse_args()
    scraper = SCRAPER_CLS(max_pages=args.max_pages)
    asyncio.run(scraper.crawl(args.url))
