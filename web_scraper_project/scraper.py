# scraper.py
import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract page title
        title = soup.title.string if soup.title else "No title found"

        # Extract all links
        links = [a['href'] for a in soup.find_all('a', href=True)]

        return {"title": title, "links": links}
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
