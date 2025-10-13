import json
from typing import Dict, List


def save_as_jsonl(data: List[Dict], output_path: str) -> None:
    """
    Save data in JSONL format (one JSON object per line).
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def load_jsonl(file_path: str) -> List[Dict]:
    """
    Load data from JSONL format.
    """
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data
