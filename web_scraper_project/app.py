# app.py
from flask import Flask, render_template, request
from scraper import scrape_website

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    if request.method == "POST":
        url = request.form.get("url")
        data = scrape_website(url)
    
    return render_template("index.html", data=data)

if __name__ == "__main__":
    print("Starting Flask app on http://127.0.0.1:5000/")
    app.run(debug=True)
