import pytest
from pathlib import Path

from src.uploaders.main import Uploader
from .conftest import ExpectedMetrics


COLLECTION_ID = "test_models"


def assert_metrics_equal(actual: dict, expected: dict, tolerance: float = 0.001):
    """Assert that two metrics dicts are approximately equal."""
    for metric_type in ["accuracy_metrics", "text_metrics"]:
        if metric_type in expected:
            assert metric_type in actual, f"Missing {metric_type} in actual"
            for key, expected_value in expected[metric_type].items():
                actual_value = actual[metric_type].get(key)
                assert (
                    actual_value is not None
                ), f"Missing {metric_type}.{key} in actual"
                assert (
                    abs(actual_value - expected_value) < tolerance
                ), f"{metric_type}.{key}: expected {expected_value}, got {actual_value}"


class TestUploadCreatesDocuments:
    """Tests that upload creates correct documents in Firebase."""

    def test_upload_creates_model_document(self, firestore_client, user1_data_path):
        """Test that uploading creates a model document with correct fields."""
        uploader = Uploader(firestore_client, user1_data_path, COLLECTION_ID)
        uploader.upload()

        # Query the model document
        model_doc = firestore_client.collection(COLLECTION_ID).document("model_a").get()

        assert model_doc.exists, "Model document should exist"
        data = model_doc.to_dict()
        assert data["model_name"] == "Model A"
        assert data["is_polish"] is True
        assert data["model_config"] == {}

    def test_upload_creates_exam_document(self, firestore_client, user1_data_path):
        """Test that uploading creates exam documents with correct structure."""
        uploader = Uploader(firestore_client, user1_data_path, COLLECTION_ID)
        uploader.upload()

        # Query the exam document
        exam_doc = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_a")
            .collection("exams")
            .document("adwokacki_radcowy_2024")
            .get()
        )

        assert exam_doc.exists, "Exam document should exist"
        data = exam_doc.to_dict()
        assert data["type"] == "adwokacki_radcowy"
        assert data["year"] == 2024
        assert "accuracy_metrics" in data
        assert "text_metrics" in data

    def test_upload_creates_all_aggregate_document(
        self, firestore_client, user1_data_path
    ):
        """Test that uploading creates the 'all' aggregate document."""
        uploader = Uploader(firestore_client, user1_data_path, COLLECTION_ID)
        uploader.upload()

        # Query the "all" document
        all_doc = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_a")
            .collection("exams")
            .document("all")
            .get()
        )

        assert all_doc.exists, "'all' aggregate document should exist"
        data = all_doc.to_dict()
        assert data["type"] == "all"
        assert data["year"] == "all"


class TestMetricsCalculation:
    """Tests that metrics are calculated correctly."""

    def test_accuracy_metrics_calculated_correctly(
        self, firestore_client, user1_data_path
    ):
        """Test that accuracy metrics are calculated correctly from JSONL data."""
        uploader = Uploader(firestore_client, user1_data_path, COLLECTION_ID)
        uploader.upload()

        exam_doc = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_a")
            .collection("exams")
            .document("adwokacki_radcowy_2024")
            .get()
        )

        data = exam_doc.to_dict()
        expected = ExpectedMetrics.USER1_MODEL_A

        # Check accuracy metrics
        assert (
            abs(
                data["accuracy_metrics"]["answer"]
                - expected["accuracy_metrics"]["answer"]
            )
            < 0.001
        )
        assert (
            abs(
                data["accuracy_metrics"]["legal_basis"]
                - expected["accuracy_metrics"]["legal_basis"]
            )
            < 0.001
        )

    def test_text_metrics_averaged_correctly(self, firestore_client, user1_data_path):
        """Test that text metrics are averaged correctly from JSONL data."""
        uploader = Uploader(firestore_client, user1_data_path, COLLECTION_ID)
        uploader.upload()

        exam_doc = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_a")
            .collection("exams")
            .document("adwokacki_radcowy_2024")
            .get()
        )

        data = exam_doc.to_dict()
        expected = ExpectedMetrics.USER1_MODEL_A

        # Check text metrics
        assert (
            abs(
                data["text_metrics"]["exact_match"]
                - expected["text_metrics"]["exact_match"]
            )
            < 0.001
        )
        assert (
            abs(data["text_metrics"]["bleu"] - expected["text_metrics"]["bleu"]) < 0.001
        )

    def test_all_aggregate_averages_multiple_exams(
        self, firestore_client, multi_exam_path
    ):
        """Test that 'all' aggregate correctly averages multiple exam documents."""
        uploader = Uploader(firestore_client, multi_exam_path, COLLECTION_ID)
        uploader.upload()

        all_doc = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_multi")
            .collection("exams")
            .document("all")
            .get()
        )

        data = all_doc.to_dict()
        expected = ExpectedMetrics.MULTI_EXAM_ALL

        assert_metrics_equal(data, expected)


