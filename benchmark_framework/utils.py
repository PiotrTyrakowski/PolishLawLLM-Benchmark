import json
from pathlib import Path

from benchmark_framework.constants import ENCODING
from benchmark_framework.tasks import Task


def initialize_tasks(tasks_path: Path) -> list[Task]:
    """
    Load tasks from a JSONL file.

    Args:
        tasks_path (Path): Path to the JSONL file containing tasks.

    Returns:
        List[Task]: List of tasks loaded from the file.
    """
    if not tasks_path.exists():
        raise FileNotFoundError(f"File {tasks_path} not found.")

    tasks = []
    with open(tasks_path, "r", encoding=ENCODING) as f:
        for line in f:
            task_raw = json.loads(line)
            tasks.append(
                Task(
                    question=task_raw["question"],
                    choices=task_raw["choices"],
                    answer=task_raw["answer"],
                )
            )

    return tasks
