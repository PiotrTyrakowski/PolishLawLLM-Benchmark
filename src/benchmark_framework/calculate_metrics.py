import typer
from pathlib import Path
from typing import List, Dict, Any

from src.benchmark_framework.metrics.exact_match import ExactMatchMetric
from src.benchmark_framework.metrics.weighted_bleu import WeightedBleuMetric
from src.parsers.utils.file_utils import FileOperations

app = typer.Typer(help="CLI for calculating metrics on benchmark results")


def find_jsonl_files(directory: Path) -> List[Path]:
    """Recursively find all .jsonl files in a directory."""
    return list(directory.rglob("*.jsonl"))


def process_entry(entry: Dict[str, Any], corpuses_path: Path) -> Dict[str, Any]:
    """
    Process a single entry and calculate metrics.
    """
    accuracy_metrics = {}
    if "model_answer" in entry and "correct_answer" in entry:
        model_answer = entry["model_answer"].strip().lower()
        correct_answer = entry["correct_answer"].strip().lower()
        exact_match = ExactMatchMetric()
        accuracy_metrics["answer"] = exact_match(model_answer, correct_answer)

    text_metrics = {}
    if "model_legal_basis_content" in entry and "legal_basis_content" in entry:
        model_text = entry["model_legal_basis_content"]
        reference_text = entry["legal_basis_content"]

        exact_match = ExactMatchMetric()
        text_metrics["exact_match"] = exact_match(model_text, reference_text)

        bleu_metric = WeightedBleuMetric()
        text_metrics["bleu"] = bleu_metric(
            prediction=model_text, reference=reference_text
        )

        weighted_bleu_metric = WeightedBleuMetric(
            ngram_importances=[1, 2, 1], corpuses_dir=corpuses_path
        )
        text_metrics["weighted_bleu"] = weighted_bleu_metric(
            prediction=model_text, reference=reference_text
        )

    entry["accuracy_metrics"] = accuracy_metrics
    entry["text_metrics"] = text_metrics
    entry.pop("model_response", None)
    return entry


@app.command()
def calculate_metrics(
    input_dir: Path = typer.Argument(
        ..., help="Path to the results directory containing JSONL files"
    ),
    output_dir: Path = typer.Argument(
        ..., help="Path to the output directory for processed files"
    ),
    corpuses_dir: Path = typer.Argument(
        "data/corpuses", help="Path to the directory containing corpuses"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files in the output directory",
    ),
) -> None:
    if not input_dir.exists():
        typer.secho(
            f"Error: Input directory '{input_dir}' does not exist.", fg=typer.colors.RED
        )
        raise typer.Exit(code=1)

    if not input_dir.is_dir():
        typer.secho(f"Error: '{input_dir}' is not a directory.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    jsonl_files = find_jsonl_files(input_dir)

    if not jsonl_files:
        typer.secho(f"No JSONL files found in '{input_dir}'.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    typer.echo(f"Found {len(jsonl_files)} JSONL file(s) in '{input_dir}'")

    processed_count = 0
    skipped_count = 0

    for jsonl_file in jsonl_files:
        relative_path = jsonl_file.relative_to(input_dir)
        output_path = output_dir / relative_path

        if output_path.exists() and not force:
            typer.secho(
                f"Skipping '{relative_path}': output file already exists (use --force to overwrite)",
                fg=typer.colors.YELLOW,
            )
            skipped_count += 1
            continue

        typer.echo(f"Processing: {relative_path}")
        entries = FileOperations.load_jsonl(jsonl_file)

        if not entries:
            typer.secho(
                f"  Warning: No entries found in '{relative_path}'",
                fg=typer.colors.YELLOW,
            )
            continue

        processed_entries = [
            process_entry(entry, Path(corpuses_dir)) for entry in entries
        ]

        FileOperations.save_jsonl(processed_entries, output_path)
        processed_count += 1

    typer.echo("")
    typer.secho(
        f"Done! Processed {processed_count} file(s), skipped {skipped_count} file(s).",
        fg=typer.colors.GREEN,
        bold=True,
    )


if __name__ == "__main__":
    app()
