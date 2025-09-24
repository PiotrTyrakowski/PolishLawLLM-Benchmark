import json
from pathlib import Path
import re
from benchmark_framework.constants import ENCODING
from benchmark_framework.types.task import Task
from benchmark_framework.types.exam import Exam
from benchmark_framework.getters.get_type import get_task_by_dataset


def initialize_tasks_from_jsonl(tasks_path: Path, dataset_name: str) -> list[Task]:
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
            tasks.append(get_task_by_dataset(dataset_name, task_raw))
    return tasks


def initialize_tasks(tasks_dir_path: Path, dataset_name: str) -> list[Task]:
    """
    Load tasks from a directory (searches recursively for *.jsonl files).
    """
    tasks = []
    
    for file in (tasks_dir_path / dataset_name).rglob("*.jsonl"):
        tasks.extend(initialize_tasks_from_jsonl(file, dataset_name))
    return tasks

def extract_answer_from_response(response_text: str) -> str:
        """
        Extract answer from model response that ends with "ANSWER: X" format.
        
        Args:
            response_text: Full response text from the model
            
        Returns:
            Single letter answer (A, B, or C) or original text if parsing fails
        """
        response_text = response_text.strip()
        
        # Look for "ANSWER: " followed by A, B, or C
        match = re.search(r'ANSWER:\s*([ABC])', response_text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        
        # Fallback: look for single letter at the end
        for letter in ['A', 'B', 'C']:
            if letter in response_text[-5:]:  # Check last 5 characters
                return letter
        
        # Return full response if parsing fails
        return response_text
