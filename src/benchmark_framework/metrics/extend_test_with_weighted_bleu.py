from pathlib import Path
from typing import Optional, List, Dict, Any

import typer
from src.benchmark_framework.metrics.weighted_bleu import WeightedBleuMetric
from src.benchmark_framework.managers.base_manager import BaseManager
from src.parsers.extractors.legal_basis_extractor import LegalBasisExtractor
from src.parsers.utils.file_utils import FileOperations

app = typer.Typer()


@app.command()
def main(
    input_file: Path = typer.Argument(..., help="Path to input JSONL file"),
    corpus_dir: Path = typer.Argument(
        ..., help="Path to directory containing corpus JSON files"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Path to output JSONL file (optional)"
    ),
):
    # Validate input file
    if not input_file.exists():
        typer.echo(f"Error: Input file does not exist: {input_file}", err=True)
        raise typer.Exit(code=1)

    # Validate corpus directory
    if not corpus_dir.exists():
        typer.echo(f"Error: Corpus directory does not exist: {corpus_dir}", err=True)
        raise typer.Exit(code=1)

    if not corpus_dir.is_dir():
        typer.echo(f"Error: Corpus path is not a directory: {corpus_dir}", err=True)
        raise typer.Exit(code=1)

    # Default output path if not provided
    if output_file is None:
        output_file = (
            input_file.parent / f"{input_file.stem}_weighted_bleu_3{input_file.suffix}"
        )

    typer.echo(f"Loading input file: {input_file}")
    try:
        entries = FileOperations.load_jsonl(input_file)
    except Exception as e:
        typer.echo(f"Error loading input file: {e}", err=True)
        raise typer.Exit(code=1)

    weighted_bleu = WeightedBleuMetric(
        ngram_importances=[1, 2, 1], corpuses_dir=corpus_dir
    )

    processed_count = 0
    error_count = 0
    updated_entries: List[Dict[str, Any]] = []

    legal_basis_extractor = LegalBasisExtractor()
    for idx, data in enumerate(entries, start=1):
        try:
            model_response = data.get("model_response", "")
            legal_basis_content = data.get("legal_basis_content", "")
            legal_basis = data.get("legal_basis", "")

            extracted_legal_basis = legal_basis_extractor.parse(legal_basis)
            code_abbr = LegalBasisExtractor.format_code_abbreviation(
                extracted_legal_basis.code
            )
            legal_basis_model = BaseManager.extract_legal_basis_from_response(
                model_response
            )

            try:
                weighted_bleu_score = weighted_bleu(
                    prediction=legal_basis_model,
                    reference=legal_basis_content,
                    code_abbr=code_abbr,
                )
            except Exception as e:
                typer.echo(
                    f"Warning: Error calculating weighted BLEU for entry {idx}: {e}",
                    err=True,
                )
                weighted_bleu_score = 0.0

            if "metrics" not in data or not isinstance(data["metrics"], dict):
                data["metrics"] = {}

            data["metrics"][weighted_bleu.name] = weighted_bleu_score

            updated_entries.append(data)
            processed_count += 1

        except Exception as e:
            typer.echo(f"Error processing entry {idx}: {e}", err=True)
            error_count += 1

    # Save results
    try:
        FileOperations.save_jsonl(updated_entries, output_file)
    except Exception as e:
        typer.echo(f"Error saving output file: {e}", err=True)
        raise typer.Exit(code=1)

    typer.echo("\nProcessing complete!")
    typer.echo(f"Successfully processed: {processed_count} entries")
    typer.echo(f"Errors encountered: {error_count}")
    typer.echo(f"Output saved to: {output_file}")


if __name__ == "__main__":
    app()
