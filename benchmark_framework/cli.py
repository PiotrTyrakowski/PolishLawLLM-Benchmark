from pathlib import Path
import typer

from benchmark_framework.runner import BenchmarkRunner
from benchmark_framework.get_model import get_model_by_name
from benchmark_framework.utils import initialize_tasks

app = typer.Typer(help="CLI for LLM Benchmark Framework")


@app.command()
def run(
    tasks_path: Path = typer.Argument(..., help="Path to JSONL file with tasks"),
    model_name: str = typer.Argument(
        ..., help="Model name (e.g., chatgpt, claude, llama)"
    )
):
    """
    Run the benchmark on a given model and questions dataset.
    """
    tasks = initialize_tasks(tasks_path)
    model = get_model_by_name(model_name)
    runner = BenchmarkRunner(model, tasks)

    # Run benchmark
    typer.echo(f"Running benchmark for {model_name} on {len(tasks)} tasks...")
    accuracy = runner.run()

    typer.echo(f"Accuracy: {accuracy:.2%}")


if __name__ == "__main__":
    app()
