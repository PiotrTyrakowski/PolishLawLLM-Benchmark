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

from src.parsers.parsers.getters import get_legal_base_parser
from src.common.file_operations import FileOperations
from src.parsers.corpuses.corpuses_config import START_PAGE

app = typer.Typer(help="Extract articles from legal PDF documents")
console = Console()


def get_start_page(pdf_path: Path, year: int) -> int:
    kodeks_name = pdf_path.stem.lower()

    if year in START_PAGE and kodeks_name in START_PAGE[year]:
        return START_PAGE[year][kodeks_name]

    print("WARNING!!! No start page found for kodeks: ", kodeks_name)
    return 1


def process_pdf(pdf_path: Path, output_dir: Path, year: int) -> bool:
    try:
        output_path = output_dir / f"{pdf_path.stem}.json"
        start_page = get_start_page(pdf_path, year)
        parser = get_legal_base_parser(pdf_path, start_page)
        articles = parser.parse()
        FileOperations.save_json(articles, output_path)
        return True
    except Exception as e:
        console.print(f"[red]Error processing {pdf_path.name}: {e}[/red]")
        return False


@app.command()
def extract(
    input_dir: Path = typer.Argument(
        ...,
        help="Directory containing PDF files to process",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output_dir: Path = typer.Argument(
        ...,
        help="Directory where to save extracted articles (JSON files)",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    year: int = typer.Argument(..., help="year"),
):
    """
    Extract articles from all PDF files in the input directory and save them as JSON files.

    Example:
        python -m src.parsers.corpuses.setup_corpuses data/pdfs/2025/legal_base data/corpuses/2025 2025
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = list(input_dir.glob("*.pdf"))

    if not year:
        console.print(f"[yellow]No year specified[/yellow]")
        raise typer.Exit(code=1)

    if not pdf_files:
        console.print(f"[yellow]No PDF files found in {input_dir}[/yellow]")
        raise typer.Exit(code=1)

    console.print(f"[cyan]Found {len(pdf_files)} PDF file(s) in {input_dir}[/cyan]")
    console.print(f"[cyan]Output directory: {output_dir}[/cyan]\n")

    successful = 0
    failed = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[green]Processing PDFs...", total=len(pdf_files))

        for pdf_path in pdf_files:
            progress.update(task, description=f"[green]Processing: {pdf_path.name}")

            if process_pdf(pdf_path, output_dir, year):
                successful += 1
                console.print(f"[green]✓[/green] {pdf_path.name}")
            else:
                failed += 1
                console.print(f"[red]✗[/red] {pdf_path.name}")

            progress.advance(task)

    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  Total files: {len(pdf_files)}")
    console.print(f"  [green]Successful: {successful}[/green]")
    if failed > 0:
        console.print(f"  [red]Failed: {failed}[/red]")

    if failed > 0:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
