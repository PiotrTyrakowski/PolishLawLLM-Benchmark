import json

from benchmark_framework.constants import ENCODING


class Task:
    def __init__(self, question, choices, answer):
        self.question, self.choices, self.answer = question, choices, answer

def load_tasks(jsonl_path):
    tasks = []
    with open(jsonl_path, encoding=ENCODING) as f:
        for line in f:
            obj = json.loads(line)
            tasks.append(Task(obj["question"], obj["choices"], obj["answer"]))
    return tasks
