import json
from pathlib import Path
from typing import List, Dict, Any


class FileOperations:
    """File I/O operations."""

    @staticmethod
    def save_jsonl(data: List[Dict[str, Any]], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    @staticmethod
    def load_jsonl(file_path: Path) -> List[Dict[str, Any]]:
        data = []
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data

    @staticmethod
    def save_json(data: Dict[str, Any], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
