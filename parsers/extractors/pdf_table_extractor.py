import pdfplumber
from typing import List, Optional, Callable
from pathlib import Path


class PdfTableExtractor:
    def extract_text(
        self, pdf_path: Path, start_page: int = 1, min_char_size: float = 8.0
    ) -> str:
        extracted_lines = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[start_page - 1 :]:
                filter_fn = self._make_char_filter(min_size=min_char_size)
                filtered_page = page.filter(filter_fn)
                tables = filtered_page.extract_tables()

                for table in tables:
                    for row in table:
                        line = self._process_row(row)
                        if line:
                            extracted_lines.append(line)

        return "\n".join(extracted_lines)

    def _process_row(self, row: List[Optional[str]]) -> Optional[str]:
        clean_cells = []
        for cell in row:
            if cell:
                cleaned_text = cell.replace("\n", " ").strip()
                if cleaned_text:
                    clean_cells.append(cleaned_text)

        if not clean_cells:
            return None

        # If the first cell contains header keywords like "nr" or "pytania", skip it.
        first_cell_lower = clean_cells[0].lower()
        header_keywords = ["nr", "pytania", "odpowiedź", "podstawa", "prawidłowa"]
        if any(keyword in first_cell_lower for keyword in header_keywords):
            return None

        if len(clean_cells) < 3:
            return None

        return " ".join(clean_cells)

    @staticmethod
    def _make_char_filter(min_size: float = 8.0) -> Callable:
        def char_filter(obj):
            if obj.get("object_type") == "char":
                if "size" in obj and obj["size"] < min_size:
                    return False
            return True

        return char_filter
