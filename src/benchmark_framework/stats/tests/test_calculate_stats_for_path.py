import pytest

from src.benchmark_framework.stats.calculate_stats import calculate_stats_for_path
from src.benchmark_framework.stats.tests.conftest import create_temp_jsonl


class TestCalculateStatsForPath:
    """Tests for the calculate_stats_for_path function."""

    def test_single_file_returns_stats(self, tmp_path):
        """Test that a single file returns its stats directly."""
        entries = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            }
        ]
        file_path = create_temp_jsonl(entries, tmp_path)

        result = calculate_stats_for_path(file_path)

        assert result["accuracy_metrics"]["answer"] == 1.0
        assert result["questions_count"] == 1

    def test_directory_with_single_file(self, tmp_path):
        """Test that a directory with a single file returns its stats."""
        entries = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 0.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            }
        ]
        create_temp_jsonl(entries, tmp_path)

        result = calculate_stats_for_path(tmp_path)

        assert result["accuracy_metrics"]["answer"] == 1.0
        assert result["accuracy_metrics"]["legal_basis"] == 0.0

    def test_directory_with_multiple_files_aggregates(self, tmp_path):
        """Test that a directory with multiple files returns aggregated stats."""
        # First file
        entries1 = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            }
        ]
        create_temp_jsonl(entries1, tmp_path, "file1.jsonl")

        # Second file
        entries2 = [
            {
                "accuracy_metrics": {"answer": 0.0, "legal_basis": 0.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            }
        ]
        create_temp_jsonl(entries2, tmp_path, "file2.jsonl")

        result = calculate_stats_for_path(tmp_path)

        assert result["accuracy_metrics"]["answer"] == pytest.approx(0.5)

    def test_directory_with_nested_files(self, tmp_path):
        """Test that nested JSONL files are found recursively."""
        nested_dir = tmp_path / "nested" / "deep"
        nested_dir.mkdir(parents=True)

        entries = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            }
        ]
        create_temp_jsonl(entries, nested_dir, "nested.jsonl")

        entries2 = [
            {
                "accuracy_metrics": {"answer": 0.0, "legal_basis": 0.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            }
        ]
        create_temp_jsonl(entries2, tmp_path, "file2.jsonl")

        result = calculate_stats_for_path(tmp_path)

        assert result["accuracy_metrics"]["answer"] == 0.5

    def test_raises_error_for_empty_directory(self, tmp_path):
        """Test that ValueError is raised for directory without JSONL files."""
        with pytest.raises(ValueError, match="No .jsonl files found"):
            calculate_stats_for_path(tmp_path)

    def test_raises_error_for_invalid_path(self, tmp_path):
        """Test that ValueError is raised for non-existent path."""
        non_existent = tmp_path / "does_not_exist"

        with pytest.raises(ValueError, match="Invalid path"):
            calculate_stats_for_path(non_existent)

    def test_raises_error_when_no_valid_results(self, tmp_path):
        """Test that ValueError is raised when all files fail to process."""
        # Create an invalid JSONL file
        file_path = tmp_path / "invalid.jsonl"
        with open(file_path, "w") as f:
            f.write("not valid json\n")

        with pytest.raises(ValueError, match="No valid results computed"):
            calculate_stats_for_path(tmp_path)
