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


def initialize_tasks(dataset_name: str, tasks_path: Path = DATA_PATH) -> list[Task]:
    """
    Load tasks from a directory (searches recursively for *.jsonl files).
    """
    tasks = []
    for file in (tasks_path / dataset_name).rglob("*.jsonl"):
        tasks.extend(initialize_tasks_from_jsonl(file, dataset_name))
    return tasks


def extract_answer_from_response(response_text: str) -> str:
    """
    Extract answer from model response that ends with "ANSWER: X" format.
    Returns:
        Single letter answer (A, B, or C) or original text if parsing fails
    """
    response_text = response_text.strip()

    match = re.search(r"ANSWER:\s*([ABC])", response_text, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    # Fallback: look for single letter at the end
    for letter in ["A", "B", "C"]:
        if letter in response_text[-5:]:
            return letter

    # Return full response if parsing fails
    return response_text
