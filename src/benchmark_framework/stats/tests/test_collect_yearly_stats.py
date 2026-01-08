import pytest
from pathlib import Path

from src.benchmark_framework.stats.calculate_stats import collect_yearly_stats
from src.benchmark_framework.stats.tests.conftest import create_temp_jsonl


class TestCollectYearlyStats:
    """Tests for the collect_yearly_stats function."""

    def test_raises_error_for_non_directory(self, tmp_path):
        """Test that ValueError is raised for non-directory paths."""
        file_path = tmp_path / "file.txt"
        file_path.touch()

        with pytest.raises(ValueError, match="is not a directory"):
            collect_yearly_stats(file_path)

    def test_raises_error_when_no_year_directories(self, tmp_path):
        """Test that ValueError is raised when no year directories exist."""
        # Create non-year directories
        (tmp_path / "not_a_year").mkdir()
        (tmp_path / "abc").mkdir()

        with pytest.raises(ValueError, match="No year directories found"):
            collect_yearly_stats(tmp_path)

    def test_collects_stats_for_single_year(self, tmp_path):
        """Test collecting stats for a single year directory."""
        year_dir = tmp_path / "2023"
        year_dir.mkdir()

        entries = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            }
        ]
        create_temp_jsonl(entries, year_dir, "test.jsonl")

        result = collect_yearly_stats(tmp_path)

        assert "2023" in result
        assert result["2023"]["accuracy_metrics"]["answer"] == 1.0

    def test_collects_stats_for_multiple_years(self, tmp_path):
        """Test collecting stats for multiple year directories."""
        for year in ["2021", "2022", "2023"]:
            year_dir = tmp_path / year
            year_dir.mkdir()
            entries = [
                {
                    "accuracy_metrics": {"answer": 1.0, "legal_basis": 0.0},
                    "model_legal_basis_content": "content",
                    "model_legal_basis": "basis",
                    "model_answer": "answer",
                }
            ]
            create_temp_jsonl(entries, year_dir, "test.jsonl")

        result = collect_yearly_stats(tmp_path)

        assert len(result) == 3
        assert "2021" in result
        assert "2022" in result
        assert "2023" in result

    def test_skips_year_directories_without_jsonl_files(self, tmp_path):
        """Test that year directories without JSONL files are skipped."""
        (tmp_path / "2021").mkdir()  # No files

        year_dir = tmp_path / "2022"
        year_dir.mkdir()
        entries = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 0.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            }
        ]
        create_temp_jsonl(entries, year_dir, "test.jsonl")

        result = collect_yearly_stats(tmp_path)

        assert "2021" not in result
        assert "2022" in result

    def test_aggregates_multiple_files_per_year(self, tmp_path):
        """Test aggregation of multiple JSONL files in a single year."""
        year_dir = tmp_path / "2023"
        year_dir.mkdir()

        # First file: all correct
        entries1 = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            }
        ]
        create_temp_jsonl(entries1, year_dir, "test1.jsonl")

        # Second file: none correct
        entries2 = [
            {
                "accuracy_metrics": {"answer": 0.0, "legal_basis": 0.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            }
        ]
        create_temp_jsonl(entries2, year_dir, "test2.jsonl")

        result = collect_yearly_stats(tmp_path)

        # Should be weighted average: 0.5
        assert result["2023"]["accuracy_metrics"]["answer"] == pytest.approx(0.5)

    def test_ignores_non_numeric_directories(self, tmp_path):
        """Test that non-numeric directories are ignored."""
        (tmp_path / "not_a_year").mkdir()
        (tmp_path / "2023abc").mkdir()

        year_dir = tmp_path / "2023"
        year_dir.mkdir()
        entries = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                "model_legal_basis_content": "content",
                "model_legal_basis": "basis",
                "model_answer": "answer",
            }
        ]
        create_temp_jsonl(entries, year_dir, "test.jsonl")

        result = collect_yearly_stats(tmp_path)

        assert len(result) == 1
        assert "2023" in result
