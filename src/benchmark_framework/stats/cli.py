from pathlib import Path
import typer
from typing_extensions import Annotated

from src.benchmark_framework.stats.calculate_stats import calculate_stats_for_path
from src.benchmark_framework.stats.calculate_stats import (
    calculate_exam_stats_for_all_models,
)
from src.benchmark_framework.stats.calculate_stats import get_model_aggregated_stats
from src.benchmark_framework.stats.plotting import (
    plot_metric_over_years,
    plot_metric_for_model_parameters,
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
            help="Path to directory containing models subdirectories.",
            exists=True,
            dir_okay=True,
            file_okay=False,
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            "-o",
            help="Directory to save plots.",
        ),
    ] = Path("data/plots2"),
    parameters: Annotated[
        bool,
        typer.Option(
            "--parameters",
            "-p",
        ),
    ] = False,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    if parameters:
        model_stats = get_model_aggregated_stats(input_path)
        plot_metric_for_model_parameters(
            model_stats,
            "accuracy_metrics",
            "answer",
            "Dokładność odpowiedzi vs liczba parametrów modeli",
            output_dir,
        )
        plot_metric_for_model_parameters(
            model_stats,
            "accuracy_metrics",
            "legal_basis",
            "Dokładność oznaczenia przepisu prawnego vs liczba parametrów modeli",
            output_dir,
        )
        plot_metric_for_model_parameters(
            model_stats,
            "text_metrics",
            "exact_match",
            "Dokładność treści przepisu prawnego vs liczba parametrów modeli",
            output_dir,
        )
        plot_metric_for_model_parameters(
            model_stats,
            "text_metrics",
            "rouge_n_f1",
            "ROUGE-N F1 vs liczba parametrów modeli",
            output_dir,
        )
        plot_metric_for_model_parameters(
            model_stats,
            "text_metrics",
            "rouge_w",
            "ROUGE-W F1 vs liczba parametrów modeli",
            output_dir,
        )
        plot_metric_for_model_parameters(
            model_stats,
            "text_metrics",
            "rouge_n_tfidf",
            "Czułość ROUGE-N TF-IDF vs liczba parametrów modeli",
            output_dir,
        )
        return

    try:
        model_stats = calculate_exam_stats_for_all_models(input_path)
        plot_metric_over_years(
            model_stats,
            "accuracy_metrics",
            "answer",
            "Dokładność odpowiedzi - wyniki na przestrzeni lat",
            output_dir,
        )
        plot_metric_over_years(
            model_stats,
            "accuracy_metrics",
            "legal_basis",
            "Dokładność oznaczenia przepisu prawnego - wyniki na przestrzeni lat",
            output_dir,
        )
        plot_metric_over_years(
            model_stats,
            "text_metrics",
            "exact_match",
            "Dokładność treści przepisu prawnego - wyniki na przestrzeni lat",
            output_dir,
        )
        plot_metric_over_years(
            model_stats,
            "text_metrics",
            "rouge_n_f1",
            "ROUGE-N F1 - wyniki na przestrzeni lat",
            output_dir,
        )
        plot_metric_over_years(
            model_stats,
            "text_metrics",
            "rouge_w",
            "ROUGE-W F1 - wyniki na przestrzeni lat",
            output_dir,
        )
        plot_metric_over_years(
            model_stats,
            "text_metrics",
            "rouge_n_tfidf",
            "Czułość ROUGE-N TF-IDF - wyniki na przestrzeni lat",
            output_dir,
        )
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
