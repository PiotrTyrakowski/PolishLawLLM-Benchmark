import typer
import json
from pathlib import Path
from parsers.utils.file_utils import FileOperations

app = typer.Typer()


@app.command()
def calculate_metrics(file_path: Path):
    """
    Reads a JSON line file using FileOperations, calculates accuracy, and averages specific metrics.
    """
    if not file_path.exists():
        typer.secho(f"Error: File '{file_path}' not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    try:
        dataset = FileOperations.load_jsonl(file_path)
    except json.JSONDecodeError:
        typer.secho(
            "Error: Failed to decode JSON. Ensure the file is in valid JSONL format.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"An unexpected error occurred: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    total_count = len(dataset)

    if total_count == 0:
        typer.secho("No data found in file.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    correct_count = 0
    empty_legal_basis_count = 0

    # Accumulators for all items
    sum_exact_match = 0.0
    sum_bleu = 0.0
    sum_weighted_bleu = 0.0

    # Accumulators for correct items only
    sum_bleu_correct = 0.0
    sum_weighted_bleu_correct = 0.0

    for data in dataset:
        is_correct = data.get("is_correct", False)
        if is_correct:
            correct_count += 1

        # Check if extracted_legal_basis_content is empty
        legal_basis_content = data.get("extracted_legal_basis_content", "")
        if not legal_basis_content or legal_basis_content.strip() == "":
            empty_legal_basis_count += 1

        metrics = data.get("metrics", {})
        exact_match = metrics.get("exact_match", 0.0)
        sum_exact_match += exact_match

        current_bleu = 0.0
        current_weighted = 0.0

        for key, value in metrics.items():
            if key.startswith("bleu"):
                current_bleu = value
            elif key.startswith("weighted_bleu"):
                current_weighted = value

        sum_bleu += current_bleu
        sum_weighted_bleu += current_weighted

        if is_correct:
            sum_bleu_correct += current_bleu
            sum_weighted_bleu_correct += current_weighted

    accuracy = correct_count / total_count
    avg_exact_match = sum_exact_match / total_count
    avg_bleu = sum_bleu / total_count
    avg_weighted_bleu = sum_weighted_bleu / total_count

    avg_bleu_on_correct = sum_bleu_correct / correct_count if correct_count > 0 else 0.0
    avg_weighted_on_correct = (
        sum_weighted_bleu_correct / correct_count if correct_count > 0 else 0.0
    )

    typer.secho(
        f"\n--- Results for: {file_path.name} ---", fg=typer.colors.GREEN, bold=True
    )

    print(f"Total items processed: {total_count}")
    print(f"Correct items: {correct_count}")
    print(f"No legal basis returned by the model: {empty_legal_basis_count}")
    print("-" * 40)

    typer.secho(f"Accuracy: {accuracy:.4f} ({accuracy:.2%})", fg=typer.colors.CYAN)
    print(f"Exact Matches count: {sum_exact_match}")
    print(f"Avg BLEU (All): {avg_bleu:.4f}")
    print(f"Avg Weighted BLEU (All): {avg_weighted_bleu:.4f}")
    print("-" * 40)

    typer.secho("Metrics for Correct Answers Only:", bold=True)
    print(f"Avg BLEU (Correct): {avg_bleu_on_correct:.4f}")
    print(f"Avg Weighted BLEU (Correct): {avg_weighted_on_correct:.4f}")
    print("")


if __name__ == "__main__":
    app()
