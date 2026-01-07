from pathlib import Path
import typer
from typing_extensions import Annotated

from src.benchmark_framework.stats.calculate_stats import calculate_stats_for_path
from src.benchmark_framework.stats.plotting import (
    plot_accuracy_over_years,
    plot_text_metrics_over_years,
)
from src.benchmark_framework.stats.utils import print_stats

app = typer.Typer(
    help="Calculate statistics and create plots from benchmark results.",
    no_args_is_help=True,
)


@app.command()
def stats(
    file_path: Annotated[
        Path,
        typer.Argument(
            help="Path to the JSONL file or directory containing benchmark results.",
            exists=True,
        ),
    ],
):
    """
    Calculate and display statistics for a file or directory.
    """
    try:
        results = calculate_stats_for_path(file_path)
        print_stats(results)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def plot(
    input_path: Annotated[
        Path,
        typer.Argument(
            help="Path to directory containing year subdirectories.",
            exists=True,
            dir_okay=True,
            file_okay=False,
        ),
    ],
    model_name: Annotated[
        str,
        typer.Argument(
            help="Name of the model for plot title.",
        ),
    ],
    accuracy: Annotated[
        bool,
        typer.Option(
            "--accuracy",
            "-a",
            help="Plot accuracy metrics over years.",
        ),
    ] = False,
    text_metrics: Annotated[
        bool,
        typer.Option(
            "--text-metrics",
            "-t",
            help="Plot text metrics over years.",
        ),
    ] = False,
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            "-o",
            help="Directory to save plots.",
        ),
    ] = Path("data/plots"),
):
    """
    Create plots of metrics over years. If no flags are specified, both accuracy and text metrics plots will be generated.
    """
    if model_name is None:
        typer.secho(f"Model name is required", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    # If neither flag is set, plot both
    if not accuracy and not text_metrics:
        accuracy = True
        text_metrics = True

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        if accuracy:
            plot_accuracy_over_years(input_path, model_name, output_dir)
            typer.secho("Accuracy plot generated successfully!", fg=typer.colors.GREEN)

        if text_metrics:
            plot_text_metrics_over_years(input_path, model_name, output_dir)
            typer.secho(
                "Text metrics plot generated successfully!", fg=typer.colors.GREEN
            )
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
