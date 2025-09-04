from abc import ABC, abstractmethod
from typing import List, Optional


class Task(ABC):
    def __init__(self):
        super().__init__()

 
    @abstractmethod
    def get_prompt(self) -> str:
        """
        Get the prompt for the task.
        """
        pass