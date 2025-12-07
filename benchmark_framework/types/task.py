from abc import ABC, abstractmethod


class Task(ABC):
    """
    Abstract base class for benchmark tasks.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_prompt(self) -> str:
        """
        Returns a formatted prompt string for the task.
        """
        pass

    @abstractmethod
    def get_year(self) -> int:
        pass
