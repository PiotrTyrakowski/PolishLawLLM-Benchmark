import argparse
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict
import matplotlib.pyplot as plt

from src.common.file_operations import FileOperations


def calculate_stats(file_path: Path) -> Dict[str, Any]:
    """
    Loads a JSONL file and calculates accuracy and averages for all text metrics.
    """
    dataset = FileOperations.load_jsonl(file_path)
    total_count = len(dataset)

    if total_count == 0:
        return {
            "accuracy_metrics": {"answer": 0.0, "legal_basis": 0.0},
            "text_metrics": {},
            "malformed_response_rate": 0.0,
            "questions_count": 0,
        }

    correct_count = 0
    correct_legal_basis = 0
    malformed_responses_count = 0

    # Accumulators for text metrics (dynamically collected)
    text_metrics_sum = defaultdict(float)

    for data in dataset:
        accuracy_metrics = data.get("accuracy_metrics", {})
        is_correct = accuracy_metrics.get("answer", False)
        if is_correct:
            correct_count += 1

        is_correct_legal_basis = accuracy_metrics.get("legal_basis", False)
        if is_correct_legal_basis:
            correct_legal_basis += 1

        required_keys = [
            "model_legal_basis_content",
            "model_legal_basis",
            "model_answer",
        ]
        if any(not (data.get(k) or "").strip() for k in required_keys):
            malformed_responses_count += 1

        # Accumulate all text metrics dynamically
        text_metrics = data.get("text_metrics", {})
        for metric_name, metric_value in text_metrics.items():
            assert isinstance(metric_value, (int, float))
            text_metrics_sum[metric_name] += metric_value

    accuracy = correct_count / total_count
    legal_basis = correct_legal_basis / total_count
    malformed_response_rate = malformed_responses_count / total_count

    avg_text_metrics = {
        metric_name: total_sum / total_count
        for metric_name, total_sum in text_metrics_sum.items()
    }

    return {
        "accuracy_metrics": {"answer": accuracy, "legal_basis": legal_basis},
        "text_metrics": avg_text_metrics,
        "malformed_response_rate": malformed_response_rate,
        "questions_count": total_count,
    }


