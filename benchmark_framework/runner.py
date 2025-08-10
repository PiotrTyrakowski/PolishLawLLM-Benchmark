from benchmark_framework.models.base import BaseModel
from benchmark_framework.tasks import Task


class BenchmarkRunner:
    def __init__(self, model: BaseModel, tasks: list[Task]):
        self.model = model
        self.tasks = tasks

    def run(self):
        correct = 0
        for task in self.tasks:
            resp = self.model.generate_answer(task.question, task.choices)
            if resp.strip().startswith(task.answer):
                correct += 1
        accuracy = correct / len(self.tasks)
        return accuracy
