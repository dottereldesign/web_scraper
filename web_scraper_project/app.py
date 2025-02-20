# app.py
from flask import Flask, render_template, request
from scraper import scrape_website
import logging

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    level=logging.DEBUG
)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    if request.method == "POST":
        url = request.form.get("url")
        logging.info(f"📥 Received scraping request for: {url}")
        data = scrape_website(url)
    
    return render_template("index.html", data=data)

if __name__ == "__main__":
    logging.info("🚀 Starting Flask App...")
    app.run(debug=True)
