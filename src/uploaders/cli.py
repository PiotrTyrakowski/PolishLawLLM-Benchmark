import typer
from pathlib import Path
from typing import Annotated, Optional, Final
from firebase.main import firestore_db
from uploaders.main import Uploader

DATA_PATH: Final[Path] = Path(__file__).resolve().parents[2] / "data"
DEFAULT_PATH: Final[Path] = DATA_PATH / "results_with_metrics"
DEFAULT_COLLECTION: Final[str] = "results"

app = typer.Typer(help="Upload results to Firebase")

@app.command()
def upload(
    path: Annotated[
        Path,
        typer.Option(
            "--path",
            "-p",
            help="Path to the directory containing results (default: data/results_with_metrics)",
        ),
    ] = DEFAULT_PATH,
    collection_id: Annotated[
        str,
        typer.Option("--collection", "-c", help="Firestore collection name"),
    ] = DEFAULT_COLLECTION,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Preview what would be uploaded without actually uploading",
        ),
    ] = False,
):
    """
    Upload exam results from results_with_metrics to Firebase.

    This command reads JSONL files from the results_with_metrics/exams directory,
    aggregates the metrics per exam (year + exam_type), and uploads them to
    Firestore in the format expected by the frontend.
    """

    uploader = Uploader(db=firestore_db, path=path, collection_id=collection_id)
    if not dry_run:
        uploader.upload()

if __name__ == "__main__":
    app()
