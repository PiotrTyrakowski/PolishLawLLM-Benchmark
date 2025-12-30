import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Set

from src.common.domain.task import Task
from src.benchmark_framework.utils.task_loader import initialize_tasks
from src.benchmark_framework.models.base_model import BaseModel
from src.constants import ENCODING


class BaseManager(ABC):
    """
    Abstract base class for benchmark managers.
    """

    def __init__(
        self,
        model: BaseModel,
        task_type: str,
        tasks_path: Path,
        year: Optional[int] = None,
    ):
        super().__init__()
        self.model = model
        self.task_type = task_type
        self.tasks = initialize_tasks(task_type.lower(), tasks_path, year)

        # Cache to store sets of processed IDs per output file path
        self._processed_cache: Dict[Path, Set[str]] = {}

    @abstractmethod
    def get_result(self, task: Task, model_response: str) -> dict:
        """Generate a result dictionary for a completed task."""
        pass

    @abstractmethod
    def get_output_path(self, task: Task, results_dir: Path) -> Path:
        """
        Determine the specific output file path for a given task.
        """
        pass

    def is_task_processed(self, task: Task, results_dir: Path) -> bool:
        """
        Checks if the task has already been processed by looking into
        the specific output file destined for this task.
        """
        output_path = self.get_output_path(task, results_dir)

        # Lazy load: If we haven't read this specific output file yet, do it now
        if output_path not in self._processed_cache:
            self._processed_cache[output_path] = set()
            if output_path.exists():
                try:
                    with open(output_path, "r", encoding=ENCODING) as f:
                        for line in f:
                            if not line.strip():
                                continue
                            try:
                                data = json.loads(line)
                                if "id" in data:
                                    self._processed_cache[output_path].add(
                                        str(data["id"])
                                    )
                            except json.JSONDecodeError:
                                continue
                except Exception as e:
                    print(
                        f"Warning: Error reading existing results from {output_path}: {e}"
                    )

        return str(task.id) in self._processed_cache[output_path]

    def save_result(self, task: Task, result: dict, results_dir: Path) -> None:
        output_path = self.get_output_path(task, results_dir)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "a", encoding=ENCODING) as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        # Update the cache so subsequent checks know this is done
        if output_path not in self._processed_cache:
            self._processed_cache[output_path] = set()
        self._processed_cache[output_path].add(str(task.id))

    def get_system_prompt(self, year: int) -> str:
        return ""
