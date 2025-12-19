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

from src.parsers.parsers.legal_base_parser import LegalBaseParser

app = typer.Typer(help="Extract articles from legal PDF documents")
console = Console()


def process_pdf(pdf_path: Path, output_dir: Path) -> bool:
    try:
        output_path = output_dir / f"{pdf_path.stem}.json"
        parser = LegalBaseParser(pdf_path)
        parser.save_all_articles(output_path=output_path)
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
):
    """
    Extract articles from all PDF files in the input directory and save them as JSON files.

    Example:
        python -m parsers.setup_corpuses data/pdfs/2025/legal_base data/corpuses/2025
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = list(input_dir.glob("*.pdf"))

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

            if process_pdf(pdf_path, output_dir):
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
