import pytest

from src.benchmark_framework.stats.calculate_stats import aggregate_results


class TestAggregateResults:
    """Tests for the aggregate_results function."""

    def test_empty_results_list_returns_empty_dict(self):
        """Test that an empty results list returns an empty dictionary."""
        result = aggregate_results([])
        
        assert result == {}

    def test_single_result_aggregation(self):
        """Test aggregation with a single result."""
        results = [
            {
                "accuracy_metrics": {"answer": 0.8, "legal_basis": 0.6},
                "text_metrics": {"rouge_1": 0.7},
                "malformed_response_rate": 0.1,
                "questions_count": 10,
            }
        ]
        
        result = aggregate_results(results)
        
        assert result["accuracy_metrics"]["answer"] == pytest.approx(0.8)
        assert result["accuracy_metrics"]["legal_basis"] == pytest.approx(0.6)
        assert result["text_metrics"]["rouge_1"] == pytest.approx(0.7)
        assert result["malformed_response_rate"] == pytest.approx(0.1)

    def test_weighted_average_aggregation(self):
        """Test that aggregation uses weighted average based on question count."""
        results = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                "text_metrics": {"rouge_1": 1.0},
                "malformed_response_rate": 0.0,
                "questions_count": 10,  # Weight: 10
            },
            {
                "accuracy_metrics": {"answer": 0.0, "legal_basis": 0.0},
                "text_metrics": {"rouge_1": 0.0},
                "malformed_response_rate": 1.0,
                "questions_count": 5,  # Weight: 10
            },
        ]
        
        result = aggregate_results(results)
        
        assert result["accuracy_metrics"]["answer"] == pytest.approx(2.0 / 3.0)
        assert result["accuracy_metrics"]["legal_basis"] == pytest.approx(2.0 / 3.0)
        assert result["text_metrics"]["rouge_1"] == pytest.approx(2.0 / 3.0)
        assert result["malformed_response_rate"] == pytest.approx(1.0 / 3.0)

    def test_weighted_average_unequal_counts(self):
        """Test weighted average with unequal question counts."""
        results = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 0.8},
                "text_metrics": {},
                "malformed_response_rate": 0.0,
                "questions_count": 80,  # 80% weight
            },
            {
                "accuracy_metrics": {"answer": 0.0, "legal_basis": 0.0},
                "text_metrics": {},
                "malformed_response_rate": 1.0,
                "questions_count": 20,  # 20% weight
            },
        ]
        
        result = aggregate_results(results)
        
        # Weighted average: (1.0 * 80 + 0.0 * 20) / 100 = 0.8
        assert result["accuracy_metrics"]["answer"] == pytest.approx(0.8)
        # (0.8 * 80 + 0.0 * 20) / 100 = 0.64
        assert result["accuracy_metrics"]["legal_basis"] == pytest.approx(0.64)
        # (0.0 * 80 + 1.0 * 20) / 100 = 0.2
        assert result["malformed_response_rate"] == pytest.approx(0.2)

    def test_skips_zero_question_count_results(self):
        """Test that results with zero question count are skipped."""
        results = [
            {
                "accuracy_metrics": {"answer": 0.8, "legal_basis": 0.6},
                "text_metrics": {},
                "malformed_response_rate": 0.1,
                "questions_count": 10,
            },
            {
                "accuracy_metrics": {"answer": 0.0, "legal_basis": 0.0},
                "text_metrics": {},
                "malformed_response_rate": 1.0,
                "questions_count": 0,  # Should be skipped
            },
        ]
        
        result = aggregate_results(results)

        assert result["accuracy_metrics"]["answer"] == 0.8
        assert result["accuracy_metrics"]["legal_basis"] == 0.6

    def test_raises_error_when_all_zero_count(self):
        """Test that ValueError is raised when all results have zero question count."""
        results = [
            {"accuracy_metrics": {"answer": 0.5}, "questions_count": 0},
            {"accuracy_metrics": {"answer": 0.5}, "questions_count": 0},
        ]
        
        with pytest.raises(ValueError, match="Total questions count is zero"):
            aggregate_results(results)

    def test_aggregates_different_text_metrics(self):
        """Test aggregation of results with different text metric keys."""
        results = [
            {
                "accuracy_metrics": {"answer": 0.8, "legal_basis": 0.6},
                "text_metrics": {"rouge_1": 0.8},
                "malformed_response_rate": 0.1,
                "questions_count": 10,
            },
            {
                "accuracy_metrics": {"answer": 0.6, "legal_basis": 0.4},
                "text_metrics": {"rouge_1": 0.4, "rouge_2": 0.5},
                "malformed_response_rate": 0.2,
                "questions_count": 10,
            },
        ]
        
        result = aggregate_results(results)
        
        # rouge_1: (0.8 * 10 + 0.4 * 10) / 20 = 0.6
        assert result["text_metrics"]["rouge_1"] == pytest.approx(0.6)
        # rouge_2: (0 * 10 + 0.5 * 10) / 20 = 0.25 (only in second result)
        assert result["text_metrics"]["rouge_2"] == pytest.approx(0.25)