class TestMultiUserUpload:
    """Tests for multi-user upload scenarios."""

    def test_upload_different_models_coexist(
        self, firestore_client, user1_data_path, user2_different_model_path
    ):
        """Test that two users uploading different models don't interfere."""
        # User 1 uploads model_a
        uploader1 = Uploader(firestore_client, user1_data_path, COLLECTION_ID)
        uploader1.upload()

        # User 2 uploads model_b
        uploader2 = Uploader(
            firestore_client, user2_different_model_path, COLLECTION_ID
        )
        uploader2.upload()

        # Verify both models exist
        model_a = firestore_client.collection(COLLECTION_ID).document("model_a").get()
        model_b = firestore_client.collection(COLLECTION_ID).document("model_b").get()

        assert model_a.exists, "Model A should exist"
        assert model_b.exists, "Model B should exist"

        # Verify model_a data is intact
        assert model_a.to_dict()["model_name"] == "Model A"
        assert model_a.to_dict()["is_polish"] is True

        # Verify model_b has its own data
        assert model_b.to_dict()["model_name"] == "Model B"
        assert model_b.to_dict()["is_polish"] is False

    def test_upload_same_model_different_exams_both_exist(
        self, firestore_client, user1_data_path, user2_same_model_path
    ):
        """Test that uploading same model with different exams keeps both exams."""
        # User 1 uploads model_a with 2024 exams
        uploader1 = Uploader(firestore_client, user1_data_path, COLLECTION_ID)
        uploader1.upload()

        # User 2 uploads model_a with 2025 exams
        uploader2 = Uploader(firestore_client, user2_same_model_path, COLLECTION_ID)
        uploader2.upload()

        # Verify both exam documents exist
        exam_2024 = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_a")
            .collection("exams")
            .document("adwokacki_radcowy_2024")
            .get()
        )
        exam_2025 = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_a")
            .collection("exams")
            .document("notarialny_2025")
            .get()
        )

        assert exam_2024.exists, "2024 exam should still exist"
        assert exam_2025.exists, "2025 exam should exist"

    def test_upload_same_model_different_exams_updates_all_aggregate(
        self, firestore_client, user1_data_path, user2_same_model_path
    ):
        """Test that 'all' aggregate is recalculated after second upload with weighted averaging."""
        # User 1 uploads model_a with 2024 exams
        uploader1 = Uploader(firestore_client, user1_data_path, COLLECTION_ID)
        uploader1.upload()

        # Check initial "all" metrics (should be just 2024 exam)
        all_doc_initial = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_a")
            .collection("exams")
            .document("all")
            .get()
        )

        # User 2 uploads model_a with 2025 exams
        uploader2 = Uploader(firestore_client, user2_same_model_path, COLLECTION_ID)
        uploader2.upload()

        # Check updated "all" metrics (should now be weighted average of both exams)
        all_doc_updated = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_a")
            .collection("exams")
            .document("all")
            .get()
        )
        updated_data = all_doc_updated.to_dict()

        # The "all" metrics should be weighted average after second upload
        # 2024: 3 questions, accuracy.answer = 2/3
        # 2025: 2 questions, accuracy.answer = 0.0
        # Weighted average: (2/3 * 3 + 0 * 2) / 5 = 2/5 = 0.4
        expected_combined_answer = (2 / 3 * 3 + 0.0 * 2) / 5
        assert (
            abs(updated_data["accuracy_metrics"]["answer"] - expected_combined_answer)
            < 0.001
        )

        # 2024: 3 questions, bleu = 0.6
        # 2025: 2 questions, bleu = 0.2
        # Weighted average: (0.6 * 3 + 0.2 * 2) / 5 = 2.2/5 = 0.44
        expected_combined_bleu = (0.6 * 3 + 0.2 * 2) / 5
        assert (
            abs(updated_data["text_metrics"]["bleu"] - expected_combined_bleu) < 0.001
        )

        # Check questions_count is sum of both exams
        assert updated_data["questions_count"] == 5


