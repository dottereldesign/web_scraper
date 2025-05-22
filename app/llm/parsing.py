# app/llm/parsing.py
import re
import json
from typing import Any, Dict

def extract_first_json_block(text: str) -> str:
    start = text.find("{")
    if start == -1:
        return ""
    brace_count = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                return text[start:i+1]
    return ""

def parse_llm_response_content(content: str) -> Dict[str, Any]:
    import re, json
    match = re.search(r"```json\s*(.*?)```", content, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
    else:
        json_str = extract_first_json_block(content)
        if not json_str:
            content_strip = content.strip()
            if content_strip.startswith("{") and content_strip.endswith("}"):
                json_str = content_strip
            else:
                # Do not even try to parse if it doesn't look like JSON
                return {"parse_error": "No valid JSON found", "raw_content": content}
    try:
        return json.loads(json_str)
    except Exception as e:
        return {"parse_error": str(e), "raw_content": content}
