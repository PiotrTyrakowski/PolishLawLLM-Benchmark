from pathlib import Path
import json


def create_temp_jsonl(
    entries: list, tmp_path: Path, filename: str = "test.jsonl"
) -> Path:
    """Helper to create a temporary JSONL file with given entries."""
    file_path = tmp_path / filename
    with open(file_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return file_path
