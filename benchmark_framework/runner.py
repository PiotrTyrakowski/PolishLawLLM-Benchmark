import time
from tqdm import tqdm
from benchmark_framework.managers.base_manager import BaseManager


def rate_limit_wait(requests_per_minute):
    min_delay_between_requests = 60.0 / requests_per_minute + 1
    time.sleep(min_delay_between_requests)


class BenchmarkRunner:
    def __init__(self, manager: BaseManager):
        self.manager = manager
        self.model = manager.model
        self.output_file = f"{self.model.model_name}.jsonl"

    def _run_iterative(self):
        runner_config = self.model.get_default_runner_config()

        total_processed = 0
        tasks = self.manager.tasks
        task_slice = tasks[runner_config.start_index :]

        with tqdm(total=len(task_slice), desc="Processing tasks", unit="task") as pbar:
            for task in task_slice:
                if runner_config.requests_per_minute is not None:
                    rate_limit_wait(runner_config.requests_per_minute)

                resp = self.model.generate_response(
                    self.manager.get_system_prompt(year=task.get_year()),
                    task.get_prompt(),
                )
                result = self.manager.get_result(task, resp)
                self.manager.append_to_file(self.output_file, result)
                total_processed += 1
                pbar.update(1)

                if (
                    runner_config.daily_limit is not None
                    and total_processed >= runner_config.daily_limit
                ):
                    break
        return

    def run(self):
        return self._run_iterative()
