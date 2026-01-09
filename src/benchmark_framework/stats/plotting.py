from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt

from src.benchmark_framework.stats.calculate_stats import collect_yearly_stats

def plot_metric_over_years(models_metrics_over_years: dict, metric_parent: str, metric_name: str, title: str, output_dir: Path):
    metric_for_model = {}
    years = []
    for model_name, yearly_stats in models_metrics_over_years.items():
        if len(years) == 0:
            years = sorted(yearly_stats.keys(), key=int)
        assert years == sorted(yearly_stats.keys(), key=int), "Years mismatch between models"
        metric_values = [yearly_stats[y][metric_parent][metric_name] for y in years]
        metric_for_model[model_name] = metric_values

    # Create plot with all models
    plt.figure(figsize=(12, 7))
    
    markers = ['o', 's', '^', 'D', 'v', 'p', 'h', '*']
    linestyles = ['-']
    
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
    plt.ylim(0, 1.05)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=3, fontsize=8)
    
    output_filename = f"{metric_name}_over_years.png"
    _save_plot(output_dir / output_filename)
    print(f"Saved plot to {output_dir / output_filename}")


def _save_plot(output_path: Path) -> Path:
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    return output_path
