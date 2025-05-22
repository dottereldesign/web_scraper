# app/llm/categorizer.py
import os
import logging
from typing import Dict, Any  # Add this if not already
from .prompt_templates import navigation_and_main_text_prompt
from .parsing import parse_llm_response_content
from .api import call_llama3
from .utils import try_write_file, PROJECT_TMP_DIR
from typing import TypedDict, List

# Optionally use your existing logger setup
try:
    from scraper.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger("llm_categorizer")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

def categorize_text_with_llama3(page_text: str) -> Dict[str, Any]:
    prompt = navigation_and_main_text_prompt(page_text)
    logger.info("📝 Full page text sent to LLM (length: %d)", len(page_text))
    try_write_file(os.path.join(PROJECT_TMP_DIR, "llm_last_input.txt"), page_text)
    logger.info("🔎 Sending prompt to Llama3:\n%s", prompt[:1500] + ("..." if len(prompt) > 1500 else ""))

    output, error = call_llama3(prompt, logger)
    if not output:
        return {"error": error}

    content = output.get("message", {}).get("content", "").strip()
    try_write_file(os.path.join(PROJECT_TMP_DIR, "llm_last_output.txt"), content)
    data = parse_llm_response_content(content)

    # Always ensure both keys exist for stability
    if "Quick-links" not in data:
        data["Quick-links"] = []
    if "Main text block" not in data:
        data["Main text block"] = ""
    return data
