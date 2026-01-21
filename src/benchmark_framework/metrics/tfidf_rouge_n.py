import json
import math
from pathlib import Path
from collections import Counter
from typing import List, Sequence

from src.benchmark_framework.metrics.base_metric import BaseMetric
from src.benchmark_framework.metrics.rouge_n import RougeNMetric
from src.common.text_formatter import TextFormatter


class TFIDFRougeNMetric(BaseMetric):
    def __init__(
        self, corpuses_dir: Path, ngrams_importances: List[float] = [1, 1, 1]
    ) -> None:
        super().__init__(f"rouge_n_tfidf")
        self.ngrams_importances = ngrams_importances
        self.build_idf_lookup(corpuses_dir=corpuses_dir)

    def build_idf_lookup(self, corpuses_dir: Path):
        self.idf_lookup = {}
        assert corpuses_dir.exists()
        for file in corpuses_dir.glob("*.json"):
            data = {}
            document_frequency = Counter()
            with open(file, "r") as f:
                data = json.load(f)

            # Skip empty corpus files
            if not data:
                continue

            for article_number, article_text in data.items():
                tokens = {
                    token.lower()
                    for token in self.get_normalized_words(
                        TextFormatter.format_extracted_text(article_text)
                    )
                }
                document_frequency.update(tokens)
            total_docs = len(data)
            assert total_docs > 0
            idf_lookup = {
                token: math.log(total_docs / (freq + 1)) + 1
                for token, freq in document_frequency.items()
            }
            self.idf_lookup[file.stem] = idf_lookup

    def _compute(self, prediction: str, reference: str, code_abbr: str) -> float:
        assert self.ngrams_importances is not None

        pred_tokens = self.get_normalized_words(prediction)
        ref_tokens = self.get_normalized_words(reference)
        max_possible_n = min(len(pred_tokens), len(ref_tokens))

        if max_possible_n == 0:
            return 0.0

        weighted_sum = 0.0
        total_weight = 0.0

        for n, weight in enumerate(self.ngrams_importances, start=1):
            if weight > 0 and n <= max_possible_n:
                recall = self.calculate_recall(prediction, reference, n, code_abbr)
                weighted_sum += weight * recall
                total_weight += weight

        assert total_weight > 0, "Total weight must be greater than zero."

        result = weighted_sum / total_weight
        assert 0.0 <= result <= 1.0
        return result

    def calculate_recall(
        self, prediction: str, reference: str, n: int, code_abbr: str
    ) -> float:
        """Calculate ROUGE-N recall score."""
        pred_tokens = self.get_normalized_words(prediction)
        ref_tokens = self.get_normalized_words(reference)

        pred_ngrams_counts = RougeNMetric.get_ngrams(pred_tokens, n)
        ref_ngram_counts = RougeNMetric.get_ngrams(ref_tokens, n)

        token_weights = self.get_tokens_tfidf(ref_tokens, code_abbr)

        nominator = 0
        denominator = 0

        for ngram, count in ref_ngram_counts.items():
            ngram_intersection_count = min(count, pred_ngrams_counts.get(ngram, 0))
            ngram_weight = self.get_ngram_weight(ngram, token_weights)
            nominator += ngram_intersection_count * ngram_weight
            denominator += count * ngram_weight

        recall = nominator / denominator if denominator > 0 else 0.0
        assert 0.0 <= recall <= 1.0
        return recall

    def get_tokens_tfidf(
        self, ref_tokens: Sequence[str], code_abbr: str
    ) -> dict[str, float]:
        assert self.idf_lookup is not None
        weights = {}
        assert (
            code_abbr in self.idf_lookup
        ), f"Code abbreviation '{code_abbr}' not found in IDF lookup"
        idf_dict = self.idf_lookup.get(code_abbr)

        for token in set(ref_tokens):
            assert len(token) > 0
            tf = ref_tokens.count(token) / len(ref_tokens)
            idf = idf_dict.get(token, 0)
            weights[token] = tf * idf

        return weights

    def get_ngram_weight(
        self, ngram: tuple[str, ...], token_weights: dict[str, float]
    ) -> float:
        assert self.idf_lookup is not None

        max_weight = max(token_weights.values())
        assert max_weight > 0.0
        weight = 0.0

        # if the token is not in the reference text, the tf part is 0
        for token in ngram:
            weight += token_weights.get(token, 0.0) / max_weight

        assert len(ngram) > 0
        ngram_weight = weight / len(ngram)
        assert 0.0 <= ngram_weight <= 1.0
        return ngram_weight
