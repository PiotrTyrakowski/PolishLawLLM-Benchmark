import time
from tqdm import tqdm
from benchmark_framework.managers.base_manager import BaseManager


def rate_limit_wait(requests_per_minute):
    min_delay_between_requests = 60.0 / requests_per_minute + 1
    time.sleep(min_delay_between_requests)


class BenchmarkRunner:
    def __init__(self, manager: BaseManager):
        self.manager = manager
        self.model = manager.get_model()
        self.system_prompt = manager.get_system_prompt()
        self.output_file = f"{self.model.model_name}.jsonl"

    def _run_iterative(self):
        runner_config = self.model.get_default_runner_config()

        total_processed = 0
        tasks = self.manager.get_tasks()
        task_slice = tasks[runner_config.start_index :]

        with tqdm(total=len(task_slice), desc="Processing tasks", unit="task") as pbar:
            for task in task_slice:
                if runner_config.requests_per_minute is not None:
                    rate_limit_wait(runner_config.requests_per_minute)

                resp = self.model.generate_response(
                    self.system_prompt, task.get_prompt()
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

        accuracy = self.manager.get_summary()["accuracy"]
        return accuracy

    def _run_batch(self):
        tasks = self.manager.get_tasks()
        all_prompts = [task.get_prompt() for task in tasks]
        chunk_size = self.model.model_config.chunk_size
        batch_size = self.model.model_config.batch_size

        if chunk_size % batch_size != 0:
            print("WARNING: Chunk size is not divisible by batch size")

        with tqdm(total=len(tasks), desc="Processing tasks", unit="task") as pbar_outer:
            for i in range(0, len(tasks), chunk_size):
                chunk_prompts = all_prompts[i : i + chunk_size]
                chunk_responses = self.model.generate_batch_response(
                    self.system_prompt, chunk_prompts, batch_size
                )

                for j, model_response in enumerate(chunk_responses):
                    idx = i + j
                    result = self.manager.get_result(tasks[idx], model_response)
                    self.manager.append_to_file(self.output_file, result)
                    pbar_outer.update(1)

        accuracy = self.manager.get_summary()["accuracy"]
        return accuracy

    def run(self):
        if self.model.model_config.batch_size is None:
            return self._run_iterative()
        else:
            return self._run_batch()
