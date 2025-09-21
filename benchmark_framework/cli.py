import typer
from benchmark_framework.runner import BenchmarkRunner
from benchmark_framework.getters.get_model import get_model_by_name
from benchmark_framework.getters.get_manager import get_manager_by_dataset

app = typer.Typer(help="CLI for LLM Benchmark Framework")


@app.command()
def run(
    model_name: str = typer.Argument(
        ..., help="Model name (e.g., chatgpt, claude, llama)"
    ),
    dataset_name: str = typer.Argument(
        ..., help="Dataset name (e.g., exams)"
    )
):
    """
    Run the benchmark on a given model and questions dataset.
    """
    model = get_model_by_name(model_name)
    manager = get_manager_by_dataset(dataset_name, model_name)
    runner = BenchmarkRunner(model, manager)

    # TODO: remove this
    # settings to use gemini for free https://ai.google.dev/gemini-api/docs/rate-limits
    runner.set_requests_per_minute(5) 
    runner.set_daily_limit(100)
    runner.set_start_from_task_index(0)

    typer.echo(f"Running benchmark for {model_name} on {len(manager.get_tasks())} tasks...")
    accuracy = runner.run()

    typer.echo(f"Accuracy: {accuracy:.2%}")

if __name__ == "__main__":
    app()
