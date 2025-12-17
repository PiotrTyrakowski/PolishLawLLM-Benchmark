import typer
import re
from pathlib import Path
from typing import Dict, List

from parsers.parsers.pdf_question_parser import PDFQuestionParser
from parsers.parsers.pdf_answer_parser import PDFAnswerParser
from parsers.services.exam_service import ExamService
from parsers.services.legal_basis_service import LegalBasisService
from parsers.repositories.jsonl_repository import JSONLRepository
from parsers.utils.exam_file_discovery import ExamFileDiscovery

app = typer.Typer()


@app.command()
def parse(
    pdfs_path: Path = typer.Argument(
        ..., help="Path to the directory containing exam PDFs"
    ),
    corpuses_path: Path = typer.Argument(
        ..., help="Path to the corpuses directory containing year subdirectories"
    ),
):
    """
    Parse Polish law exam PDFs into structured JSONL format.

    This command processes exam PDFs from the specified directory,
    extracts legal basis content from pre-generated corpus files,
    and saves the results in JSONL format.
    """
    if not pdfs_path.exists():
        typer.echo(f"Error: Directory '{pdfs_path}' not found", err=True)
        raise typer.Exit(code=1)

    if not corpuses_path.exists():
        typer.echo(f"Error: Corpuses directory '{corpuses_path}' not found", err=True)
        raise typer.Exit(code=1)

    # Initialize shared services
    repository = JSONLRepository(Path("data/exams"))

    # Discover exam files
    exams = ExamFileDiscovery.discover_exams(pdfs_path)

    if not exams:
        typer.echo("No exam files found in directory")
        raise typer.Exit(code=1)

    # Process each exam
    total_processed = 0
    for year, exam_types in exams.items():
        # Check if corpus exists for this year
        corpus_year_dir = corpuses_path / year
        if not corpus_year_dir.exists():
            typer.echo(
                f"\n⚠ Warning: Corpus directory for year {year} not found at '{corpus_year_dir}', skipping all exams for this year"
            )
            continue

        legal_basis_service = LegalBasisService(corpus_year_dir)

        for exam_type, files in exam_types.items():
            typer.echo(f"\n{'=' * 60}")
            typer.echo(f"Processing: {exam_type} - {year}")
            typer.echo(f"{'=' * 60}")

            # Validate required files
            if "questions" not in files:
                typer.echo("  ⚠ Questions file not found, skipping")
                continue

            if "answers" not in files:
                typer.echo("  ⚠ Answers file not found, skipping")
                continue

            try:
                # Create parsers
                question_parser = PDFQuestionParser(files["questions"])
                answer_parser = PDFAnswerParser(files["answers"])

                exam_service = ExamService(
                    question_parser=question_parser,
                    answer_parser=answer_parser,
                    legal_basis_service=legal_basis_service,
                )

                exam = exam_service.process_exam(exam_type=exam_type, year=int(year))

                # Save exam
                repository.save(exam)

                typer.echo(f"  ✓ Successfully processed {len(exam.tasks)} tasks")
                total_processed += 1

            except Exception as e:
                typer.echo(f"  ✗ Error processing exam: {str(e)}", err=True)
                continue

    # Summary
    typer.echo(f"\n{'=' * 60}")
    typer.echo(f"Processing complete: {total_processed} exam(s) processed")
    typer.echo(f"{'=' * 60}")


if __name__ == "__main__":
    app()
