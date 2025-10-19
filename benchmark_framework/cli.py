import typer

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
):
    """
    Run the benchmark on a given model and questions dataset.
    """
    model_config = ModelConfig(google_search=google_search)
    model = get_llm_model(model_name, model_config)
    manager = get_manager(dataset_name, model)
    runner = BenchmarkRunner(manager)

    typer.echo(
        f"Running benchmark for {model_name} on {len(manager.get_tasks())} tasks..."
    )
    accuracy = runner.run()

    typer.echo(f"Accuracy: {accuracy:.2%}")


if __name__ == "__main__":
    app()
