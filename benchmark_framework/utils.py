import json
from pathlib import Path
import re
from benchmark_framework.constants import ENCODING, DATA_PATH, RESULTS_PATH
from benchmark_framework.types.task import Task
from benchmark_framework.getters.get_type import get_task_by_dataset


def initialize_tasks_from_jsonl(tasks_path: Path, dataset_name: str) -> list[Task]:
    """
    Load tasks from a JSONL file.
    """
    if not tasks_path.exists():
        raise FileNotFoundError(f"File {tasks_path} not found.")
    tasks = []
    with open(tasks_path, "r", encoding=ENCODING) as f:
        for line in f:
            task_raw = json.loads(line)
            tasks.append(get_task_by_dataset(dataset_name, task_raw))
    return tasks


def initialize_tasks(dataset_name: str, tasks_dir_path: Path = DATA_PATH) -> list[Task]:
    """
    Load tasks from a directory (searches recursively for *.jsonl files).
    """
    tasks = []
    for file in (tasks_dir_path / dataset_name).rglob("*.jsonl"):
        tasks.extend(initialize_tasks_from_jsonl(file, dataset_name))
    return tasks


def extract_answer_from_response(response_text: str) -> str:
    """
    Extract answer from model response in JSON format.
    """
    response_text = response_text.strip()
    answer = ""
    try:
        # Try to parse as JSON
        json_response = json.loads(response_text)
        answer = json_response.get("answer", "").strip().upper()
    except json.JSONDecodeError:
        # Try to find JSON object directly in text
        json_match = re.search(r'\{.*?"answer".*?\}', response_text, re.DOTALL)
        if json_match:
            try:
                json_response = json.loads(json_match.group(0))
                answer = json_response.get("answer", "").strip().upper()
            except json.JSONDecodeError:
                pass

    if answer in ["A", "B", "C"]:
        return answer

    return ""
