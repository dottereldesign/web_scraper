# Web Scraper Project

This is a web scraper built using Flask and Selenium to extract links, text, and files from web pages.

## Features

- Extracts all website links, including file links (.pdf, .doc, .mp4, etc.)
- Extracts visible and non-visible text content
- Simulates hovering over dropdown menus
- Uses Flask for a web interface

## Prerequisites

Ensure you have the following installed:

- Python 3.8 or later
- Firefox browser
- Geckodriver (for Selenium)

### Installing Geckodriver (Ubuntu/Debian)

```sh
sudo apt update
sudo apt install firefox-geckodriver
```

### Installing Geckodriver (MacOS)

```sh
brew install geckodriver
```

## Setup Instructions

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/web_scraper_project.git
cd web_scraper_project
```

### 2. Create a Virtual Environment

```sh
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Run the Application

```sh
FLASK_DEBUG=1 flask run
```

The application will start on `http://127.0.0.1:5000/`

## Project Structure

```
web_scraper_project/
│── scraper/
│   ├── actions.py    # Handles interaction with dropdowns
│   ├── browser.py    # Manages Selenium WebDriver setup
│   ├── extract.py    # Extracts links and text
│   ├── scraper.py    # Main scraping logic
│   ├── utils.py      # Helper functions
│── templates/
│   ├── index.html    # Flask frontend
│── app.py            # Flask server
│── requirements.txt  # Python dependencies
│── README.md         # Project documentation
```

## Troubleshooting

- **If Flask is not found**, activate the virtual environment: `source venv/bin/activate`
- **If Selenium WebDriver is not working**, ensure Geckodriver is installed and accessible in your PATH.
- **If running into permission issues**, try running: `chmod +x venv/bin/activate`

## License

This project is open-source under the MIT License.
