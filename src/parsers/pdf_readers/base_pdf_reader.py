from abc import ABC, abstractmethod
from pathlib import Path


class BasePdfReader(ABC):
    """Interface for reading text content from PDF files."""

    @abstractmethod
    def read(self, pdf_path: Path, start_page: int = 1) -> str:
        """
        Reads the content of a PDF file and returns it as a string.

        Args:
            pdf_path: Path to the PDF file.
            start_page: The page number to start reading from (1-indexed).

        Returns:
            The extracted text content.
        """
        pass
