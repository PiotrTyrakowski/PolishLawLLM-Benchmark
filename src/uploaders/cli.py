import logging
from pathlib import Path
from typing import Annotated, Final

import typer
from rich.console import Console
from rich.logging import RichHandler

from firebase.main import firestore_db
from uploaders.main import Uploader

DATA_PATH: Final[Path] = Path(__file__).resolve().parents[2] / "data"
DEFAULT_PATH: Final[Path] = DATA_PATH / "results_with_metrics"
DEFAULT_COLLECTION: Final[str] = "results"

app = typer.Typer(help="Upload benchmark results to Firebase")
console = Console()


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True, console=console)],
    )


@app.command()
def upload(
    path: Annotated[
        Path,
        typer.Option(
            "--path",
            "-p",
            help="Path to the results directory",
        ),
    ] = DEFAULT_PATH,
    collection_id: Annotated[
        str,
        typer.Option("--collection", "-c", help="Firestore collection name"),
    ] = DEFAULT_COLLECTION,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable debug logging"),
    ] = False,
) -> None:
    """Upload test results to Firebase."""
    setup_logging(verbose)

    uploader = Uploader(db=firestore_db, path=path, collection_id=collection_id)

    with console.status("[bold green]Uploading to Firestore..."):
        uploader.upload()
    console.print("[green]✓[/] Upload complete")


if __name__ == "__main__":
    app()
