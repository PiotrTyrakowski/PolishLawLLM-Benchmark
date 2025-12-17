import pdfplumber
from typing import List, Optional, Callable
from pathlib import Path


class PdfTableExtractor:
    def extract_text(
        self, pdf_path: Path, start_page: int = 1, min_char_size: float = 9.0
    ) -> str:
        extracted_lines = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[start_page - 1 :]:
                for char in page.chars:
                    if char.get("size", 0) < min_char_size:
                        char["text"] = "SKIP"

                tables = page.extract_tables()

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
                # Replace newlines with spaces to flatten multi-line cells
                cleaned_text = cell.replace("\n", " ").strip()
                if cleaned_text:
                    clean_cells.append(cleaned_text)

        if not clean_cells:
            return None

        # Filter out header rows
        first_cell_lower = clean_cells[0].lower()
        header_keywords = ["nr", "pytania", "odpowiedź", "podstawa", "prawidłowa"]
        if any(keyword in first_cell_lower for keyword in header_keywords):
            return None

        # Ensure row has enough columns (Number, Answer, Legal Basis)
        if len(clean_cells) < 3:
            return None

        return " ".join(clean_cells)
