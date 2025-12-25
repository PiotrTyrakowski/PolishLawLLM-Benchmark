import re


class TextFormatter:
    """Text formatting and cleaning utilities."""

    @staticmethod
    def format_extracted_text(text: str) -> str:
        """Format extracted text by handling hyphens and spacing."""
        lines = text.split("\n")
        result_lines = []

        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line.endswith("-"):
                result_lines.append(stripped_line[:-1])
            else:
                result_lines.append(stripped_line)
                if i < len(lines) - 1:
                    result_lines.append(" ")

        result = "".join(result_lines)
        result = re.sub(r"\n+", "\n", result)
        result = re.sub(r" +", " ", result)
        return result.strip()

    @staticmethod
    def clean_whitespace(text: str) -> str:
        """Clean excessive whitespace from text."""
        return re.sub(r"\s+", " ", text.strip())
