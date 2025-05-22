# app/llm/utils.py
import os
import json

PROJECT_TMP_DIR = os.path.join(os.path.dirname(__file__), "..", "tmp")

def try_write_file(path: str, data, is_json: bool = False):
    try:
        if is_json:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)
    except Exception as e:
        print(f"[DEBUG] Failed to write to {path}: {e}")