class TestJudgments:
    """Tests for judgment document handling."""

    def test_upload_creates_judgment_document(
        self, firestore_client, with_judgments_path
    ):
        """Test that judgments are uploaded correctly."""
        uploader = Uploader(firestore_client, with_judgments_path, COLLECTION_ID)
        uploader.upload()

        judgment_doc = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_with_judgments")
            .collection("judgments")
            .document("all")
            .get()
        )

        assert judgment_doc.exists, "Judgment document should exist"
        data = judgment_doc.to_dict()
        assert "accuracy_metrics" in data
        assert "text_metrics" in data

    def test_upload_judgments_only_model(self, firestore_client, judgments_only_path):
        """Test that a model with only judgments (no exams) uploads correctly."""
        uploader = Uploader(firestore_client, judgments_only_path, COLLECTION_ID)
        uploader.upload()

        # Model document should exist
        model_doc = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_judgments_only")
            .get()
        )
        assert model_doc.exists, "Model document should exist"

        # Judgment document should exist
        judgment_doc = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_judgments_only")
            .collection("judgments")
            .document("all")
            .get()
        )
        assert judgment_doc.exists, "Judgment document should exist"

    def test_upload_with_both_exams_and_judgments(
        self, firestore_client, with_judgments_path
    ):
        """Test that both exams and judgments are uploaded for the same model."""
        uploader = Uploader(firestore_client, with_judgments_path, COLLECTION_ID)
        uploader.upload()

        # Exam should exist
        exam_doc = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_with_judgments")
            .collection("exams")
            .document("adwokacki_radcowy_2024")
            .get()
        )
        assert exam_doc.exists, "Exam document should exist"

        # Judgment should exist
        judgment_doc = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_with_judgments")
            .collection("judgments")
            .document("all")
            .get()
        )
        assert judgment_doc.exists, "Judgment document should exist"

        # "all" exam aggregate should exist
        all_doc = (
            firestore_client.collection(COLLECTION_ID)
            .document("model_with_judgments")
            .collection("exams")
            .document("all")
            .get()
        )
        assert all_doc.exists, "'all' aggregate should exist"


