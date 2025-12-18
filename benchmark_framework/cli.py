import typer
from typing import Optional

from benchmark_framework.configs.model_config import ModelConfig
from benchmark_framework.runner import BenchmarkRunner
from benchmark_framework.getters.get_manager import get_manager
from benchmark_framework.getters.get_llm_model import get_llm_model

app = typer.Typer(help="CLI for LLM Benchmark Framework")


@app.command()
def run(
    model_name: str = typer.Argument(
        ..., help="Model name (e.g., chatgpt, gemini-2.5-pro, claude, llama)"
    ),
    dataset_name: str = typer.Argument(..., help="Dataset name (e.g., exams)"),
    google_search: bool = typer.Option(
        False,
        "--google-search",
        help="Enable Google Search tool for the model (only applicable for gemini).",
    ),
    year: Optional[int] = typer.Option(
        None,
        "--year",
        "-y",
        help="Specific year of tests to run (e.g. 2012). If not provided, runs all available.",
    ),
):
    model_config = ModelConfig(google_search=google_search)
    model = get_llm_model(model_name, model_config)
    manager = get_manager(dataset_name, model, year=year)

    runner = BenchmarkRunner(manager)
    typer.echo(f"Running benchmark for {model_name} on {len(manager.tasks)} tasks...")
    if year:
        typer.echo(f"Filtering for year: {year}")

    runner.run()


if __name__ == "__main__":
    app()
