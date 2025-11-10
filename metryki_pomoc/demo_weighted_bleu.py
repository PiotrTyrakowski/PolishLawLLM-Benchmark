"""Demonstracja ważonego BLEU z budowaniem zasobów TF-IDF z JSONL."""

from __future__ import annotations

import json
from pathlib import Path

from metryki_pomoc.text_metrics import WeightedBleuMetric


REFERENCE_FILE = Path(__file__).with_name("przyklad_referencji.jsonl")

REFERENCE = (
    "Zgodnie z art. 415 kodeksu cywilnego kto z winy swej wyrządził drugiemu szkodę,"
    " obowiązany jest do jej naprawienia."
)

CASES = [
    {"name": "identyczny", "prediction": REFERENCE},
    {
        "name": "parafraza z ważnymi tokenami",
        "prediction": (
            "Art. 415 kodeksu cywilnego stanowi, że kto z własnej winy spowodował szkodę,"
            " zobowiązany jest ją naprawić."
        ),
    },
    {
        "name": "krótkie streszczenie",
        "prediction": "Sprawca szkody odpowiada za jej naprawienie",
    },
]


def load_references() -> list[str]:
    data = []
    with REFERENCE_FILE.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                data.append(json.loads(line)["reference"])
    return data


def main() -> None:
    references = load_references()
    resources = WeightedBleuMetric.build_resources(references)
    metric = WeightedBleuMetric(resources, 2)

    print("Weighted BLEU demo\n====================")
    print(f"Loaded {len(references)} reference texts for TF-IDF baseline.\n")
    example_tokens = list(resources.idf_lookup.items())[:5]
    print("Sample IDF weights:")
    for token, value in example_tokens:
        print(f"  {token!r}: {value:.3f}")
    print()

    for case in CASES:
        score = metric(case["prediction"], REFERENCE)
        print(f"Case: {case['name']}")
        print(f"  prediction: {case['prediction']}")
        print(f"  reference : {REFERENCE}")
        print(f"  Weighted BLEU: {score:.4f}\n")


if __name__ == "__main__":
    main()
