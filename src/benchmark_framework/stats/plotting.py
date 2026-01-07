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
        label="Dokładność odpowiedzi",
    )
    plt.plot(
        years,
        legal_acc,
        marker="o",
        linestyle="--",
        linewidth=2,
        label="Dokładność oznaczenia podstawy prawnej",
    )
    plt.plot(
        years,
        exact_match,
        marker="o",
        linestyle=":",
        linewidth=2,
        label="Dokładność treści przepisu",
    )

    plt.title(f"{model_name} - Dokładność na przestrzeni lat")
    plt.xlabel("Rok")
    plt.ylabel("Wartość metryki")
    plt.ylim(0, 1.05)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()

    output_filename = f"accuracy_over_years_{model_name}.png"
    _save_plot(output_dir / output_filename)


def plot_text_metrics_over_years(base_path: Path, model_name: str, output_dir: Path):
    yearly_stats = collect_yearly_stats(base_path)

    years = sorted(yearly_stats.keys(), key=int)

    answer_acc = [yearly_stats[y]["text_metrics"]["rouge_w"] for y in years]
    legal_acc = [yearly_stats[y]["text_metrics"]["rouge_n_f1"] for y in years]
    exact_match = [yearly_stats[y]["text_metrics"]["rouge_n_tfidf"] for y in years]

    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(
        years,
        answer_acc,
        marker="o",
        linestyle="-",
        linewidth=2,
        label="ROUGE-W F1",
    )
    plt.plot(
        years,
        legal_acc,
        marker="o",
        linestyle="--",
        linewidth=2,
        label="ROUGE-N F1",
    )
    plt.plot(
        years,
        exact_match,
        marker="o",
        linestyle=":",
        linewidth=2,
        label="ROUGE-N TF-IDF recall",
    )

    plt.title(f"{model_name} - Metryki tekstowe na przestrzeni lat")
    plt.xlabel("Rok")
    plt.ylabel("Wartość metryki")
    plt.ylim(0, 1.05)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()

    output_filename = f"text_metrics_over_years_{model_name}.png"
    _save_plot(output_dir / output_filename)


def _save_plot(output_path: Path) -> Path:
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    return output_path
