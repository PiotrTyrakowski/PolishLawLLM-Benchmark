from pathlib import Path

from src.parsers.extractors.base_extractor import BaseExtractor
from src.parsers.pdf_readers.base_pdf_reader import BasePdfReader


class BaseParser:
    def __init__(
        self,
        file_path: Path,
        extractor: BaseExtractor,
        pdf_reader: BasePdfReader,
        start_page: int = 1,
    ):
        self.file_path = file_path
        self.extractor = extractor
        self.pdf_reader = pdf_reader
        self.start_page = start_page
        self._validate_file()

    def _validate_file(self) -> None:
        """Validate that file exists."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

    def parse(self):
        """Parse the file and return domain objects."""
        text = self.pdf_reader.read(self.file_path, start_page=self.start_page)
        return self.extractor.extract(text)
