from pathlib import Path
from typing import Optional, Callable
import pdfplumber
import re


class PdfTextExtractor:
    """Extract text from PDF files with filtering capabilities."""

    def extract_text(
        self, pdf_path: Path, start_page: int = 1, min_char_size: float = 9.0
    ) -> str:
        """
        Extract text from PDF starting from specified page.

        Args:
            pdf_path: Path to PDF file
            start_page: Page number to start extraction (1-indexed)
            min_char_size: Minimum character size to include

        Returns:
            Extracted text
        """
        text_parts = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[start_page - 1 :]:
                filter_fn = self._make_char_filter(min_size=min_char_size)
                filtered_page = page.filter(filter_fn)
                page_text = filtered_page.extract_text(
                    x_tolerance=3, y_tolerance=3, layout=True
                )
                if page_text:
                    text_parts.append(page_text)

        result = "\n".join(text_parts)
        result = self._filter_exam_headers(result)
        return result

    @staticmethod
    def _make_char_filter(min_size: float = 9.0) -> Callable:
        """Create character filter function."""

        def char_filter(char):
            if "size" in char and char["size"] < min_size:
                return False
            return True

        return char_filter

    @staticmethod
    def _filter_exam_headers(text: str) -> str:
        """Filter out any lines containing the exam header text."""
        lines = text.split("\n")
        filtered_lines = [
            line
            for line in lines
            if "EGZAMIN WSTĘPNY DLA KANDYDATÓW" not in line
            and "EGZAMIN KONKURSOWY" not in line
        ]
        return "\n".join(filtered_lines)


class LegalBaseTextExtractor(PdfTextExtractor):
    """Extract text from legal code documents."""

    def extract_text(
        self, pdf_path: Path, start_page: int = 1, min_char_size: float = 9.0
    ) -> str:
        text_parts = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                print(f"Loading PDF: {len(pdf.pages)} pages...")
                for i, page in enumerate(pdf.pages, 1):
                    horizontals = self._find_horizontal_lines(
                        page, min_length_ratio=0.2, y_tolerance=2
                    )
                    page_h = page.height
                    keep_y0 = 0.0  # bottom of region to keep (PDF coords)
                    keep_y1 = page_h  # top of region to keep (PDF coords)

                    if horizontals:
                        bottom_lines = [
                            h for h in horizontals if h["y"] <= page_h * 0.4
                        ]
                        top_lines = [h for h in horizontals if h["y"] >= page_h * 0.6]
                        if bottom_lines:
                            bottom_candidate = min(bottom_lines, key=lambda h: h["y"])
                            keep_y0 = bottom_candidate["y"] + 15  # small padding
                        if top_lines:
                            top_candidate = max(top_lines, key=lambda h: h["y"])
                            keep_y1 = top_candidate["y"] - 15

                    if keep_y1 - keep_y0 < 10:  # too small -> fallback to full page
                        keep_y0 = 0.0
                        keep_y1 = page_h

                    filter_fn = self._make_char_filter(
                        keep_y0=keep_y0, keep_y1=keep_y1, min_size=9.0
                    )
                    filtered_page = page.filter(filter_fn)
                    page_text = filtered_page.extract_text(
                        x_tolerance=3, y_tolerance=3, layout=True
                    )
                    if page_text:
                        text_parts.append(page_text)

        except Exception as e:
            raise RuntimeError(f"Error while loading PDF: {e}")

        full_text = "\n".join(text_parts)
        filtered_text = self._filter_date_lines(full_text)
        return filtered_text

    @staticmethod
    def _filter_date_lines(text: str, indent_threshold: int = 40) -> str:
        """
        Filter out lines with excessive indentation followed by dates.
        """
        lines = text.split("\n")
        filtered_lines = []

        # Pattern to match lines with lots of whitespace and a date (YYYY-MM-DD format)
        date_pattern = re.compile(
            rf"^\s{{{indent_threshold},}}\s*?\d{{4}}-\d{{2}}-\d{{2}}"
        )

        for line in lines:
            if not date_pattern.match(line):
                filtered_lines.append(line)

        return "\n".join(filtered_lines)

    @staticmethod
    def _make_char_filter(
        keep_y0: Optional[float] = None,
        keep_y1: Optional[float] = None,
        min_size: float = 9.0,
    ):
        """
        Return a function usable by page.filter() that:
        - drops chars whose midpoint is outside [keep_y0, keep_y1] (if provided)
        - drops chars smaller than min_size (superscripts)
        """

        def char_filter(char):
            if "size" in char and char["size"] < min_size:
                return False
            if keep_y0 is not None and keep_y1 is not None:
                # compute vertical midpoint of the character box
                y0 = char.get("y0", None)
                y1 = char.get("y1", None)
                if y0 is None or y1 is None:
                    return True
                ymid = (y0 + y1) / 2.0
                if ymid < keep_y0 or ymid > keep_y1:
                    return False
            return True

        return char_filter

    @staticmethod
    def _find_horizontal_lines(page, min_length_ratio=0.6, y_tolerance=2.0):
        """
        Detect horizontal rules on the page.
        Returns list of dicts: { 'x0','x1','y','height','type' } in PDF coords (origin bottom-left).
        min_length_ratio: minimal fraction of page width for a rule.
        """
        candidates = []
        page_w = page.width

        for e in getattr(page, "edges", []) or []:
            x0, x1 = e.get("x0", 0), e.get("x1", 0)
            y0, y1 = e.get("y0", 0), e.get("y1", 0)
            length = abs(x1 - x0)
            if abs(y1 - y0) <= y_tolerance and length >= page_w * min_length_ratio:
                y = (y0 + y1) / 2.0
                candidates.append(
                    {"x0": x0, "x1": x1, "y": y, "height": abs(y1 - y0), "type": "edge"}
                )

        # sort by y
        candidates.sort(key=lambda c: c["y"])
        return candidates
