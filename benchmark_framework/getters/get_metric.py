from benchmark_framework.metrics.base_metric import BaseMetric
from benchmark_framework.metrics.exact_match import ExactMatchMetric
from benchmark_framework.metrics.weighted_bleu import WeightedBleuMetric
from benchmark_framework.constants import DATA_PATH

METRIC_REGISTRY = {
    "exact_match": ExactMatchMetric,
    "weighted_bleu": WeightedBleuMetric,
    "bleu": WeightedBleuMetric,  # 'bleu' is an alias for 'weighted_bleu'
}

REFERENCE_FILE = DATA_PATH / "kk_extracted.txt"


def get_metric(
    metric_name: str,
    ngram_importances=None,
) -> BaseMetric:
    """
    Factory function to get a metric instance by metric name.

    Args:
        metric_name: The name of the metric (e.g., 'exact_match', 'weighted_bleu', 'bleu').
        ngram_importances: Optional sequence of floats for n-gram importances (only for BLEU metrics).

    Returns:
        An instance of the specified metric class.

    Raises:
        ValueError: If the metric name is not recognized.
    """
    metric_class = METRIC_REGISTRY.get(metric_name.lower())
    if not metric_class:
        raise ValueError(f"Metric name '{metric_name}' is not recognized.")

    if metric_class == ExactMatchMetric:
        return metric_class()
    elif metric_class == WeightedBleuMetric:
        kwargs = {}
        if ngram_importances is not None:
            kwargs["ngram_importances"] = ngram_importances

        if metric_name.lower() == "weighted_bleu":
            references = load_references()
            kwargs["resources"] = WeightedBleuMetric.build_resources(references)

        return metric_class(**kwargs)


def load_references() -> list[str]:
    """
    Load reference lines from the reference file, ignoring blank lines.
    """
    data = []
    with REFERENCE_FILE.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                data.append(line)
    return data


def main() -> None:
    """
    Demonstration/test for the metric getters and sample scoring.
    """
    references = load_references()
    exact_match = get_metric("exact_match")
    bleu = get_metric("bleu", [0.7, 0.3])
    weighted_bleu = get_metric("weighted_bleu", [0.7, 0.3])
    print(exact_match("obejmuje uczestnictwa", "obejmuje uczestnictwa"))
    print(bleu("obejmuje uczestnictwa", "obejmuje uczestnictwa"))
    print(weighted_bleu("obejmuje uczestnictwa", "obejmuje uczestnictwa"))


if __name__ == "__main__":
    main()