class TestValidation:
    """Tests for input validation."""

    def test_invalid_path_raises_file_not_found(self, firestore_client):
        """Test that non-existent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            Uploader(firestore_client, Path("/non/existent/path"), COLLECTION_ID)

    def test_file_path_raises_not_a_directory(self, firestore_client, user1_data_path):
        """Test that file path (not directory) raises NotADirectoryError."""
        file_path = user1_data_path / "model_a" / "model_fields.json"
        with pytest.raises(NotADirectoryError):
            Uploader(firestore_client, file_path, COLLECTION_ID)


class TestAverageMetricsStatic:
    """Tests for the static _average_metrics method."""

    def test_average_metrics_empty_list(self):
        """Test that empty list returns empty dicts with zero questions_count."""
        result = Uploader._average_metrics([])
        assert result == {"accuracy_metrics": {}, "text_metrics": {}, "questions_count": 0}

    def test_average_metrics_single_doc(self):
        """Test that single doc returns same values."""
        docs = [
            {
                "accuracy_metrics": {"answer": 0.8, "legal_basis": 0.6},
                "text_metrics": {"bleu": 0.7, "exact_match": 0.5},
                "questions_count": 10,
            }
        ]
        result = Uploader._average_metrics(docs)

        assert abs(result["accuracy_metrics"]["answer"] - 0.8) < 0.001
        assert abs(result["accuracy_metrics"]["legal_basis"] - 0.6) < 0.001
        assert abs(result["text_metrics"]["bleu"] - 0.7) < 0.001
        assert abs(result["text_metrics"]["exact_match"] - 0.5) < 0.001
        assert result["questions_count"] == 10

    def test_average_metrics_multiple_docs(self):
        """Test that multiple docs with equal weights are averaged correctly."""
        docs = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                "text_metrics": {"bleu": 0.8},
                "questions_count": 1,
            },
            {
                "accuracy_metrics": {"answer": 0.0, "legal_basis": 0.0},
                "text_metrics": {"bleu": 0.2},
                "questions_count": 1,
            },
        ]
        result = Uploader._average_metrics(docs)

        assert abs(result["accuracy_metrics"]["answer"] - 0.5) < 0.001
        assert abs(result["accuracy_metrics"]["legal_basis"] - 0.5) < 0.001
        assert abs(result["text_metrics"]["bleu"] - 0.5) < 0.001
        assert result["questions_count"] == 2

    def test_average_metrics_dynamic_keys(self):
        """Test that varying metric keys are handled correctly with weighted averaging."""
        docs = [
            {
                "accuracy_metrics": {"answer": 1.0},
                "text_metrics": {"bleu": 0.8, "rouge": 0.9},
                "questions_count": 1,
            },
            {
                "accuracy_metrics": {"answer": 0.5, "legal_basis": 0.5},
                "text_metrics": {"bleu": 0.4},
                "questions_count": 1,
            },
        ]
        result = Uploader._average_metrics(docs)

        # "answer" appears in both docs: (1.0 * 1 + 0.5 * 1) / 2 = 0.75
        assert abs(result["accuracy_metrics"]["answer"] - 0.75) < 0.001
        # "legal_basis" only in second doc: 0.5 * 1 / 2 = 0.25
        assert abs(result["accuracy_metrics"]["legal_basis"] - 0.25) < 0.001
        # "bleu" appears in both docs: (0.8 * 1 + 0.4 * 1) / 2 = 0.6
        assert abs(result["text_metrics"]["bleu"] - 0.6) < 0.001
        # "rouge" only in first doc: 0.9 * 1 / 2 = 0.45
        assert abs(result["text_metrics"]["rouge"] - 0.45) < 0.001
        # Total questions_count
        assert result["questions_count"] == 2

    def test_average_metrics_weighted_by_questions_count(self):
        """Test that metrics are weighted by questions_count."""
        docs = [
            {
                "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
                "text_metrics": {"bleu": 0.8},
                "questions_count": 80,  # 80 questions
            },
            {
                "accuracy_metrics": {"answer": 0.0, "legal_basis": 0.0},
                "text_metrics": {"bleu": 0.0},
                "questions_count": 20,  # 20 questions
            },
        ]
        result = Uploader._average_metrics(docs)

        # Weighted average: (1.0 * 80 + 0.0 * 20) / 100 = 0.8
        assert abs(result["accuracy_metrics"]["answer"] - 0.8) < 0.001
        assert abs(result["accuracy_metrics"]["legal_basis"] - 0.8) < 0.001
        # (0.8 * 80 + 0.0 * 20) / 100 = 0.64
        assert abs(result["text_metrics"]["bleu"] - 0.64) < 0.001
        assert result["questions_count"] == 100

    def test_average_metrics_missing_questions_count_raises_error(self):
        """Test that missing questions_count raises ValueError."""
        docs = [
            {
                "accuracy_metrics": {"answer": 1.0},
                "text_metrics": {"bleu": 1.0},
                # No questions_count - should raise error
            },
        ]
        with pytest.raises(ValueError, match="questions_count"):
            Uploader._average_metrics(docs)