def aggregate_results(results_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates the average of metrics across multiple result dictionaries.
    """
    if not results_list:
        return {}

    # Accumulators
    correct_answers_sum = 0.0
    correct_legal_basis_sum = 0.0
    malformed_sum = 0.0
    total_questions_count = 0
    text_metrics_sums = defaultdict(float)

    for res in results_list:
        questions_count = res.get("questions_count")
        if questions_count is None or questions_count == 0:
            continue

        total_questions_count += questions_count
        correct_answers_sum += (
            res["accuracy_metrics"].get("answer", 0.0) * questions_count
        )
        correct_legal_basis_sum += (
            res["accuracy_metrics"].get("legal_basis", 0.0) * questions_count
        )
        malformed_sum += res.get("malformed_response_rate", 0.0) * questions_count

        for k, v in res.get("text_metrics", {}).items():
            text_metrics_sums[k] += v * questions_count

    if total_questions_count == 0:
        raise ValueError("Total questions count is zero; cannot aggregate results.")

    # Average out
    avg_accuracy = {
        "answer": correct_answers_sum / total_questions_count,
        "legal_basis": correct_legal_basis_sum / total_questions_count,
    }
    avg_malformed = malformed_sum / total_questions_count
    avg_text_metrics = {}
    for k, total_val in text_metrics_sums.items():
        avg_text_metrics[k] = total_val / total_questions_count

    return {
        "accuracy_metrics": avg_accuracy,
        "text_metrics": avg_text_metrics,
        "malformed_response_rate": avg_malformed,
    }


def plot_year_metrics(
    years: List[str], metrics_over_years: dict[str, list[float]], model_name: str
):
    """Generates and saves the accuracy plot."""
    if plt is None:
        print("Error: 'matplotlib' is not installed. Cannot generate plot.")
        return

    plt.figure(figsize=(10, 6))

    # Plot Answer Accuracy
    plt.plot(
        years,
        metrics_over_years["answer"],
        marker="o",
        linestyle="-",
        linewidth=2,
        label="Answer Accuracy",
    )

    # Plot Legal Basis Accuracy
    plt.plot(
        years,
        metrics_over_years["legal_basis"],
        marker="o",
        linestyle="--",
        linewidth=2,
        label="Legal Basis Accuracy",
    )

    plt.plot(
        years,
        metrics_over_years["exact_match"],
        marker="o",
        linestyle=":",
        linewidth=2,
        label="Exact Match Accuracy",
    )

    plt.title(f"{model_name} - year")
    plt.xlabel("Year")
    plt.ylabel("Accuracy")
    plt.ylim(0, 1.05)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()

    output_filename = f"accuracy_over_years_{model_name}.png"
    plt.tight_layout()
    plt.savefig(output_filename)
    print(f"\nPlot saved to: {output_filename}")


def process_standard_mode(input_path: Path):
    """The original functionality: recursive aggregation."""
    target_files: List[Path] = []

    if input_path.is_dir():
        target_files = list(input_path.rglob("*.jsonl"))
        if not target_files:
            print(f"No .jsonl files found in directory '{input_path}'.")
            exit(0)
        print(f"Found {len(target_files)} files. Processing...")
    elif input_path.is_file():
        target_files = [input_path]
    else:
        print(f"Error: incorrect input path '{input_path}'.")
        exit(1)

    all_results = []
    for file in target_files:
        try:
            res = calculate_stats(file)
            all_results.append(res)
        except Exception as e:
            print(f"Warning: Failed to process {file}. Error: {e}")

    if not all_results:
        print("No valid results computed.")
        exit(1)

    if len(all_results) == 1:
        final_results = all_results[0]
    else:
        final_results = aggregate_results(all_results)

    print_final_results(final_results)


def process_year_mode(base_path: Path, model_name: str):
    if not base_path.is_dir():
        print(
            f"Error: Path '{base_path}' is not a directory. Cannot perform year-based analysis."
        )
        exit(1)

    # Find year directories (digits only)
    year_dirs = sorted(
        [d for d in base_path.iterdir() if d.is_dir() and d.name.isdigit()],
        key=lambda x: int(x.name),
    )

    if not year_dirs:
        print("No year directories (e.g., '2016', '2017') found.")
        exit(0)

    years_label = []
    answer_accuracies = []
    legal_basis_accuracies = []
    exact_match_over_years = []

    print(f"Processing yearly stats for model: {model_name}\n")
    print(f"{'Year':<10} | {'Answer Acc':<12} | {'Legal Acc':<12} | {'Files':<5}")
    print("-" * 45)

    metrics_over_years = {}

    for year_dir in year_dirs:
        year_name = year_dir.name
        jsonl_files = list(year_dir.glob("*.jsonl"))

        if not jsonl_files:
            continue

        year_results = []
        for file in jsonl_files:
            res = calculate_stats(file)
            year_results.append(res)
        if len(year_results) == 0:
            continue

        aggregated = aggregate_results(year_results)

        acc_answer = aggregated["accuracy_metrics"].get("answer", 0.0)
        acc_legal = aggregated["accuracy_metrics"].get("legal_basis", 0.0)
        exact_match = aggregated["text_metrics"].get("exact_match", 0.0)

        years_label.append(year_name)
        answer_accuracies.append(acc_answer)
        legal_basis_accuracies.append(acc_legal)
        exact_match_over_years.append(exact_match)

        print(
            f"{year_name:<10} | {acc_answer:.4f}       | {acc_legal:.4f}       | {len(jsonl_files):<5}"
        )

    metrics_over_years["exact_match"] = exact_match_over_years
    metrics_over_years["answer"] = answer_accuracies
    metrics_over_years["legal_basis"] = legal_basis_accuracies

    # Generate Plot
    if years_label:
        plot_year_metrics(years_label, metrics_over_years, model_name)
    else:
        print("No data found to plot.")


def print_final_results(final_results: Dict[str, Any]):
    print()
    print("=== Results ===")
    print("Accuracy Metrics:")
    print(f"  Answer accuracy: {final_results['accuracy_metrics']['answer']:.4f}")
    print(
        f"  Legal basis accuracy: {final_results['accuracy_metrics']['legal_basis']:.4f}"
    )
    print()
    print("Text Metrics:")
    for metric_name, metric_value in sorted(final_results["text_metrics"].items()):
        print(f"  {metric_name}: {metric_value:.4f}")
    print()
    print(f"Malformed Response Rate: {final_results['malformed_response_rate']:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate statistics from a JSONL file with benchmark results."
    )
    parser.add_argument(
        "file_path",
        type=Path,
        help="Path to the JSONL file or directory containing benchmark results.",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Enable year-by-year aggregation and plotting.",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        help="Name of the model (required if --plot is used) for the chart title.",
    )

    args = parser.parse_args()
    input_path: Path = args.file_path

    if not input_path.exists():
        print(f"Error: Path '{input_path}' not found.")
        exit(1)

    if args.plot:
        if not args.model_name:
            print("Error: --model-name is required when --plot is used.")
            exit(1)
        process_year_mode(input_path, args.model_name)
    else:
        process_standard_mode(input_path)
