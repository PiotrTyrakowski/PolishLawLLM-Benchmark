import re
from typing import Optional
from pathlib import Path


class LegalBaseExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"File {pdf_path} does not exist")

        self.content = self._extract_text_from_pdf()

    def _extract_text_from_pdf(self) -> str:
        text_parts = []

        try:
            import pdfplumber

            with pdfplumber.open(self.pdf_path) as pdf:
                print(f"Loading PDF: {len(pdf.pages)} pages...")

                for i, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
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

    def get_article_formatted(self, article_number: int) -> Optional[str]:
        """Get formatted article text (split into paragraphs)."""
        article = self.get_article(article_number)
        if not article:
            return None

        # Formatting - add blank lines before paragraphs
        formatted = re.sub(r"(§\s+\d+\.)", r"\n\1", article)
        # Remove excessive blank lines
        formatted = re.sub(r"\n{3,}", "\n\n", formatted)

        return formatted.strip()


if __name__ == "__main__":
    # Use with a PDF file
    try:
        # Load code from PDF
        extractor = LegalBaseExtractor("kk.pdf")

        # Get article 6
        print("=== Article 6 (raw) ===")
        article_6 = extractor.get_article(6)
        if article_6:
            print(article_6)
        else:
            print("Article 6 not found")

        print("\n" + "=" * 50 + "\n")

        # Get formatted article 6
        print("=== Article 6 (formatted) ===")
        article_6_formatted = extractor.get_article_formatted(6)
        if article_6_formatted:
            print(article_6_formatted)
        else:
            print("Article 6 not found")

        print("\n" + "=" * 50 + "\n")

        # Example with another article
        print("=== Article 148 (murder) ===")
        article_148 = extractor.get_article_formatted(148)
        if article_148:
            print(article_148)
        else:
            print("Article 148 not found")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except RuntimeError as e:
        print(f"Error: {e}")
