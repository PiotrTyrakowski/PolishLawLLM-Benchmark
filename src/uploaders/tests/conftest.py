import os
import pytest
import requests
from pathlib import Path
from google.cloud import firestore

# Point to Firebase emulator
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"

PROJECT_ID = "test-project"
EMULATOR_HOST = "localhost:8080"

# Path to test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def firestore_client():
    """Create Firestore client connected to emulator."""
    return firestore.Client(project=PROJECT_ID)


@pytest.fixture(autouse=True)
def clear_emulator():
    """Clear emulator data before each test."""
    try:
        requests.delete(
            f"http://{EMULATOR_HOST}/emulator/v1/projects/{PROJECT_ID}/databases/(default)/documents"
        )
    except requests.exceptions.ConnectionError:
        pytest.skip(
            "Firebase emulator is not running. Start it with: firebase emulators:start --only firestore"
        )
    yield


@pytest.fixture
def user1_data_path() -> Path:
    """Path to user1's test data: model_a with 2024 adwokacki_radcowy exam.

    Expected metrics after upload:
    - accuracy.answer = 2/3 = 0.6667
    - accuracy.legal_basis = 1/3 = 0.3333
    - text_metrics.exact_match = (1.0 + 0.5 + 0.0) / 3 = 0.5
    - text_metrics.bleu = (0.9 + 0.6 + 0.3) / 3 = 0.6
    """
    return TEST_DATA_DIR / "user1_upload"


@pytest.fixture
def user2_different_model_path() -> Path:
    """Path to user2's test data: model_b with 2025 notarialny exam.

    Expected metrics after upload:
    - accuracy.answer = 1.0
    - accuracy.legal_basis = 1.0
    - text_metrics.exact_match = 1.0
    - text_metrics.bleu = 1.0
    """
    return TEST_DATA_DIR / "user2_different_model"


@pytest.fixture
def user2_same_model_path() -> Path:
    """Path to user2's test data: model_a with 2025 notarialny exam (same model as user1).

    Expected metrics after upload:
    - accuracy.answer = 0.0
    - accuracy.legal_basis = 0.0
    - text_metrics.exact_match = 0.0
    - text_metrics.bleu = 0.2
    """
    return TEST_DATA_DIR / "user2_same_model"


@pytest.fixture
def multi_exam_path() -> Path:
    """Path to multi-exam test data: model_multi with multiple exams.

    Contains:
    - 2024/adwokacki_radcowy: accuracy 1.0, text_metrics 0.8
    - 2024/notarialny: accuracy 0.5, text_metrics 0.5
    - 2025/komorniczy: accuracy 0.0, text_metrics 0.2

    Expected "all" aggregate:
    - accuracy.answer = (1.0 + 0.5 + 0.0) / 3 = 0.5
    - accuracy.legal_basis = (1.0 + 0.5 + 0.0) / 3 = 0.5
    - text_metrics.exact_match = (0.8 + 0.5 + 0.2) / 3 = 0.5
    - text_metrics.bleu = (0.8 + 0.5 + 0.2) / 3 = 0.5
    """
    return TEST_DATA_DIR / "multi_exam"


@pytest.fixture
def with_judgments_path() -> Path:
    """Path to test data with both exams and judgments.

    Contains:
    - exams/2024/adwokacki_radcowy: accuracy 1.0, text_metrics 1.0
    - judgments/all.jsonl: accuracy 0.5, text_metrics ~0.7
    """
    return TEST_DATA_DIR / "with_judgments"


@pytest.fixture
def judgments_only_path() -> Path:
    """Path to test data with only judgments (no exams).

    Contains:
    - judgments/all.jsonl: accuracy 1.0, text_metrics 1.0
    """
    return TEST_DATA_DIR / "judgments_only"


# Expected metrics constants for assertions
class ExpectedMetrics:
    """Expected metrics for each test dataset."""

    # user1_upload/model_a - 2024 adwokacki_radcowy
    USER1_MODEL_A = {
        "accuracy_metrics": {
            "answer": 2 / 3,  # 0.6667
            "legal_basis": 1 / 3,  # 0.3333
        },
        "text_metrics": {
            "exact_match": 0.5,  # (1.0 + 0.5 + 0.0) / 3
            "bleu": 0.6,  # (0.9 + 0.6 + 0.3) / 3
        },
    }

    # user2_different_model/model_b - 2025 notarialny
    USER2_MODEL_B = {
        "accuracy_metrics": {
            "answer": 1.0,
            "legal_basis": 1.0,
        },
        "text_metrics": {
            "exact_match": 1.0,
            "bleu": 1.0,
        },
    }

    # user2_same_model/model_a - 2025 notarialny
    USER2_MODEL_A_2025 = {
        "accuracy_metrics": {
            "answer": 0.0,
            "legal_basis": 0.0,
        },
        "text_metrics": {
            "exact_match": 0.0,
            "bleu": 0.2,
        },
    }

    # multi_exam/model_multi "all" aggregate
    MULTI_EXAM_ALL = {
        "accuracy_metrics": {
            "answer": 0.5,  # (1.0 + 0.5 + 0.0) / 3
            "legal_basis": 0.5,  # (1.0 + 0.5 + 0.0) / 3
        },
        "text_metrics": {
            "exact_match": 0.5,  # (0.8 + 0.5 + 0.2) / 3
            "bleu": 0.5,  # (0.8 + 0.5 + 0.2) / 3
        },
    }

    # with_judgments/model_with_judgments - judgments (no "answer" key for judgments)
    JUDGMENTS = {
        "accuracy_metrics": {
            "legal_basis": 0.5,  # (1.0 + 0.0) / 2
        },
        "text_metrics": {
            "exact_match": 0.5,  # (1.0 + 0.0) / 2
            "bleu": 0.7,  # (0.9 + 0.5) / 2
        },
    }

    # judgments_only/model_judgments_only - judgments only
    JUDGMENTS_ONLY = {
        "accuracy_metrics": {
            "legal_basis": 1.0,  # (1.0 + 1.0) / 2
        },
        "text_metrics": {
            "exact_match": 1.0,  # (1.0 + 1.0) / 2
            "bleu": 1.0,  # (1.0 + 1.0) / 2
        },
    }
