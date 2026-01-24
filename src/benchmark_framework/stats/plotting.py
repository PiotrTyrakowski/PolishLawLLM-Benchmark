from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from src.benchmark_framework.stats.config import MODEL_CONFIG


def plot_metric_for_model_parameters(
    models_metrics: dict,
    metric_parent: str,
    metric_name: str,
    title: str,
    output_dir: Path,
):
    data = []
    special_model = "gpt-5.2"
    special_model_score = None

    for model_name, metrics in models_metrics.items():
        if model_name == special_model:
            special_model_score = metrics[metric_parent][metric_name]
            continue

        if model_name in MODEL_CONFIG:
            model_config = MODEL_CONFIG[model_name]
            marker_style = f"${model_config.shortcut}$"
            data.append(
                {
                    "Model": model_name,
                    "Metric": metrics[metric_parent][metric_name],
                    "Parameters": model_config.parameters,
                    "Marker": marker_style,
                }
            )

    df = pd.DataFrame(data)
    fig, ax = plt.subplots(figsize=(10, 6))

    for marker, group in df.groupby("Marker"):
        label_text = group["Model"].iloc[0]
        ax.scatter(
            group["Parameters"],
            group["Metric"],
            marker=marker,
            s=150,
            label=label_text,
            alpha=0.8,
        )

    if special_model_score is not None:
        ax.axhline(
            y=special_model_score,
            color="red",
            linestyle="--",
            linewidth=1.5,
            label=special_model,
            alpha=0.8
        )

    ax.set_title(title, fontsize=14, pad=20)
    ax.set_xlabel("Liczba parametrów (w miliardach)")
    ax.set_ylabel("Wartość metryki")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())

    ax.legend(
        bbox_to_anchor=(1.02, 1),  # X=1.02 (just right of plot), Y=1 (top aligned)
        loc="upper left",  # Anchor the top-left corner of the legend to that point
        borderaxespad=0,  # Remove extra padding between anchor and legend
    )

    plt.savefig(
        output_dir / f"{metric_name}_vs_parameters.png",
        dpi=300,
        bbox_inches="tight",  # IMPORTANT: Prevents cutting off the legends/labels
        transparent=False,
    )
    plt.close(fig)


def plot_metric_over_years(
    models_metrics_over_years: dict,
    metric_parent: str,
    metric_name: str,
    title: str,
    output_dir: Path,
):
    metric_for_model = {}
    years = []
    for model_name, yearly_stats in models_metrics_over_years.items():
        if len(years) == 0:
            years = sorted(yearly_stats.keys(), key=int)
        assert years == sorted(
            yearly_stats.keys(), key=int
        ), "Years mismatch between models"
        metric_values = [yearly_stats[y][metric_parent][metric_name] for y in years]
        metric_for_model[model_name] = metric_values

    # Create plot with all models
    plt.figure(figsize=(12, 7))

    markers = ["o", "s", "^", "D", "v", "p", "h", "*"]
    linestyles = ["-"]

    for idx, (model_name, metric_values) in enumerate(metric_for_model.items()):
        plt.plot(
            years,
            metric_values,
            marker=markers[idx % len(markers)],
            linestyle=linestyles[idx % len(linestyles)],
            linewidth=2,
            markersize=6,
            label=model_name,
        )

    plt.title(title, y=1.15)
    plt.xlabel("Rok")
    plt.ylabel("Wartość metryki")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=3, fontsize=8)

    output_filename = f"{metric_name}_over_years.png"
    _save_plot(output_dir / output_filename)
    print(f"Saved plot to {output_dir / output_filename}")


def _save_plot(output_path: Path) -> Path:
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    return output_path
