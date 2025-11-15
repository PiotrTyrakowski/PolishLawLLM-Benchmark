"""Demonstracja ważonego BLEU z budowaniem zasobów TF-IDF z JSONL."""

from __future__ import annotations

import json
from pathlib import Path

from weighted_bleu import WeightedBleuMetric

REFERENCE_FILE = Path(__file__).parent.parent / "kk_extracted.txt"

REFERENCE = (
    "Art. 53. § 1. Sąd wymierza karę według swojego uznania, w granicach "
    "przewidzianych w ustawie, uwzględniając stopień społecznej szkodliwości czynu, "
    "okoliczności obciążające i okoliczności łagodzące, cele kary w zakresie społecznego "
    "oddziaływania, a także cele zapobiegawcze, które ma ona osiągnąć w stosunku do "
    "skazanego. Dolegliwość kary nie może przekraczać stopnia winy."
)

CASES = [
    {"name": "identyczny", "prediction": REFERENCE},
    {
        "name": "parafraza z ważnymi tokenami",
        "prediction": (
            "Zgodnie z art. 53 § 1 kk, sąd wymierza karę w granicach ustawy, kierując się swoim "
            "uznaniem i uwzględniając społeczną szkodliwość, cele zapobiegawcze i wychowawcze "
            "kary oraz stopień winy."
        ),
    },
    {
        "name": "krótkie streszczenie",
        "prediction": "Sąd wymierza karę wedle uznania, biorąc pod uwagę szkodliwość czynu, cele kary i winę sprawcy.",
    },
    {
        "name": "inne sformułowanie, to samo znaczenie",
        "prediction": (
            "Organ sądowy, w ramach ustawowych, swobodnie decyduje o karze, rozważając społeczną "
            "szkodliwość, cele prewencyjne i represyjne, przy czym kara nie może być surowsza niż wina."
        ),
    },
    {
        "name": "częściowa zgodność",
        "prediction": "Dolegliwość kary nie może przekraczać stopnia winy.",
    },
    {
        "name": "słowa kluczowe, zły kontekst",
        "prediction": "Wina sądu jest oczywista, kara za społeczną szkodliwość czynu musi być dotkliwa.",
    },
    {
        "name": "lekko błędna informacja",
        "prediction": (
            "Sąd wymierza karę według swojego uznania, ale dolegliwość kary może przekraczać "
            "stopień winy w wyjątkowych okolicznościach."
        ),
    },
    {
        "name": "bardzo abstrakcyjne streszczenie",
        "prediction": "Wymiar sprawiedliwości polega na dostosowaniu kary do czynu i sprawcy.",
    },
    {
        "name": "całkowicie niepowiązane",
        "prediction": (
            "Zgodnie z art. 415 kodeksu cywilnego kto z winy swej wyrządził drugiemu szkodę, "
            "obowiązany jest do jej naprawienia."
        ),
    },
    {
        "name": "dłuższa parafraza z dodatkami",
        "prediction": (
            "Artykuł 53, paragraf 1 kodeksu karnego stanowi, że sąd ma swobodę w wymierzaniu "
            "kary, ale musi działać w granicach prawa. Przy wymiarze kary sąd bierze pod "
            "uwagę wiele czynników, takich jak społeczna szkodliwość, cele prewencyjne i "
            "wychowawcze wobec skazanego, a także okoliczności łagodzące i obciążające. "
            "Co najważniejsze, kara nigdy nie może być bardziej dotkliwa niż stopień "
            "zawinienia sprawcy."
        ),
    },
]


def load_references() -> list[str]:
    data = []
    with REFERENCE_FILE.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                data.append((line))
    return data


def main() -> None:
    references = load_references()
    resources = WeightedBleuMetric.build_resources(references)
    metric = WeightedBleuMetric([0.7, 0.3], resources)

    print("Weighted BLEU demo\n====================")
    print(f"Loaded {len(references)} reference texts for TF-IDF baseline.\n")
    example_tokens = list(resources.idf_lookup.items())[:5]
    print("Sample IDF weights:")
    for token, value in example_tokens:
        print(len(example_tokens))
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
