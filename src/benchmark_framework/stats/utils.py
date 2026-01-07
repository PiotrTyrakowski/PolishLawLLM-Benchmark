from typing import Dict, Any


def print_stats(stats: Dict[str, Any]):
    """
    Pretty print statistics dictionary.
    """
    print("\n=== Results ===")
    print("Accuracy Metrics:")
    print(f"  Answer accuracy: {stats['accuracy_metrics']['answer']:.4f}")
    print(f"  Legal basis accuracy: {stats['accuracy_metrics']['legal_basis']:.4f}")

    print("\nText Metrics:")
    for metric_name, metric_value in sorted(stats["text_metrics"].items()):
        print(f"  {metric_name}: {metric_value:.4f}")

    print(f"\nMalformed Response Rate: {stats['malformed_response_rate']:.4f}")