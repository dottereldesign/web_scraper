# app.py

import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from threading import Thread, Lock
from time import time
from typing import Optional, Any, Dict

from scraper.core.crawler import async_bfs_crawl
from scraper.logging_config import get_logger
import asyncio

load_dotenv()
SECRET_KEY: str = os.getenv("FLASK_SECRET", "fallback_secret_key")
app = Flask(__name__)
app.secret_key = SECRET_KEY
logger = get_logger(__name__)

RATE_LIMIT_SECONDS: int = 20

# ---------- NEW: In-memory task status store ----------
crawl_status_store: Dict[str, str] = {}
crawl_status_lock = Lock()

def set_crawl_status(task_id: str, status: str):
    with crawl_status_lock:
        crawl_status_store[task_id] = status

def get_crawl_status(task_id: str) -> Optional[str]:
    with crawl_status_lock:
        return crawl_status_store.get(task_id)

def run_crawl(url: str, max_pages: int, task_id: str) -> None:
    """
    Runs the async crawler in a background thread.
    Updates the crawl_status_store with crawl status.
    """
    try:
        set_crawl_status(task_id, "Crawl started...")
        asyncio.run(async_bfs_crawl(url, max_pages=max_pages, status_key=task_id, status_callback=set_crawl_status))
        set_crawl_status(task_id, "Crawl finished.")
    except Exception as e:
        logger.error(f"Crawl failed: {e}", exc_info=True)
        set_crawl_status(task_id, f"Error during crawl: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    error: Optional[str] = None
    status: Optional[str] = None
    extracted_text: Optional[str] = None
    task_id: Optional[str] = None

    if request.method == "POST":
        url: Optional[str] = request.form.get("url")
        last_crawl_any: Any = request.cookies.get("last_crawl", 0)
        try:
            last_crawl: float = float(last_crawl_any)
        except (ValueError, TypeError):
            last_crawl = 0.0
        now: float = time()
        task_id = f"crawl_{int(now*1000)}_{os.urandom(2).hex()}"  # much less collision risk

        if now - last_crawl < RATE_LIMIT_SECONDS:
            error = f"Please wait {int(RATE_LIMIT_SECONDS - (now - last_crawl))} seconds before crawling again."
        elif url:
            set_crawl_status(task_id, "Crawl started...")
            t = Thread(target=run_crawl, args=(url, 50, task_id))
            t.daemon = True
            t.start()
            status = f"Crawling started in background. Task ID: {task_id} (Refresh to update status.)"

    # Get status for any running/finished crawl (show most recent, if any)
    crawl_status: Optional[str] = None
    if task_id:
        crawl_status = get_crawl_status(task_id)
    else:
        # Try to show last task (minor: could add per-user logic)
        with crawl_status_lock:
            if crawl_status_store:
                last_task = sorted(crawl_status_store.keys())[-1]
                crawl_status = crawl_status_store[last_task]

    return render_template(
        "index.html",
        error=error,
        status=status,
        crawl_status=crawl_status,
        text=extracted_text
    )

# Optional: expose a /status/<task_id> API endpoint for JS polling

if __name__ == "__main__":
    app.run(debug=True)
