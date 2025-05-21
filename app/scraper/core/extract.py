# scraper/core/extract.py
import asyncio
import re
from typing import List, Optional, Set, Union

from bs4 import BeautifulSoup, Tag
from playwright.async_api import async_playwright, Error as PlaywrightError # type: ignore

from playwright.async_api import async_playwright # type: ignore


from scraper.core.storage import save_text
from scraper.logging_config import get_logger
from scraper.utils.headers import get_random_headers
from scraper.utils.url_utils import format_url

logger = get_logger(__name__)

async def async_extract_text(url: str, domain: Optional[str] = None) -> Union[str, None]:
    """
    Extract text from a webpage asynchronously using Playwright, save it using unified save_text().
    Returns the extracted text, or an error message.
    """
    logger.info(f"🔍 Extracting text from: {url}")
    url = format_url(url)
    if not domain:
        domain = url.split("//")[-1].split("/")[0]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(extra_http_headers=get_random_headers())
        page = await context.new_page()

        try:
            await page.goto(url, timeout=20000, wait_until="networkidle")
            await asyncio.sleep(2)  # Give time for full render

            page_source = await page.content()
            if not page_source:
                logger.error("❌ No HTML content retrieved.")
                return "Error: No HTML content retrieved."

            extracted_text = parse_page_text(page_source)
            save_text(domain, url, extracted_text)
            return extracted_text

        except PlaywrightError as pe:
            logger.error(f"❌ Playwright error extracting text: {pe}", exc_info=True)
            return f"Error extracting text: {pe}"
        except Exception as e:
            logger.error(f"❌ Error extracting text: {e}", exc_info=True)
            return f"Error extracting text: {e}"
        finally:
            await browser.close()

def parse_page_text(html: str) -> str:
    """
    Clean and parse main page text from HTML with BeautifulSoup.
    Returns cleaned text or an error string.
    """
    if not html:
        logger.error("❌ Received empty HTML content.")
        return "Error: No HTML content received."

    logger.info("🛠️ Parsing page HTML with BeautifulSoup...")
    soup = BeautifulSoup(html, "lxml")

    logger.info("🧹 Removing unnecessary elements...")
    try:
        for tag in soup.find_all(
            [
                "nav",
                "header",
                "footer",
                "aside",
                "script",
                "style",
                "form",
                "button",
                "iframe",
                "noscript",
            ]
        ):
            tag.decompose()
    except Exception as e:
        logger.error(f"❌ Error while removing sections: {e}")

    logger.info("🔎 Extracting meaningful text elements...")
    try:
        main_content = soup.find("div", id="wsite-content") or soup.find(
            "div", class_="wsite-section-content"
        )

        if not (main_content and isinstance(main_content, Tag)):
            logger.warning("⚠️ No identifiable main content found.")
            return "Error: No meaningful text found on the page."

        text_elements = [
            el
            for el in main_content.find_all(
                [
                    "p",
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                    "li",
                    "td",
                    "th",
                    "span",
                    "div",
                ]
            )
            if isinstance(el, Tag)
        ]
        logger.info(f"📄 Found {len(text_elements)} text elements in main content.")

        text_list: List[str] = []
        seen_paragraphs: Set[str] = set()
        prev_line: str = ""

        for el in text_elements:
            extracted_text: str = el.get_text(separator=" ", strip=True)

            if not extracted_text or len(extracted_text) < 5:
                continue

            if any(
                keyword in extracted_text.lower()
                for keyword in ["file size:", "file type:", "download file", "pdf"]
            ):
                continue

            if re.match(r"^\d+\s*kb$", extracted_text.lower()):
                logger.info(f"🚀 Skipping file size reference: {extracted_text}")
                continue

            if extracted_text == prev_line:
                continue
            prev_line = extracted_text

            normalized_text = " ".join(extracted_text.split()).lower()
            if normalized_text in seen_paragraphs:
                continue

            text_list.append(extracted_text)
            seen_paragraphs.add(normalized_text)

        # Post-processing for duplicate blocks and "Contact" at end
        if (
            len(text_list) > 1
            and text_list[0][:30] == text_list[1][:30]
            and abs(len(text_list[0]) - len(text_list[1])) < 20
        ):
            logger.info("🚀 Removing first duplicated block, keeping formatted version.")
            text_list.pop(0)

        if text_list and text_list[-1].strip().lower() == "contact":
            logger.info("🚀 Removing unnecessary 'Contact' at the end.")
            text_list.pop()

        text = "\n\n".join(text_list)

        if not text.strip():
            logger.warning("⚠️ Extracted text is empty.")
            return "Error: Extracted text is empty."

        logger.info(f"✅ Successfully extracted text ({len(text)} characters).")
        return text.strip()

    except Exception as e:
        logger.error(f"❌ Error while extracting text: {e}", exc_info=True)
        return f"Error: Exception encountered while extracting text: {e}"
