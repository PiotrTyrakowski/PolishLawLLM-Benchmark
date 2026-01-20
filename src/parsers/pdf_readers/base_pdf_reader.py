from abc import ABC, abstractmethod
from pathlib import Path


class BasePdfReader(ABC):
    """Interface for reading text content from PDF files."""

    @abstractmethod
    def read(self, pdf_path: Path, start_page: int = 1) -> str:
        pass
