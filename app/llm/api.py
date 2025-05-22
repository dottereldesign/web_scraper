# app/llm/api.py
import os
import requests
from .utils import try_write_file, PROJECT_TMP_DIR

def call_llama3(prompt: str, logger):
    try:
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=120,
        )
        try_write_file(os.path.join(PROJECT_TMP_DIR, "llm_last_output_raw_response.txt"), r.text)
        logger.info("✅ Llama3 API status code: %s", r.status_code)
        if r.status_code != 200:
            logger.error("❌ Llama3 API call failed: %s", r.text)
            return None, r.text
        return r.json(), None
    except Exception as ex:
        logger.exception("❌ Exception while requesting Llama3 API")
        return None, str(ex)
