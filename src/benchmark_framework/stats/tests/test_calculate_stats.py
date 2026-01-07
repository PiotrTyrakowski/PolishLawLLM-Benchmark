import pytest

from src.benchmark_framework.stats.calculate_stats import calculate_stats
from src.benchmark_framework.stats.tests.conftest import create_temp_jsonl


class TestCalculateStats:
    """Tests for the calculate_stats function."""

    def test_empty_dataset_returns_zero_stats(self, tmp_path):
        """Test that an empty dataset returns zero values."""
        file_path = create_temp_jsonl([], tmp_path)

        result = calculate_stats(file_path)

        assert result["accuracy_metrics"]["answer"] == 0.0
        assert result["accuracy_metrics"]["legal_basis"] == 0.0
        assert result["text_metrics"] == {}
        assert result["malformed_response_rate"] == 0.0
        assert result["questions_count"] == 0

    def test_all_correct_answers(self, tmp_path):
        """Test that all correct answers return accuracy of 1.0."""
        entries = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            },
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                "model_legal_basis_content": "content2",
                "model_legal_basis": "basis2",
                "model_answer": "answer2",
            },
        ]
        file_path = create_temp_jsonl(entries, tmp_path)

        result = calculate_stats(file_path)

        assert result["accuracy_metrics"]["answer"] == 1.0
        assert result["accuracy_metrics"]["legal_basis"] == 1.0
        assert result["malformed_response_rate"] == 0.0
        assert result["questions_count"] == 2

    def test_no_correct_answers(self, tmp_path):
        """Test that no correct answers return accuracy of 0.0."""
        entries = [
            {
                "accuracy_metrics": {"answer": 0.0, "legal_basis": 0.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            },
            {
                "accuracy_metrics": {"answer": 0.0, "legal_basis": 0.0},
                "model_legal_basis_content": "content2",
                "model_legal_basis": "basis2",
                "model_answer": "answer2",
            },
        ]
        file_path = create_temp_jsonl(entries, tmp_path)

        result = calculate_stats(file_path)

        assert result["accuracy_metrics"]["answer"] == 0.0
        assert result["accuracy_metrics"]["legal_basis"] == 0.0
        assert result["malformed_response_rate"] == 0.0
        assert result["questions_count"] == 2

    def test_mixed_correct_answers(self, tmp_path):
        """Test mixed correct and incorrect answers."""
        entries = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 0.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            },
            {
                "accuracy_metrics": {"answer": 0.0, "legal_basis": 1.0},
                "model_legal_basis_content": "content2",
                "model_legal_basis": "basis2",
                "model_answer": "answer2",
            },
        ]
        file_path = create_temp_jsonl(entries, tmp_path)

        result = calculate_stats(file_path)

        assert result["accuracy_metrics"]["answer"] == 0.5
        assert result["accuracy_metrics"]["legal_basis"] == 0.5
        assert result["questions_count"] == 2

    def test_malformed_response_missing_model_answer(self, tmp_path):
        """Test that missing model_answer is counted as malformed."""
        entries = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 0.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "",  # Empty = malformed
            },
        ]
        file_path = create_temp_jsonl(entries, tmp_path)

        result = calculate_stats(file_path)

        assert result["malformed_response_rate"] == 1.0

    def test_malformed_response_whitespace_only(self, tmp_path):
        """Test that whitespace-only fields are counted as malformed."""
        entries = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                "model_legal_basis_content": "   ",  # Whitespace only
                "model_legal_basis": "basis",
                "model_answer": "answer",
            },
        ]
        file_path = create_temp_jsonl(entries, tmp_path)

        result = calculate_stats(file_path)

        assert result["malformed_response_rate"] == 1.0

    def test_malformed_response_missing_key(self, tmp_path):
        """Test that missing required key is counted as malformed."""
        entries = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                # model_legal_basis_content is missing
                "model_legal_basis": "basis",
                "model_answer": "answer",
            },
        ]
        file_path = create_temp_jsonl(entries, tmp_path)

        result = calculate_stats(file_path)

        assert result["malformed_response_rate"] == 1.0

    def test_text_metrics_averaging(self, tmp_path):
        """Test that text metrics are averaged correctly."""
        entries = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
                "text_metrics": {"rouge_1": 0.8, "rouge_2": 0.6},
            },
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                "model_legal_basis_content": "content2",
                "model_legal_basis": "basis2",
                "model_answer": "answer2",
                "text_metrics": {"rouge_1": 0.4, "rouge_2": 0.2},
            },
        ]
        file_path = create_temp_jsonl(entries, tmp_path)

        result = calculate_stats(file_path)

        assert result["text_metrics"]["rouge_1"] == pytest.approx(0.6)
        assert result["text_metrics"]["rouge_2"] == pytest.approx(0.4)

    def test_missing_accuracy_metrics_treated_as_false(self, tmp_path):
        """Test that missing accuracy_metrics are treated as False."""
        entries = [
            {
                # No accuracy_metrics
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            },
        ]
        file_path = create_temp_jsonl(entries, tmp_path)

        result = calculate_stats(file_path)

        assert result["accuracy_metrics"]["answer"] == 0.0
        assert result["accuracy_metrics"]["legal_basis"] == 0.0
