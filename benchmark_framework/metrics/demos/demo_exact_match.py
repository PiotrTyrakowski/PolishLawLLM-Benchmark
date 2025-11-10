"""Demonstracja metryki ExactMatch na przykładowych odpowiedziach ABCD."""

from __future__ import annotations

from exact_match import ExactMatchMetric


CASES = [
    {"name": "dokładnie ta sama litera", "prediction": "A", "reference": "A"},
    {"name": "różna litera", "prediction": "B", "reference": "C"},
    {"name": "różne odstępy", "prediction": "  d  ", "reference": "D"},
]


def main() -> None:
    metric = ExactMatchMetric()
    print("ExactMatchMetric demo\n=====================")
    for case in CASES:
        score = metric(case["prediction"], case["reference"])
        print(f"Case: {case['name']}")
        print(f"  prediction: {case['prediction']!r}")
        print(f"  reference : {case['reference']!r}")
        print(f"  score     : {score:.2f}\n")


if __name__ == "__main__":
    main()
