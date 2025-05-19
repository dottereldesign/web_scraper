# app.py

import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from threading import Thread, Lock
from time import time
from typing import Optional, Any, Dict, List
from scraper.core.crawler import async_bfs_crawl
from scraper.logging_config import get_logger
import asyncio
from flask import send_from_directory

load_dotenv()
SECRET_KEY: str = os.getenv("FLASK_SECRET", "fallback_secret_key")
app = Flask(__name__)
app.secret_key = SECRET_KEY
logger = get_logger(__name__)

RATE_LIMIT_SECONDS: int = 20

# ---------- In-memory task status store ----------
crawl_status_store: Dict[str, str] = {}
crawl_status_lock = Lock()

def set_crawl_status(task_id: str, status: str):
    with crawl_status_lock:
        crawl_status_store[task_id] = status

def get_crawl_status(task_id: str) -> Optional[str]:
    with crawl_status_lock:
        return crawl_status_store.get(task_id)

def run_crawl(url: str, max_pages: int, task_id: str) -> None:
    try:
        set_crawl_status(task_id, "Crawl started...")
        asyncio.run(async_bfs_crawl(url, max_pages=max_pages, status_key=task_id, status_callback=set_crawl_status))
        set_crawl_status(task_id, "Crawl finished.")
    except Exception as e:
        logger.error(f"Crawl failed: {e}", exc_info=True)
        set_crawl_status(task_id, f"Error during crawl: {e}")

def list_scraped_files(domain: str) -> Dict[str, List[Dict[str, str]]]:
    """List and categorize files scraped for a given domain."""
    base_dir = os.path.join("extracted_data", domain)
    categories = {
        "images": [],
        "documents": [],
        "others": [],
    }
    # Image and doc extensions for display logic
    img_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    doc_exts = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".txt", ".zip", ".rar"}
    for cat in ["images", "files"]:
        dir_path = os.path.join(base_dir, cat)
        if os.path.exists(dir_path):
            for fname in os.listdir(dir_path):
                ext = os.path.splitext(fname)[1].lower()
                file_info = {
                    "name": fname,
                    "ext": ext,
                    "path": f"/{dir_path}/{fname}", # Flask static serving (see NOTE below)
                }
                if ext in img_exts and cat == "images":
                    categories["images"].append(file_info)
                elif ext in doc_exts:
                    categories["documents"].append(file_info)
                else:
                    categories["others"].append(file_info)
    return categories

@app.route('/extracted_data/<path:filename>')
def extracted_data(filename):
    return send_from_directory('extracted_data', filename)

@app.route("/", methods=["GET", "POST"])
def index():
    error: Optional[str] = None
    status: Optional[str] = None
    extracted_text: Optional[str] = None
    task_id: Optional[str] = None
    scraped_files = {}

    if request.method == "POST":
        url: Optional[str] = request.form.get("url")
        last_crawl_any: Any = request.cookies.get("last_crawl", 0)
        try:
            last_crawl: float = float(last_crawl_any)
        except (ValueError, TypeError):
            last_crawl = 0.0
        now: float = time()
        task_id = f"crawl_{int(now*1000)}_{os.urandom(2).hex()}"

        if now - last_crawl < RATE_LIMIT_SECONDS:
            error = f"Please wait {int(RATE_LIMIT_SECONDS - (now - last_crawl))} seconds before crawling again."
        elif url:
            set_crawl_status(task_id, "Crawl started...")
            t = Thread(target=run_crawl, args=(url, 50, task_id))
            t.daemon = True
            t.start()
            status = f"Crawling started in background. Task ID: {task_id} (Refresh to update status.)"

    # Detect last crawled domain for display
    last_domain = None
    extracted_dirs = [
        d for d in os.listdir("extracted_data")
        if os.path.isdir(os.path.join("extracted_data", d))
    ]
    if extracted_dirs:
        last_domain = sorted(extracted_dirs)[-1]
        scraped_files = list_scraped_files(last_domain)
        # Display latest text
        txt_dir = os.path.join("extracted_data", last_domain, "text")
        if os.path.exists(txt_dir):
            txt_files = [f for f in os.listdir(txt_dir) if f.endswith(".txt")]
            if txt_files:
                with open(os.path.join(txt_dir, sorted(txt_files)[-1]), "r", encoding="utf-8") as f:
                    extracted_text = f.read()

    crawl_status: Optional[str] = None
    if task_id:
        crawl_status = get_crawl_status(task_id)
    else:
        with crawl_status_lock:
            if crawl_status_store:
                last_task = sorted(crawl_status_store.keys())[-1]
                crawl_status = crawl_status_store[last_task]

    return render_template(
        "index.html",
        error=error,
        status=status,
        crawl_status=crawl_status,
        text=extracted_text,
        scraped_files=scraped_files
    )

if __name__ == "__main__":
    app.run(debug=True)
