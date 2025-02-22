# app.py
import logging
import sys
from flask import Flask, render_template, request, redirect, url_for, session
from scraper.scraper import detect_navbar

# ✅ Truncated Formatter to Limit Log Length
class TruncatedFormatter(logging.Formatter):
    def format(self, record):
        max_length = 100  # Set max length for logs
        original_message = super().format(record)
        if len(original_message) > max_length:
            return original_message[:max_length] + "..."  # Truncate and add "..."
        return original_message

# ✅ Remove existing handlers (prevents duplicate logs)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# ✅ Setup global logging with TruncatedFormatter
formatter = TruncatedFormatter("%(asctime)s - [%(levelname)s] - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

# ✅ Apply to root logger
logging.basicConfig(level=logging.INFO, handlers=[handler])  # Set default to INFO

# ✅ Suppress DEBUG logs from third-party libraries
logging.getLogger("selenium").setLevel(logging.WARNING)  # Suppress Selenium debug logs
logging.getLogger("urllib3").setLevel(logging.WARNING)  # Suppress urllib3 debug logs
logging.getLogger("werkzeug").setLevel(logging.WARNING)  # Suppress Flask server debug logs

app = Flask(__name__)
app.secret_key = "your_secret_key"

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
