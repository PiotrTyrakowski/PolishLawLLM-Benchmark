import re
from typing import Optional
from pathlib import Path


class LegalBaseExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"File {pdf_path} does not exist")

        self.content = self._extract_text_from_pdf()

    # ----------------------------------
    # PDF processing
    # ----------------------------------
    def _make_char_filter(
        self,
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

    def _find_horizontal_lines(self, page, min_length_ratio=0.6, y_tolerance=2.0):
        """
        Detect horizontal rules on the page.
        Returns list of dicts: { 'x0','x1','y','height','type' } in PDF coords (origin bottom-left).
        min_length_ratio: minimal fraction of page width for a rule.
        """
        candidates = []
        page_w = page.width

        for e in getattr(page, "edges", []) or []:
            # pdfplumber edge dicts sometimes have orientation or x0,x1,y0,y1
            x0, x1 = e.get("x0", 0), e.get("x1", 0)
            y0, y1 = e.get("y0", 0), e.get("y1", 0)
            length = abs(x1 - x0)
            if abs(y1 - y0) <= y_tolerance and length >= page_w * min_length_ratio:
                y = (y0 + y1) / 2.0
                candidates.append(
                    {"x0": x0, "x1": x1, "y": y, "height": abs(y1 - y0), "type": "edge"}
                )

        # sort by y (PDF coords: 0 = bottom). Keep stable ordering
        candidates.sort(key=lambda c: c["y"])
        return candidates

    def _extract_text_from_pdf(self) -> str:
        text_parts = []

        try:
            import pdfplumber

            with pdfplumber.open(self.pdf_path) as pdf:
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

                print(f"Finished loading PDF")

        except Exception as e:
            raise RuntimeError(f"Error while loading PDF: {e}")

        text = "\n".join(text_parts)

        try:
            out_path = self.pdf_path.with_name(self.pdf_path.stem + "_extracted.txt")
            out_path.write_text(text, encoding="utf-8")
            print(f"Saved extracted text to {out_path}")
        except Exception as e:
            print(f"Warning: failed to save extracted text for debugging: {e}")

        return text

    # ----------------------------------
    # Text processing
    # ----------------------------------
    def _format_extracted_text(self, text: str) -> str:
        lines = text.split("\n")
        formatted_lines = []
        for line in lines:
            if not line.strip():
                continue
            else:
                formatted_lines.append(line.strip())

        result_parts = []
        for i, line in enumerate(formatted_lines):
            if line.endswith("-"):
                result_parts.append(line[:-1])
            else:
                result_parts.append(line)
                if i < len(formatted_lines) - 1:
                    result_parts.append(" ")

        result = "".join(result_parts)
        result = re.sub(r"\n+", "\n", result)
        result = re.sub(r" +", " ", result)
        return result.strip()

    def _get_raw_article(self, article_number: int) -> Optional[str]:
        # Pattern for the given article - looks for "Art. X." or "Art. Xa." where X is the number
        # and captures everything up to the next "Art." or the end of the chapter
        pattern = rf"Art\.\s+{article_number}[a-z]?\.\s+.*?(?=(?:Art\.\s+\d+[a-z]?\.|Rozdział\s+[IVXLCDM]+|$))"

        # Search with DOTALL flag (. also matches \n)
        match = re.search(pattern, self.content, re.DOTALL)

        if match:
            return match.group(0)

        return ValueError(f"Article {article_number} not found")

    def get_article(self, article_number: int) -> Optional[str]:
        return self._format_extracted_text(self._get_raw_article(article_number))

    def get_paragraph(
        self, article_number: int, paragraph_number: int
    ) -> Optional[str]:
        article_text = self._get_raw_article(article_number)
        if article_text is None:
            return ValueError(f"Article {article_number} not found")

        # Pattern to match paragraph definitions
        # Paragraphs can appear in two ways:
        # 1. After article header: "Art. X. § Y."
        # 2. Indented with 11 spaces: "           § Y."
        # Captures everything until the next paragraph (always indented with 11 spaces) or end of article
        paragraph_pattern = rf"(?:^ {{11}}|Art\.\s+{article_number}\.\s+)§\s+{paragraph_number}\.\s+(.+?)(?=^ {{11}}§\s+\d+[a-z]?\.|\Z)"

        match = re.search(paragraph_pattern, article_text, re.MULTILINE | re.DOTALL)

        if match:
            paragraph_content = match.group(1)
            return self._format_extracted_text(paragraph_content)

        return ValueError(
            f"Paragraph {paragraph_number} not found in article {article_number}"
        )
