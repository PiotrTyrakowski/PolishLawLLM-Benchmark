import json
from pathlib import Path
from typing import Optional
from benchmark_framework.constants import ENCODING, DATA_PATH
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
            if not line.strip():
                continue
            task_raw = json.loads(line)
            tasks.append(get_task_by_dataset(dataset_name, task_raw))
    return tasks


def initialize_tasks(
    dataset_name: str, tasks_dir_path: Path = DATA_PATH, year: Optional[int] = None
) -> list[Task]:
    """
    Load tasks from a directory (searches recursively for *.jsonl files).
    If year is provided, only loads files located in that year's directory.
    """
    tasks = []
    base_search_path = tasks_dir_path / dataset_name

    if year is not None:
        search_pattern = f"**/{year}/*.jsonl"
    else:
        search_pattern = "**/*.jsonl"

    for file in base_search_path.glob(search_pattern):
        tasks.extend(initialize_tasks_from_jsonl(file, dataset_name))

    return tasks
