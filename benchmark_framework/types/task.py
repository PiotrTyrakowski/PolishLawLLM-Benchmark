from abc import ABC, abstractmethod
from typing import List, Optional


class Task(ABC):
    """
    Abstract base class for benchmark tasks.
    """
    def __init__(self):
        super().__init__()

 
    @abstractmethod
    def get_prompt(self) -> str:
        """
        Generate a formatted prompt string for the task.

        Returns:
            str: A complete prompt that can be sent to a language model for evaluation.
        """
        pass