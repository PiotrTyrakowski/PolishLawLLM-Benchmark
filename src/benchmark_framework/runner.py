import time
from pathlib import Path
from tqdm import tqdm
from src.benchmark_framework.managers.base_manager import BaseManager


def rate_limit_wait(requests_per_minute):
    min_delay_between_requests = 60.0 / requests_per_minute + 0.1
    time.sleep(min_delay_between_requests)


class BenchmarkRunner:
    def __init__(self, manager: BaseManager, output_path: Path):
        self.manager = manager
        self.model = manager.model
        self.output_path = output_path

    def _run_iterative(self) -> None:
        runner_config = self.model.get_default_runner_config()

        total_processed = 0
        tasks = self.manager.tasks

        with tqdm(total=len(tasks), desc="Processing tasks", unit="task") as pbar:
            for task in tasks:

                if self.manager.is_task_processed(task, self.output_path):
                    pbar.update(1)
                    continue

                if runner_config.requests_per_minute is not None:
                    rate_limit_wait(runner_config.requests_per_minute)

                system_prompt = self.manager.get_system_prompt(task)

                try:
                    resp = self.model.generate_response(
                        system_prompt,
                        task.get_prompt(),
                    )

                    result = self.manager.get_result(task, resp)
                    self.manager.save_result(task, result, self.output_path)

                    total_processed += 1
                except Exception as e:
                    print(f"\n[ERROR] Failed to process task {task.id}: {e}")

                pbar.update(1)

                if (
                    runner_config.daily_limit is not None
                    and total_processed >= runner_config.daily_limit
                ):
                    print(
                        f"\n[WARNING] Daily limit reached: {total_processed}/{len(tasks)} tasks processed."
                    )
                    break

    def run(self) -> None:
        return self._run_iterative()
