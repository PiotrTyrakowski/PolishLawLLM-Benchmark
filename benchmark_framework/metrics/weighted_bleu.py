
import math
from collections import Counter
from dataclasses import dataclass
from statistics import fmean
from typing import Iterable, Sequence
from base_metric import BaseMetric


@dataclass
class WeightedBleuResources:
    """Cache przechowujący preobliczone wartości IDF dla tokenów."""

    idf_lookup: dict[str, float]
    default_idf: float


class WeightedBleuMetric(BaseMetric):
    """BLEU modyfikowany wagami TF-IDF opisanymi w Lab2 (sekcja 8.4).
    Pozwala także ustawić ważność rozmiaru n-gramów przez ngram_importances."""

    def __init__(
        self, 
        ngram_importances: Sequence[float] = [1, 1, 1, 1],
        resources: WeightedBleuResources = None
    ) -> None:
        """
        Args:
            ngram_importances: Importance for each n-gram size (from 1 to max_n) default [1, 1, 1, 1]
            resources: WeightedBleuResources with IDF mapping
        """
        if not resources:
            raise ValueError("resources were not provided")

        self.max_n = len(ngram_importances)
        super().__init__(f"weighted_bleu_max_{self.max_n}gram")
        self.resources = resources
        self.ngram_importances = [x / sum(ngram_importances) for x in ngram_importances] 

    @classmethod
    def build_resources(cls, documents: Iterable[str]) -> WeightedBleuResources:
        docs = [doc for doc in documents if doc.strip()]
        if not docs:
            raise ValueError("documents must contain at least one non-empty string")

        document_frequency: Counter[str] = Counter()
        for doc in docs:
            tokens = {token.lower() for token in doc.split()}
            document_frequency.update(tokens)

        total_docs = len(docs)
        idf_lookup = {
            token: math.log((total_docs + 1) / (freq + 1)) + 1 for token, freq in document_frequency.items()
        }
        default_idf = math.log(total_docs + 1) + 1
        return WeightedBleuResources(idf_lookup=idf_lookup, default_idf=default_idf)

    def _compute(self, prediction: str, reference: str) -> float:
        cand_tokens = prediction.lower().split()
        ref_tokens = reference.lower().split()
        if not cand_tokens or not ref_tokens:
            return 0.0

        token_weights = self._token_weights(ref_tokens)
        bp = 1.0 if len(cand_tokens) > len(ref_tokens) else math.exp(
            1 - len(ref_tokens) / max(len(cand_tokens), 1)
        )

        log_precision_sum = 0.0
        for n, importance in enumerate(self.ngram_importances, start=1):
            cand_counts = self._ngrams(cand_tokens, n)
            ref_counts = self._ngrams(ref_tokens, n)
            if not cand_counts:
                return 0.0

            numerator = 0.0
            denominator = 0.0
            for ngram, count in cand_counts.items():
                weight = self._weight_ngram(ngram, token_weights)
                numerator += min(count, ref_counts.get(ngram, 0)) * weight
                denominator += count * weight

            precision = self.epsylon  # >0
            if numerator > 0.0 and denominator > 0.0:
                precision += numerator / denominator

            log_precision_sum += importance * math.log(precision)

        return float(bp * math.exp(log_precision_sum))

    def _token_weights(self, tokens: Sequence[str]) -> dict[str, float]:
        lookup = self.resources.idf_lookup
        default = self.resources.default_idf
        return {token.lower(): lookup.get(token.lower(), default) for token in tokens}

    @staticmethod
    def _weight_ngram(ngram: tuple[str, ...], token_weights: dict[str, float]) -> float:
        weights = [token_weights.get(token.lower(), 1.0) for token in ngram]
        return float(fmean(weights)) if weights else 1.0

    @staticmethod
    def _ngrams(tokens: Sequence[str], n: int) -> Counter[tuple[str, ...]]:
        return Counter(tuple(tokens[i : i + n]) for i in range(max(len(tokens) - n + 1, 0)))