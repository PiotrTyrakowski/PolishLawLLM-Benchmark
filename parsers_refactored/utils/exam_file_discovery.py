import typer
import re
from pathlib import Path
from typing import Dict


class ExamFileDiscovery:
    """Discover and organize exam PDF files."""

    @staticmethod
    def discover_exams(pdf_dir: Path) -> Dict[str, Dict[str, Dict[str, Path]]]:
        """
        Discover exam files in directory.

        Returns:
            Dict structured as: {year: {exam_type: {file_type: path}}}
        """
        exams = {}
        pdf_files = [f for f in pdf_dir.iterdir() if f.suffix == ".pdf"]

        for pdf_file in pdf_files:
            year_match = re.search(r"\d{4}", pdf_file.name)
            if not year_match:
                typer.echo(f"Warning: No year found in '{pdf_file.name}', skipping.")
                continue

            year = year_match.group(0)
            exam_type = ExamFileDiscovery._determine_exam_type(pdf_file.name)

            if not exam_type:
                typer.echo(
                    f"Warning: Cannot determine exam type for '{pdf_file.name}', skipping."
                )
                continue

            # Initialize nested dicts
            if year not in exams:
                exams[year] = {}
            if exam_type not in exams[year]:
                exams[year][exam_type] = {}

            # Classify file type
            if pdf_file.name.startswith("Zestaw_pytań"):
                exams[year][exam_type]["questions"] = pdf_file
            elif pdf_file.name.startswith("Wykaz_prawidłowych_odpowiedzi"):
                exams[year][exam_type]["answers"] = pdf_file

        return exams

    @staticmethod
    def _determine_exam_type(filename: str) -> str:
        """Determine exam type from filename."""
        filename_lower = filename.lower()

        if "adwokack" in filename_lower or "radcow" in filename_lower:
            return "adwokacki_radcowy"
        elif "komornic" in filename_lower:
            return "komorniczy"
        elif "notarialn" in filename_lower:
            return "notarialny"

        return None
