from abc import ABC, abstractmethod
from typing import List, Generic, TypeVar, Tuple
from pathlib import Path

T = TypeVar("T")


class BaseParser(ABC, Generic[T]):
    """Abstract base parser following Open-Closed Principle."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._validate_file()

    def _validate_file(self) -> None:
        """Validate that file exists."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

    @abstractmethod
    def parse(self) -> List[T]:
        """Parse the file and return domain objects."""
        pass

    @abstractmethod
    def validate(self, item: T) -> Tuple[bool, List[str]]:
        """Validate a single parsed item."""
        pass
