# Scrapegoat – Website Text and File Scraper

Scrapegoat is a web-based tool that lets you extract text, images, and documents from public websites. The app features a mobile-first, responsive UI and organizes scraped files by type and extension for easy browsing and download.

---

## Features

- **Web-based interface** (Flask, Jinja2)
- **Extracts page text** and saves it locally
- **Downloads images and documents** (PDF, DOCX, TXT, etc.) found on crawled pages
- **Categorizes files** as Images, Documents, and Others with extensions displayed
- **Responsive UI** (desktop, tablet, mobile friendly)
- **Background crawling** with status updates
- **Per-domain storage** for all extracted data

---

## Quickstart

### 1. Clone and Install

```bash
git clone git@github.com:dottereldesign/web_scraper.git
cd scrapegoat/app
python3 -m venv venv
source venv/bin/activate     # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Install Playwrite Browsers

```bash
playwright install
```

## 3. Configure environment

Create a `.env` file in the `app/` directory. Example:

```env
FLASK_SECRET=your_flask_secret
USE_HEADLESS=1
```

## 4. Run the server

flask run --reload

## Usage

1. **Enter a URL** in the input box (e.g. `https://quotes.toscrape.com/`)
2. **Click “Extract”**
3. **Wait for crawl to complete**
   - Progress/status will be displayed.
4. **Extracted text and files** will be shown and categorized on the UI.
5. **Download files** or copy text as needed.

---

## Safe Demo URLs

Try scraping these public demo/test sites:

- [https://quotes.toscrape.com/](https://quotes.toscrape.com/)
- [https://books.toscrape.com/](https://books.toscrape.com/)

> ⚠️ **Do not scrape private or protected websites without permission.**  
> Always check site terms and robots.txt.

## Roadmap

- [ ] **Per-user scrape history**  
       Save and display each user's previous scrape sessions.
- [ ] **Progress polling / AJAX refresh**  
       Use live status updates so users don’t have to refresh manually.
- [ ] **Advanced crawl controls**
  - Set depth/number of pages
  - Blacklist/whitelist URLs
  - Limit crawl to specific domains or subpaths
- [ ] **Multi-domain support**  
       Allow multiple sites to be scraped in parallel or stored separately.
- [ ] **Authentication support**  
       Log in to sites that require authentication before scraping.
- [ ] **Custom User-Agent / Headers**  
       Set or randomize HTTP headers to avoid blocks and simulate real browsers.
- [ ] **Proxy/Rotating IP support**  
       Use proxies to avoid IP bans and geo-restrictions.
- [ ] **Download all as ZIP**  
       Allow users to download all scraped content/files as a single ZIP.
- [ ] **Full-text search on scraped data**  
       Search across all extracted text for keywords.
- [ ] **Export options**  
       Export data as CSV, JSON, PDF, or Markdown.
- [ ] **Scheduled/repeat scraping (cron)**  
       Automatically scrape sites on a schedule and notify on updates.
- [ ] **Mobile-first & responsive UI**  
       Refine mobile and tablet layouts.
- [ ] **Preview scraped images/files in-browser**
- [ ] **Scrape JavaScript-heavy sites (headless browser improvements)**
- [ ] **Custom selectors/extraction rules**  
       Let users target specific elements (like only articles, tables, etc.)
- [ ] **robots.txt and site policy checker**  
       Warn or prevent scraping of disallowed sites.
- [ ] **Detailed scrape logs & error reporting**  
       Let users view what was skipped, errors, redirects, etc.
- [ ] **Admin dashboard**  
       Manage jobs, monitor resource usage, and view analytics.
