# app.py
import logging
import sys
import os
from flask import Flask, render_template, request, session
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
    text = None
    if request.method == "POST":
        url = request.form.get("url")
        logging.info(f"📥 Extracting text from: {url}")
        text = extract_text(url)
        session["page_text"] = text  # Store text in session

    text = session.pop("page_text", None)  # Retrieve stored text
    return render_template("index.html", text=text)


if __name__ == "__main__":
    logging.info("🚀 Starting Flask App...")
    app.run(debug=True)
