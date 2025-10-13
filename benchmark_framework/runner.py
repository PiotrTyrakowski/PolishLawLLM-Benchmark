import time
from datetime import datetime, date
from pathlib import Path
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.types.task import Task
from benchmark_framework.managers.base_manager import BaseManager


class BenchmarkRunner:
    def __init__(self, manager: BaseManager):
        self.manager = manager
        self.model = manager.model
        self.model_name = self.model.get_model_name()
        self.model_tools = self.model.get_model_tools()
        self.start_task_index = 0
        self.output_file = f"{self.model_name}.jsonl"
        if self.model_tools is not None:
            # split model_tools by , and join them with _
            self.output_file = (
                f"{self.model_name}_{'_'.join(self.model_tools.split(','))}.jsonl"
            )
        
    def set_requests_per_minute(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute

    def set_daily_limit(self, daily_limit: int):
        self.daily_limit = daily_limit

    def set_start_from_task_index(self, task_index: int):
        self.start_task_index = task_index

    def _rate_limit_wait(self):
        min_delay_between_requests = 60.0 / self.requests_per_minute + 1
        time.sleep(min_delay_between_requests)


    def run(self):
        correct = 0
        total_processed = 0

        tasks = self.manager.get_tasks()
        
        for task in tasks[self.start_task_index:]:
            if(self.requests_per_minute is not None):
                self._rate_limit_wait()
            
            resp = self.model.generate_response(task.get_prompt())
            result = self.manager.get_result(task, resp, self.model_tools)
            self.manager.append_to_file(self.output_file, result)
            total_processed += 1
            print(f"Processed {total_processed} tasks")
            print(f"Current accuracy: {self.manager.get_summary()['accuracy']:.2%}")

            if self.daily_limit is not None and total_processed >= self.daily_limit:
                break
            
        accuracy = self.manager.get_summary()["accuracy"]
        return accuracy
