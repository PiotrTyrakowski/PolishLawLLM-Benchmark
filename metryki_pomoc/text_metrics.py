from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from statistics import fmean
from typing import Iterable, Sequence

try:  # Optional heavy dependencies are loaded lazily.
    from bert_score import BERTScorer
except ImportError:  # pragma: no cover - handled at runtime
    BERTScorer = None  # type: ignore

try:
    from sentence_transformers import SentenceTransformer, util as st_util
except ImportError:  # pragma: no cover - handled at runtime
    SentenceTransformer = None  # type: ignore
    st_util = None  # type: ignore

from benchmark_framework.metrics.base_metric import BaseMetric

EPSYLON = 0.001


class ExactMatchMetric(BaseMetric):
    """Binary metric for comparing discrete labels (e.g., odpowiedzi A/B/C/D)."""

    def __init__(self) -> None:
        super().__init__("exact_match")

    def _compute(self, prediction: str, reference: str) -> float:
        normalize = lambda text: "".join(text.split()).upper()
        return 1.0 if normalize(prediction) == normalize(reference) else 0.0


class BleuMetric(BaseMetric):
    """Standard BLEU-N precision with Brevity Penalty."""

    def __init__(self, max_n: int = 4, weights: Sequence[float] | None = None) -> None:
        super().__init__(f"bleu_{max_n}gram")
        self.max_n = max_n
        if weights is None:
            self.weights = [1 / max_n] * max_n
        elif len(weights) != max_n:
            raise ValueError("weights must have the same length as max_n")
        else:
            self.weights = weights

    def _compute(self, prediction: str, reference: str) -> float:
        cand_tokens = prediction.split()
        ref_tokens = reference.split()
        if not cand_tokens or not ref_tokens:
            return 0.0

        bp = 1.0 if len(cand_tokens) > len(ref_tokens) else math.exp(
            1 - len(ref_tokens) / max(len(cand_tokens), 1)
        )

        log_precision_sum = 0.0
        for n, weight in enumerate(self.weights, start=1):
            cand_counts = _ngrams(cand_tokens, n)
            ref_counts = _ngrams(ref_tokens, n)

            print(cand_counts)
            print(ref_counts)
            if not cand_counts:
                return 0.0
            overlap = sum(
                min(count, ref_counts.get(ngram, 0)) for ngram, count in cand_counts.items()
            )
            precision = overlap / sum(cand_counts.values()) + EPSYLON
            if precision == 0.0:
                return 0.0
            log_precision_sum += weight * math.log(precision)

        return float(bp * math.exp(log_precision_sum))


@dataclass
class WeightedBleuResources:
    """Cache przechowujący preobliczone wartości IDF dla tokenów."""

    idf_lookup: dict[str, float]
    default_idf: float


class WeightedBleuMetric(BaseMetric):
    """BLEU modyfikowany wagami TF-IDF opisanymi w Lab2 (sekcja 8.4)."""

    def __init__(self, resources: WeightedBleuResources, max_n: int = 4) -> None:
        super().__init__("weighted_bleu")
        self.resources = resources
        self.max_n = max_n

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
        cand_tokens = prediction.split()
        ref_tokens = reference.split()
        if not cand_tokens or not ref_tokens:
            return 0.0

        token_weights = self._token_weights(ref_tokens)
        bp = 1.0 if len(cand_tokens) > len(ref_tokens) else math.exp(
            1 - len(ref_tokens) / max(len(cand_tokens), 1)
        )

        log_precision_sum = 0.0
        for n in range(1, self.max_n + 1):
            cand_counts = _ngrams(cand_tokens, n)
            ref_counts = _ngrams(ref_tokens, n)
            if not cand_counts:
                return 0.0

            numerator = 0.0
            denominator = 0.0
            for ngram, count in cand_counts.items():
                weight = self._weight_ngram(ngram, token_weights)
                numerator += min(count, ref_counts.get(ngram, 0)) * weight
                denominator += count * weight

            if numerator == 0.0 or denominator == 0.0:
                return 0.0
            log_precision_sum += (1 / self.max_n) * math.log(numerator / denominator)

        return float(bp * math.exp(log_precision_sum))

    def _token_weights(self, tokens: Sequence[str]) -> dict[str, float]:
        lookup = self.resources.idf_lookup
        default = self.resources.default_idf
        return {token.lower(): lookup.get(token.lower(), default) for token in tokens}

    @staticmethod
    def _weight_ngram(ngram: tuple[str, ...], token_weights: dict[str, float]) -> float:
        weights = [token_weights.get(token.lower(), 1.0) for token in ngram]
        return float(fmean(weights)) if weights else 1.0


class BertScoreMetric(BaseMetric):
    """BERTScore F1 dla języka polskiego (domyślnie XLM-R Large)."""

    def __init__(
        self,
        model_type: str = "xlm-roberta-large",
        lang: str = "pl",
        device: str | None = None,
    ) -> None:
        super().__init__("bert_score")
        if BERTScorer is None:  # pragma: no cover - dependency missing
            raise ImportError("bert-score package is required for BertScoreMetric")
        self.scorer = BERTScorer(
            model_type=model_type,
            lang=lang,
            rescale_with_baseline=True,
            device=device,
        )

    def _compute(self, prediction: str, reference: str) -> float:
        _, _, f1 = self.scorer.score([prediction], [reference])
        return float(f1.numpy()[0])


class SentenceBertSimilarityMetric(BaseMetric):
    """Kosinusowe podobieństwo Sentence-BERT przeskalowane do [0, 1]."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        device: str | None = None,
    ) -> None:
        super().__init__("sentence_bert")
        if SentenceTransformer is None or st_util is None:  # pragma: no cover
            raise ImportError(
                "sentence-transformers package is required for SentenceBertSimilarityMetric"
            )
        self.model = SentenceTransformer(model_name, device=device or "cpu")

    def _compute(self, prediction: str, reference: str) -> float:
        embeddings = self.model.encode(
            [prediction, reference], normalize_embeddings=True
        )
        score = float(st_util.cos_sim(embeddings[0], embeddings[1]))
        return (score + 1) / 2


def _ngrams(tokens: Sequence[str], n: int) -> Counter[tuple[str, ...]]:
    return Counter(tuple(tokens[i : i + n]) for i in range(max(len(tokens) - n + 1, 0)))
