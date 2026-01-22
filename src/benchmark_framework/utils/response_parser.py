import json
import re


def strip_markdown_code_blocks(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    return text


def extract_json_field(response_text: str, field_name: str, default: str = "") -> str:
    text = strip_markdown_code_blocks(response_text)

    try:
        json_response = json.loads(text)
        return json_response.get(field_name, default).strip()
    except json.JSONDecodeError:
        pass

    # Fallback: regex to find the field value
    field_match = re.search(rf'"{field_name}"\s*:\s*"([^"]*)"', text, re.DOTALL)
    if field_match:
        return field_match.group(1).strip()

    # Fallback: try to find and parse a JSON object containing the field
    json_match = re.search(rf'\{{.*?"{field_name}".*?\}}', text, re.DOTALL)
    if json_match:
        try:
            json_response = json.loads(json_match.group(0))
            return json_response.get(field_name, default).strip()
        except json.JSONDecodeError:
            pass

    return default
