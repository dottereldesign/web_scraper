# app/llm/prompt_templates.py

def navigation_and_main_text_prompt(page_text: str) -> str:
    return f"""
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
{page_text}
"""
