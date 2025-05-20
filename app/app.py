# app.py
import os
from flask import Flask, render_template, request, jsonify, session, send_from_directory, redirect, url_for, flash
from dotenv import load_dotenv
from threading import Thread, Lock
from time import time
from typing import Optional, Any, Dict, List
from scraper.config import SCRAPER_CLS  # <-- Use config-based selector
from scraper.logging_config import get_logger
import asyncio

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
        scraper = SCRAPER_CLS(max_pages=max_pages)
        asyncio.run(scraper.crawl(url, status_key=task_id, status_callback=set_crawl_status))
        set_crawl_status(task_id, "Crawl finished.")
    except Exception as e:
        logger.error(f"Crawl failed: {e}", exc_info=True)
        set_crawl_status(task_id, f"Error during crawl: {e}")

def list_scraped_files(domain: str) -> Dict[str, List[Dict[str, str]]]:
    base_dir = os.path.join("extracted_data", domain)
    categories = {
        "images": [],
        "documents": [],
        "others": [],
    }
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
                    "path": f"/{dir_path}/{fname}",
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

@app.route("/status/<task_id>")
def crawl_status_api(task_id):
    status = get_crawl_status(task_id) or ""
    import re
    match = re.search(r"Crawled (\d+)[^\d]+(\d+)", status)
    progress = {}
    percent = 0
    if match:
        try:
            cur = int(match.group(1))
            total = int(match.group(2))
            percent = int(cur / total * 100)
            progress = {"cur": cur, "total": total, "percent": percent}
        except Exception:
            pass
    finished = False
    status_lc = status.lower()
    if "finished" in status_lc or "error" in status_lc:
        finished = True
        percent = 100
    progress['percent'] = percent
    return jsonify({"status": status, "finished": finished, "progress": progress})

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    status = None
    extracted_text = None
    task_id = None
    scraped_files = {}

    if request.method == "POST":
        url = request.form.get("url")
        last_crawl_any = request.cookies.get("last_crawl", 0)
        try:
            last_crawl = float(last_crawl_any)
        except (ValueError, TypeError):
            last_crawl = 0.0
        now = time()
        task_id = f"crawl_{int(now*1000)}_{os.urandom(2).hex()}"

        if now - last_crawl < RATE_LIMIT_SECONDS:
            error = f"Please wait {int(RATE_LIMIT_SECONDS - (now - last_crawl))} seconds before crawling again."
            flash(error, "error")
            return redirect(url_for("index"))

        if url:
            set_crawl_status(task_id, "Crawl started...")
            t = Thread(target=run_crawl, args=(url, 50, task_id))
            t.daemon = True
            t.start()
            from urllib.parse import urlparse
            domain_just_crawled = urlparse(url).netloc or url
            session["last_domain"] = domain_just_crawled
            session["last_task_id"] = task_id
            return redirect(url_for("index", task_id=task_id))  # PRG pattern!

    # GET logic
    task_id = request.args.get("task_id") or session.get("last_task_id")
    domain_to_display = session.get("last_domain")

    extracted_dirs = [
        d for d in os.listdir("extracted_data")
        if os.path.isdir(os.path.join("extracted_data", d))
    ]
    if not domain_to_display and extracted_dirs:
        domain_to_display = sorted(extracted_dirs)[-1]

    if domain_to_display and domain_to_display in extracted_dirs:
        scraped_files = list_scraped_files(domain_to_display)
        txt_dir = os.path.join("extracted_data", domain_to_display, "text")
        if os.path.exists(txt_dir):
            txt_files = [f for f in os.listdir(txt_dir) if f.endswith(".txt")]
            if txt_files:
                with open(os.path.join(txt_dir, sorted(txt_files)[-1]), "r", encoding="utf-8") as f:
                    extracted_text = f.read()

    crawl_status = None
    if task_id:
        crawl_status = get_crawl_status(task_id)
    else:
        with crawl_status_lock:
            if crawl_status_store:
                last_task = sorted(crawl_status_store.keys())[-1]
                crawl_status = crawl_status_store[last_task]
                task_id = last_task

    return render_template(
        "index.html",
        error=error,
        status=status,
        crawl_status=crawl_status,
        text=extracted_text,
        scraped_files=scraped_files,
        task_id=task_id,
    )

if __name__ == "__main__":
    app.run(debug=True)
