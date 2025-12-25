"""
CLI for uploading exam results to Firebase.

Usage:
    python -m uploaders.cli upload
    python -m uploaders.cli upload --path /custom/path
    python -m uploaders.cli upload --dry-run
    python -m uploaders.cli upload --model bielik
"""

import typer
from pathlib import Path
from typing import Annotated, Optional, Final

from benchmark_framework.constants import DATA_PATH
from uploaders.main import ResultsUploader, discover_models

app = typer.Typer(help="Upload exam results to Firebase")

DEFAULT_PATH: Final[Path] = DATA_PATH / "results_with_metrics" / "exams"
DEFAULT_COLLECTION: Final[str] = "results"


@app.command()
def upload(
    path: Annotated[
        Path,
        typer.Option(
            "--path", "-p",
            help="Path to the directory containing results (default: data/results_with_metrics/exams)"
        ),
    ] = DEFAULT_PATH,
    collection: Annotated[
        str,
        typer.Option(
            "--collection", "-c",
            help="Firestore collection name"
        ),
    ] = DEFAULT_COLLECTION,
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model", "-m",
            help="Upload only a specific model (by ID or name)"
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Preview what would be uploaded without actually uploading"
        ),
    ] = False,
):
    """
    Upload exam results from results_with_metrics to Firebase.
    
    This command reads JSONL files from the results_with_metrics/exams directory,
    aggregates the metrics per exam (year + exam_type), and uploads them to
    Firestore in the format expected by the frontend.
    """
    # Validate path
    if not path.exists():
        typer.echo(f"Error: Directory '{path}' not found", err=True)
        raise typer.Exit(code=1)
    
    if not path.is_dir():
        typer.echo(f"Error: '{path}' is not a directory", err=True)
        raise typer.Exit(code=1)
    
    # Create uploader
    uploader = ResultsUploader(
        source_path=path,
        collection_name=collection,
        dry_run=dry_run,
    )
    
    # Discover models
    models = uploader.discover_models()
    
    if not models:
        typer.echo("No models found in directory")
        raise typer.Exit(code=1)
    
    # Filter by model if specified
    if model:
        filtered = [
            m for m in models
            if model.lower() in m.model_id.lower() or model.lower() in m.model_name.lower()
        ]
        if not filtered:
            typer.echo(f"Error: Model '{model}' not found", err=True)
            typer.echo("\nAvailable models:")
            for m in models:
                typer.echo(f"  - {m.model_name} (id: {m.model_id})")
            raise typer.Exit(code=1)
        models = filtered
    
    # Print header
    typer.echo(f"\n{'=' * 60}")
    typer.echo(f"Uploading exam results to Firebase")
    typer.echo(f"{'=' * 60}")
    typer.echo(f"Source: {path}")
    typer.echo(f"Collection: {collection}")
    typer.echo(f"Models to upload: {len(models)}")
    if dry_run:
        typer.echo("Mode: DRY RUN (no data will be uploaded)")
    typer.echo(f"{'=' * 60}")
    
    # Upload each model
    total_models = 0
    total_exams = 0
    total_questions = 0
    
    for m in models:
        exams, questions = uploader.upload_model(m, verbose=True)
        total_models += 1
        total_exams += exams
        total_questions += questions
    
    # Print summary
    typer.echo(f"\n{'=' * 60}")
    typer.echo(f"Upload {'complete' if not dry_run else 'preview complete'}!")
    typer.echo(f"  Models: {total_models}")
    typer.echo(f"  Exams: {total_exams}")
    typer.echo(f"  Questions processed: {total_questions}")
    typer.echo(f"{'=' * 60}")


@app.command()
def list_models(
    path: Annotated[
        Path,
        typer.Option(
            "--path", "-p",
            help="Path to the directory containing results"
        ),
    ] = DEFAULT_PATH,
):
    """
    List all available models in the results directory.
    """
    if not path.exists():
        typer.echo(f"Error: Directory '{path}' not found", err=True)
        raise typer.Exit(code=1)
    
    models = discover_models(path)
    
    if not models:
        typer.echo("No models found")
        raise typer.Exit(code=1)
    
    typer.echo(f"\nFound {len(models)} model(s):\n")
    
    for m in models:
        typer.echo(f"  {m.model_name}")
        typer.echo(f"    ID: {m.model_id}")
        typer.echo(f"    Path: {m.path}")
        typer.echo(f"    Exam files: {len(m.exam_files)}")
        
        # Group by year
        years = {}
        for ef in m.exam_files:
            if ef.year not in years:
                years[ef.year] = []
            years[ef.year].append(ef.exam_type)
        
        for year in sorted(years.keys()):
            typer.echo(f"      {year}: {', '.join(sorted(years[year]))}")
        typer.echo()


if __name__ == "__main__":
    app()
