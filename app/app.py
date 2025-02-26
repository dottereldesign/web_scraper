# app.py
import logging
import sys
import os
from flask import Flask, render_template, request
from scraper.core.crawler import async_bfs_crawl  # Updated import
from scraper.core.extract import async_extract_text  # Updated import
from dotenv import load_dotenv
import asyncio

# ✅ Load environment variables
load_dotenv()
SECRET_KEY = os.getenv("FLASK_SECRET", "fallback_secret_key")

# ✅ Logging Setup
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
)

app = Flask(__name__)
app.secret_key = SECRET_KEY  # Use secure secret key


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            asyncio.run(async_bfs_crawl(url, max_pages=50))  # ✅ New async function

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
