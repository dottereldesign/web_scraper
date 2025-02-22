# app.py
import logging
from flask import Flask, render_template, request, redirect, url_for, session
from scraper.scraper import detect_navbar


# ✅ Custom Formatter to Truncate Logs (limits log messages to 100 characters)
class TruncatedFormatter(logging.Formatter):
    def format(self, record):
        max_length = 100  # Set max length for logs
        original_message = super().format(record)
        if len(original_message) > max_length:
            return original_message[:max_length] + "..."  # Truncate and add "..."
        return original_message

# ✅ Set up logging with truncated messages
formatter = TruncatedFormatter("%(asctime)s - [%(levelname)s] - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

app = Flask(__name__)
app.secret_key = "your_secret_key"  # ✅ Required for using session

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        logging.info(f"📥 Received navbar detection request for: {url}")
        data = detect_navbar(url)

        session["navbar_data"] = data  # ✅ Store data in session
        return redirect(url_for("index"))

    data = session.pop("navbar_data", None)  # ✅ Retrieve stored data
    return render_template("index.html", data=data)

if __name__ == "__main__":
    logging.info("🚀 Starting Flask App...")
    app.run(debug=True)