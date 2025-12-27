import typer
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm

from src.benchmark_framework.metrics.base_metric import BaseMetric
from src.benchmark_framework.metrics.exact_match import ExactMatchMetric
from src.benchmark_framework.metrics.rouge_n import RougeNMetric
from src.benchmark_framework.metrics.tfidf_rouge_n import TFIDFRougeNMetric
from src.benchmark_framework.metrics.rouge_w import RougeWMetric
from src.parsers.utils.file_utils import FileOperations
from src.parsers.extractors.legal_basis_extractor import LegalBasisExtractor

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
        model_answer = entry["model_answer"]
        correct_answer = entry["correct_answer"]
        exact_match = ExactMatchMetric()
        accuracy_metrics["answer"] = exact_match(model_answer, correct_answer)

    if "legal_basis" in entry and "model_legal_basis" in entry:
        model_legal_basis = entry["model_legal_basis"]
        legal_basis = entry["legal_basis"]
        exact_match = ExactMatchMetric()
        accuracy_metrics["legal_basis"] = exact_match(model_legal_basis, legal_basis)

    metrics: List[BaseMetric] = [
        ExactMatchMetric(),
        RougeNMetric(ngrams_importances=[1, 1, 1]),
        TFIDFRougeNMetric(corpuses_dir=corpuses_path, ngrams_importances=[1, 1, 1]),
        RougeWMetric(alpha=1.2, beta=1.0),
    ]

    text_metrics = {}
    if (
        "model_legal_basis_content" in entry
        and "legal_basis_content" in entry
        and "legal_basis" in entry
    ):
        model_text = entry["model_legal_basis_content"]
        reference_text = entry["legal_basis_content"]
        legal_basis = entry["legal_basis"]
        legal_basis_extractor = LegalBasisExtractor()
        legal_basis_reference = legal_basis_extractor.parse(legal_basis)
        code_abbr = LegalBasisExtractor.format_code_abbreviation(
            legal_basis_reference.code
        )

        for metric in metrics:
            text_metrics[metric.name] = metric(model_text, reference_text, code_abbr)

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

        entries = FileOperations.load_jsonl(jsonl_file)

        if not entries:
            typer.secho(
                f"  Warning: No entries found in '{relative_path}'",
                fg=typer.colors.YELLOW,
            )
            continue

        processed_entries = [
            process_entry(entry, Path(corpuses_dir) / str(entry.get("year", "")))
            for entry in tqdm(entries, desc=str(relative_path), unit="entries")
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
