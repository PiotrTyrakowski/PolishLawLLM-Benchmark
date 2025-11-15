from benchmark_framework.metrics.base_metric import BaseMetric
from benchmark_framework.metrics.exact_match import ExactMatchMetric
from benchmark_framework.metrics.weighted_bleu import WeightedBleuMetric

METRIC_REGISTRY = {
    "exact_match": ExactMatchMetric,
    "weighted_bleu": WeightedBleuMetric,
    "bleu": WeightedBleuMetric,  # Alias for weighted_bleu
}


def get_metric(
    metric_name: str,
    ngram_importances=None,
    resources=None,
) -> BaseMetric:
    """
    Factory function to get a metric instance by metric name.

    Args:
        metric_name: The name of the metric (e.g., 'exact_match', 'weighted_bleu', 'bleu').
        ngram_importances: Optional sequence of floats for n-gram importances (only for BLEU metrics).
        resources: Optional WeightedBleuResources for TF-IDF weighted BLEU (only for BLEU metrics).

    Returns:
        An instance of the specified metric class.

    Raises:
        ValueError: If the metric name is not recognized.
    """
    metric_class = METRIC_REGISTRY.get(metric_name.lower())
    if not metric_class:
        raise ValueError(f"Metric name '{metric_name}' is not recognized.")

    # Handle different metric initialization based on type
    if metric_class == ExactMatchMetric:
        return metric_class()
    elif metric_class == WeightedBleuMetric:
        kwargs = {}
        if ngram_importances is not None:
            kwargs["ngram_importances"] = ngram_importances
        if resources is not None:
            kwargs["resources"] = resources
        return metric_class(**kwargs)
    else:
        # Default: try to instantiate with no arguments
        return metric_class()

