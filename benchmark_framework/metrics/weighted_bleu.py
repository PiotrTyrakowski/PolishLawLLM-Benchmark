import math
import json
from pathlib import Path
from collections import Counter
from dataclasses import dataclass
from statistics import fmean
from typing import Iterable, Sequence, Optional
from benchmark_framework.metrics.base_metric import BaseMetric
from parsers.utils.text_utils import TextFormatter

EPSILON = 1e-1


class WeightedBleuMetric(BaseMetric):
    """BLEU metric that can use TF-IDF weights or standard BLEU calculation.
    When resources is None, behaves like standard BLEU. When resources are provided,
    uses TF-IDF weighted BLEU. Also allows setting n-gram size importance through ngram_importances.
    """

    def __init__(
        self,
        ngram_importances: Sequence[float] = [1, 1, 1, 1],
        corpuses_dir: Path = None,
    ) -> None:
        """
        Args:
            ngram_importances: Importance for each n-gram size (from 1 to max_n) default [1, 1, 1, 1]
            corpuses_dir: Directory containing corpuses in JSON format
        """
        self.max_n = len(ngram_importances)
        metric_name = (
            f"weighted_bleu_max_{self.max_n}gram"
            if corpuses_dir
            else f"bleu_max_{self.max_n}gram"
        )
        super().__init__(metric_name)
        self.idf_lookup = {}
        if corpuses_dir:
            self.build_idf_lookup(corpuses_dir)
        else:
            self.idf_lookup = None
        self.ngram_importances = [x / sum(ngram_importances) for x in ngram_importances]

    def build_idf_lookup(self, corpuses_dir: Path):
        for file in corpuses_dir.glob("*.json"):
            data = {}
            document_frequency = Counter()
            with open(file, "r") as f:
                data = json.load(f)
            for article_number, article_text in data.items():
                tokens = {
                    token.lower() for token in self.get_normalized_words(TextFormatter.format_extracted_text(article_text))
                }
                document_frequency.update(tokens)
            total_docs = len(data)
            idf_lookup = {
                token: math.log((total_docs + 1) / (freq + 1)) + 1
                for token, freq in document_frequency.items()
            }
            self.idf_lookup[file.stem] = idf_lookup

    def _compute(
        self, prediction: str, reference: str, code_abbr: Optional[str] = None
    ) -> float:
        cand_tokens = self.get_normalized_words(prediction)
        ref_tokens = self.get_normalized_words(reference)
        if not cand_tokens or not ref_tokens:
            return 0.0

        bp = (
            1.0
            if len(cand_tokens) > len(ref_tokens)
            else math.exp(1 - len(ref_tokens) / max(len(cand_tokens), 1))
        )

        log_precision_sum = 0.0
        valid_ngrams_count = 0
        for n, importance in enumerate(self.ngram_importances, start=1):
            cand_counts = self._ngrams(cand_tokens, n)
            ref_counts = self._ngrams(ref_tokens, n)

            # If there are no candidate n-grams, skip the calculation
            if not cand_counts:
                continue

            # Weighted BLEU calculation (with IDF weights)
            token_weights = self._token_weights(ref_tokens, code_abbr)
            numerator = 0.0
            denominator = 0.0
            for ngram, count in cand_counts.items():
                weight = self._weight_ngram(ngram, token_weights)
                numerator += min(count, ref_counts.get(ngram, 0)) * weight
                denominator += count * weight

            if denominator == 0.0:
                print(
                    f"Warning: Weighted BLEU Denominator is 0 for n={n} and prediction={prediction}"
                )
                continue

            precision = numerator / denominator

            if precision > 0:
                valid_ngrams_count += 1
            else:
                precision = EPSILON
            log_precision_sum += importance * math.log(precision)

        # If no n-grams matched at all, return 0
        if valid_ngrams_count == 0:
            return 0.0

        return float(bp * math.exp(log_precision_sum))

    def _token_weights(
        self, tokens: Sequence[str], code_abbr: Optional[str] = None
    ) -> dict[str, float]:
        if self.idf_lookup is None or code_abbr is None:
            return {token.lower(): 1.0 for token in tokens}

        weights = {}
        idf_dict = self.idf_lookup.get(code_abbr)
        for token in set(tokens):
            assert len(token) > 0
            tf = tokens.count(token) / len(tokens)
            idf = idf_dict.get(token)
            if idf is None:
                raise ValueError(f"Token '{token}' not found in {code_abbr} IDF lookup")
            weights[token.lower()] = tf * idf

        return weights

    def _weight_ngram(
        self, ngram: tuple[str, ...], token_weights: dict[str, float]
    ) -> float:
        if not self.idf_lookup:
            return 1.0

        max_weight = max(token_weights.values())
        assert max_weight > 0.0
        weight = 0.0

        # if the token is not in the reference text, the tf part is 0
        for token in ngram:
            weight += token_weights.get(token.lower(), 0.0) / max_weight

        assert len(ngram) > 0
        return weight / len(ngram)

    @staticmethod
    def _ngrams(tokens: Sequence[str], n: int) -> Counter[tuple[str, ...]]:
        return Counter(
            tuple(tokens[i : i + n]) for i in range(max(len(tokens) - n + 1, 0))
        )
