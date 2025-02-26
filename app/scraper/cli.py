# scraper/cli.py
import argparse
import asyncio
from scraper.core.crawler import async_bfs_crawl

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Scraper CLI")
    parser.add_argument("url", help="URL to start scraping")
    parser.add_argument("--max-pages", type=int, default=50, help="Max pages to crawl")

    args = parser.parse_args()
    asyncio.run(
        async_bfs_crawl(args.url, max_pages=args.max_pages)
    )  # ✅ Fix async call
