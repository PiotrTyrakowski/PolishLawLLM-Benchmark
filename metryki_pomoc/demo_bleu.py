"""Prosty skrypt pokazujący jak zachowuje się klasyczny BLEU dla kilku przypadków."""

from __future__ import annotations

from metryki_pomoc.text_metrics import BleuMetric


REFERENCE = (
    "Zgodnie z art. 415 kodeksu cywilnego kto z winy swej wyrządził drugiemu szkodę,"
    " obowiązany jest do jej naprawienia."
)

CASES = [
    {"name": "tekst identyczny", "prediction": REFERENCE},
    {
        "name": "parafraza",
        "prediction": (
            "Kto z własnej winy wyrządził komuś szkodę, musi ją naprawić zgodnie z art. 415 k.c."
        ),
    },
    {
        "name": "parafraza z ważnymi tokenami",
        "prediction": "Art. 415 kodeksu cywilnego stanowi, że kto z własnej winy spowodował szkodę, zobowiązany jest ją naprawić."
    },
    {
        "name": "część zdania",
        "prediction": "Sprawca szkody jest zobowiązany do jej naprawienia",
    },
    {
        "name": "zupełnie inny artykuł",
        "prediction": "Sąd może oddalić powództwo, jeżeli brak podstaw prawnych do roszczenia",
    },
]


def main() -> None:
    metric = BleuMetric([0.7, 0.3])
    print("BLEU demo\n=========")
    for case in CASES:
        score = metric(case["prediction"], REFERENCE)
        print(f"Case: {case['name']}")
        print(f"  prediction: {case['prediction']}")
        print(f"  reference : {REFERENCE}")
        print(f"  BLEU score: {score:.4f}\n")


if __name__ == "__main__":
    main()
