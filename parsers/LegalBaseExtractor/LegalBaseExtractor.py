import re
from typing import Optional
from pathlib import Path


class LegalBaseExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"File {pdf_path} does not exist")

        self.content = self._extract_text_from_pdf()

    def _filter_superscripts(self, char):
        """Filter function to exclude superscripts based on character size."""
        # Filter out characters with size smaller than normal text (typically superscripts)
        # Normal text is 9-12pt, superscripts are 6.5-8pt
        if "size" in char:
            return char["size"] >= 9.0  # Filter out anything smaller than 9pt
        return True

    def _extract_text_from_pdf(self) -> str:
        text_parts = []

        try:
            import pdfplumber

            with pdfplumber.open(self.pdf_path) as pdf:
                print(f"Loading PDF: {len(pdf.pages)} pages...")

                for i, page in enumerate(pdf.pages, 1):
                    filtered_page = page.filter(self._filter_superscripts)
                    page_text = filtered_page.extract_text(x_tolerance=3, y_tolerance=3)
                    if page_text:
                        text_parts.append(page_text)

                print(f"Finished loading PDF")

        except Exception as e:
            raise RuntimeError(f"Error while loading PDF: {e}")

        text_with_markers = [
            f"PAGE:\n{self._clear_page_markers(page_text)}" for page_text in text_parts
        ]
        text = "\n".join(text_with_markers)

        try:
            out_path = self.pdf_path.with_name(self.pdf_path.stem + "_extracted.txt")
            out_path.write_text(text, encoding="utf-8")
            print(f"Saved extracted text to {out_path}")
        except Exception as e:
            print(f"Warning: failed to save extracted text for debugging: {e}")

        return text

    def _clear_page_markers(self, page_text: str) -> str:
        """Remove first and last line from a single page's text."""
        lines = page_text.split("\n")

        if len(lines) > 2:
            cleaned_lines = lines[1:-1]
            return "\n".join(cleaned_lines)

        return ""

    def get_article(self, article_number: int) -> Optional[str]:
        # Pattern for the given article - looks for "Art. X." where X is the number
        # and captures everything up to the next "Art." or the end of the chapter
        pattern = rf"Art\.\s+{article_number}\.\s+.*?(?=(?:Art\.\s+\d+\.|Rozdział\s+[IVXLCDM]+|$))"

        # Search with DOTALL flag (. also matches \n)
        match = re.search(pattern, self.content, re.DOTALL)

        if match:
            article_text = match.group(0)
            # Clean up excessive whitespace
            article_text = re.sub(r"\n+", "\n", article_text)
            article_text = re.sub(r" +", " ", article_text)
            return article_text.strip()

        return None
