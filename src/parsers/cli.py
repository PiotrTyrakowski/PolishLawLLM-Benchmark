from pathlib import Path
import typer
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)

from src.parsers.parsers.getters import get_questions_parser, get_answers_parser
from src.parsers.services.exam_service import ExamService
from src.parsers.services.legal_basis_service import LegalBasisService
from src.parsers.utils.discover_exams import discover_exams
from src.parsers.utils.file_utils import FileOperations

app = typer.Typer()
console = Console()


@app.command()
def parse(
    pdfs_path: Path = typer.Argument(
        ..., help="Path to the directory containing exam PDFs"
    ),
    corpuses_path: Path = typer.Argument(
        ..., help="Path to the corpuses directory containing year subdirectories"
    ),
    output_path: Path = typer.Argument(
        Path("data/tasks/exams"), help="Path to the output directory for JSONL files"
    ),
):
    """
    Parse Polish law exam PDFs into structured JSONL format.

    This command processes exam PDFs from the specified directory,
    extracts legal basis content from pre-generated corpus files,
    and saves the results in JSONL format.

    python -m src.parsers.cli data/pdfs/ data/corpuses/ data/tasks/exams/
    """
    if not pdfs_path.exists():
        console.print(f"[red]Error: Directory '{pdfs_path}' not found[/red]")
        raise typer.Exit(code=1)

    if not corpuses_path.exists():
        console.print(
            f"[red]Error: Corpuses directory '{corpuses_path}' not found[/red]"
        )
        raise typer.Exit(code=1)

    exams = discover_exams(pdfs_path)
    if not exams:
        console.print("[yellow]No exam files found in directory[/yellow]")
        raise typer.Exit(code=1)

    total_exams = sum(len(exam_types) for exam_types in exams.values())
    console.print(
        f"[cyan]Found {total_exams} exam(s) in {len(exams)} year groups[/cyan]"
    )
    console.print(f"[cyan]Output directory: {output_path}[/cyan]\n")

    successful = 0
    failed = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[green]Processing exams...", total=total_exams)

        for year, exam_types in exams.items():
            corpus_year_dir = corpuses_path / year
            if not corpus_year_dir.exists():
                console.print(
                    f"[yellow]Warning: Corpus directory for year {year} not found at '{corpus_year_dir}', skipping all exams for this year[/yellow]"
                )
                # Advance progress for skipped exams
                progress.advance(task, advance=len(exam_types))
                failed += len(exam_types)
                continue

            legal_basis_service = LegalBasisService(corpus_year_dir)

            for exam_type, files in exam_types.items():
                progress.update(
                    task, description=f"[green]Processing: {exam_type} - {year}"
                )

                if "questions" not in files:
                    console.print(
                        f"[yellow]Questions file not found for {exam_type} {year}, skipping[/yellow]"
                    )
                    progress.advance(task)
                    failed += 1
                    continue

                if "answers" not in files:
                    console.print(
                        f"[yellow]Answers file not found for {exam_type} {year}, skipping[/yellow]"
                    )
                    progress.advance(task)
                    failed += 1
                    continue

                try:
                    exam_service = ExamService(
                        question_parser=get_questions_parser(
                            file_path=files["questions"]
                        ),
                        answer_parser=get_answers_parser(file_path=files["answers"]),
                        legal_basis_service=legal_basis_service,
                    )

                    exam = exam_service.process_exam(
                        exam_type=exam_type, year=int(year)
                    )

                    # Save exam
                    output_file = output_path / str(year) / f"{exam.exam_type}.jsonl"
                    FileOperations.save_jsonl(exam.to_jsonl_data(), output_file)

                    console.print(f"{exam_type} {year} ({len(exam.tasks)} tasks)")
                    successful += 1

                except Exception as e:
                    console.print(
                        f"[red]Error processing {exam_type} {year}: {str(e)}[/red]"
                    )
                    failed += 1

                progress.advance(task)

    # Summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  Total exams: {total_exams}")
    console.print(f"  [green]Successful: {successful}[/green]")
    if failed > 0:
        console.print(f"  [red]Failed: {failed}[/red]")


if __name__ == "__main__":
    app()
