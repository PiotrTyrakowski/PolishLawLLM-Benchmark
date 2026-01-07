from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt

from src.benchmark_framework.stats.calculate_stats import collect_yearly_stats


def plot_accuracy_over_years(
        base_path: Path, model_name: str, output_dir: Optional[Path] = None
):
    yearly_stats = collect_yearly_stats(base_path)

    years = sorted(yearly_stats.keys(), key=int)
    answer_acc = [yearly_stats[y]["accuracy_metrics"]["answer"] for y in years]
    legal_acc = [yearly_stats[y]["accuracy_metrics"]["legal_basis"] for y in years]
    exact_match = [
        yearly_stats[y]["text_metrics"].get("exact_match", 0.0) for y in years
    ]

    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(
        years,
        answer_acc,
        marker="o",
        linestyle="-",
        linewidth=2,
        label="Answer Accuracy",
    )
    plt.plot(
        years,
        legal_acc,
        marker="o",
        linestyle="--",
        linewidth=2,
        label="Legal Basis Accuracy",
    )
    plt.plot(
        years,
        exact_match,
        marker="o",
        linestyle=":",
        linewidth=2,
        label="Exact Match Accuracy",
    )

    plt.title(f"{model_name} - Accuracy Over Years")
    plt.xlabel("Year")
    plt.ylabel("Accuracy")
    plt.ylim(0, 1.05)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()

    output_filename = f"accuracy_over_years_{model_name}.png"
    _save_plot(output_dir / output_filename)


def plot_text_metrics_over_years(
        base_path: Path, model_name: str, output_dir: Path
):
    yearly_stats = collect_yearly_stats(base_path)

    years = sorted(yearly_stats.keys(), key=int)

    # Collect all unique text metrics
    all_metrics = set()
    for stats in yearly_stats.values():
        all_metrics.update(stats["text_metrics"].keys())

    if not all_metrics:
        print("No text metrics found to plot.")
        return

    # Prepare data for each metric
    metrics_data = {}
    for metric in sorted(all_metrics):
        metrics_data[metric] = [
            yearly_stats[y]["text_metrics"].get(metric, 0.0) for y in years
        ]

    # Create plot
    plt.figure(figsize=(12, 7))
    for metric, values in metrics_data.items():
        plt.plot(years, values, marker="o", linewidth=2, label=metric)

    plt.title(f"{model_name} - Text Metrics Over Years")
    plt.xlabel("Year")
    plt.ylabel("Metric Value")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    output_filename = f"text_metrics_over_years_{model_name}.png"
    _save_plot(output_dir / output_filename)


def _save_plot(output_path: Path) -> Path:
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    return output_path