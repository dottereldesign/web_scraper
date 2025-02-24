# app.py
import logging
import sys
import os
from flask import Flask, render_template, request
from scraper.crawler import bfs_crawl
from scraper.extract import extract_text
from dotenv import load_dotenv

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
            bfs_crawl(url, max_pages=50)  # Crawl site, storing data in extracted_data/

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
