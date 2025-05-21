# llm_categorizer.py
import requests
import json
import re
import logging
import os

from typing import Dict, Any



# === Constants ===
PROJECT_TMP_DIR = os.path.join(os.path.dirname(__file__), "tmp")

# Ensure tmp folder exists at startup
os.makedirs(PROJECT_TMP_DIR, exist_ok=True)

print("[DEBUG] RUNNING LLM_CATEGORIZER FROM:", os.path.abspath(__file__))
print("[DEBUG] PROJECT_TMP_DIR:", os.path.abspath(PROJECT_TMP_DIR))


# Import your own logger for consistency
try:
    from scraper.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    # Fallback to std logging if run standalone
    logger = logging.getLogger("llm_categorizer")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

def extract_first_json_block(text: str) -> str:
    """
    Extract the first top-level {...} JSON object from a string,
    skipping any preamble or trailing junk. Handles nested braces.
    """
    start = text.find('{')
    if start == -1:
        return ""
    brace_count = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            brace_count += 1
        elif text[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                return text[start:i+1]
    return ""

def try_write_file(path: str, data: str, is_json: bool = False):
    print(f"[DEBUG] Attempting to write to: {path}")
    try:
        if is_json:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                f.flush()
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)
                f.flush()
        print(f"[DEBUG] Successfully wrote to: {path}")
    except Exception as e:
        print(f"[DEBUG] Failed to write to {path}: {e}")
        fallback = os.path.join(PROJECT_TMP_DIR, os.path.basename(path))
        print(f"[DEBUG] Attempting fallback to: {fallback}")
        try:
            if is_json:
                with open(fallback, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                    f.flush()
            else:
                with open(fallback, "w", encoding="utf-8") as f:
                    f.write(data)
                    f.flush()
            print(f"[DEBUG] Successfully wrote to fallback: {fallback}")
        except Exception as e2:
            print(f"[DEBUG] Failed fallback write to {fallback}: {e2}")

print("[DEBUG] CWD:", os.getcwd())
try_write_file(os.path.join(PROJECT_TMP_DIR, "llm_write_test.txt"), "test123")

def categorize_text_with_llama3(text: str) -> Dict[str, Any]:
    prompt = f"""
Extract ONLY the following two things from the provided website text:

1. The main navigation or menu links.
    - Output these as a JSON array under the key "Quick-links" (in order of appearance).
    - Only include actual navigation/menu items. Exclude buttons, footer, sponsor, or slogan text.

2. The main descriptive text block from the body of the page.
    - This is sometimes called "Main Content", "Introduction", "Intro", "Welcome Message", "Hero Content", "Hero Section", or "Overview".
    - This is typically a paragraph or set of paragraphs that introduces the website or page, welcomes visitors, or summarizes what the page/site is about.
    - Output this under the key "Main text block" as a single string or array of paragraphs.

Your output must be a single JSON object with these two keys: "Quick-links" and "Main text block".
- Do **not** include any extra keys, explanations, or formatting—**only output the JSON object**.
- If either is missing, output an empty array (for "Quick-links") or an empty string (for "Main text block").

Website text:
{text}
"""
    # ... rest of your function ...

    # Log input to file (to project tmp, fallback to current dir)
    logger.info("📝 Full page text sent to LLM (length: %d)", len(text))
    try_write_file(os.path.join(PROJECT_TMP_DIR, "llm_last_input.txt"), text)

    logger.info("🔎 Sending prompt to Llama3:\n%s", prompt[:1500] + ("..." if len(prompt) > 1500 else ""))
    try:
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False   # <---- THIS LINE
            },
            timeout=120,
        )
        logger.info("✅ Llama3 API status code: %s", r.status_code)
        # Write RAW RESPONSE no matter what, before JSON decode
        raw_response_path = os.path.join(PROJECT_TMP_DIR, "llm_last_output_raw_response.txt")
        try_write_file(raw_response_path, r.text)
        print(f"[DEBUG] Raw response written to {raw_response_path}", flush=True)

        if r.status_code != 200:
            logger.error("❌ Llama3 API call failed: %s", r.text)
            return {"MainContent": f"LLM API error: {r.status_code} {r.text}"}
    except Exception as ex:
        logger.exception("❌ Exception while requesting Llama3 API")
        return {"MainContent": f"LLM API exception: {ex}"}

    # Try to decode JSON, but if it fails, bail
    try:
        output = r.json()
    except Exception as e:
        logger.error("❌ JSON decode error for raw response: %s\nRaw text was:\n%s", e, r.text)
        try_write_file(os.path.join(PROJECT_TMP_DIR, "llm_json_decode_error.txt"), str(e))
        return {"MainContent": f"LLM JSON decode error: {e}"}
    # Save the full *raw* Ollama JSON output
    logger.info("📝 Raw API output (truncated):\n%s", json.dumps(output, indent=2)[:1500] + ("..." if len(json.dumps(output)) > 1500 else ""))
    try_write_file(os.path.join(PROJECT_TMP_DIR, "llm_last_output_raw.json"), output, is_json=True)

    # Save the raw .text response as well for debug
    try:
        raw_text = r.text
        try_write_file(os.path.join(PROJECT_TMP_DIR, "llm_last_output_raw_response.txt"), raw_text)
        logger.debug("🪵 Raw LLM response body written to tmp/llm_last_output_raw_response.txt")
    except Exception as e:
        logger.warning("Couldn't write raw response text for LLM: %s", e)

    # Basic extraction from Ollama response
    content = output.get("message", {}).get("content", "").strip()
    logger.info("🧾 Llama3 message content:\n%s", content[:1200] + ("..." if len(content) > 1200 else ""))
    try_write_file(os.path.join(PROJECT_TMP_DIR, "llm_last_output.txt"), content)

    # --- Robust JSON Extraction ---
    # 1. Look for triple-backtick JSON block (cleanest case)
    match = re.search(r"```json\s*(.*?)```", content, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
    else:
        # 2. Extract the first {...} block (handles junk before/after, nested braces)
        json_str = extract_first_json_block(content)
        if not json_str:
            json_str = content.strip()  # fallback, will likely fail to parse

    logger.info("🔢 JSON string extracted for parsing:\n%s", json_str[:1200] + ("..." if len(json_str) > 1200 else ""))

    try:
        data = json.loads(json_str)
        logger.info("✅ Successfully parsed JSON from Llama3 response")
    except Exception as e:
        logger.error("❌ JSON decode error: %s\nRaw string was:\n%s", e, json_str)
        data = {"MainContent": content}

    # --- Ensure all required keys exist, even if empty ---
    expected_keys = ["Quick-links", "MainContent", "Footer", "Sponsors", "Other"]
    for k in expected_keys:
        if k not in data:
            logger.warning("⚠️ Missing key in LLM result: %s. Inserting as empty.", k)
            data[k] = [] if k in ["Quick-links", "Sponsors"] else ""

    logger.info("🎯 Final categorized data keys: %s", list(data.keys()))
    return data
