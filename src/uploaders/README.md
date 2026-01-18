# Results Uploader

This tool uploads benchmark results to Firebase Firestore, making them available for the leaderboard and analysis.

## Features

- **Firebase Integration**: Uploads benchmark results directly to Firestore
- **Exam Results**: Supports multiple exam types (adwokacki_radcowy, komorniczy, notarialny)
- **Judgment Results**: Supports legal judgment benchmark results
- **Automatic Aggregation**: Creates an "all" aggregate document with weighted average metrics across all exams
- **Multi-Year Support**: Handles results from multiple years per model

## Architecture

```
uploaders/
├── cli.py                      # CLI interface using Typer
├── main.py                     # Uploader class with core logic
└── tests/
    ├── conftest.py             # Test fixtures and Firebase emulator setup
    ├── test_uploader.py        # Test cases
    └── test_data/              # Test fixture data
        ├── user1_upload/
        ├── user2_different_model/
        ├── user2_same_model/
        ├── multi_exam/
        ├── with_judgments/
        └── judgments_only/
```

## Installation

Ensure Firebase dependencies are installed:

```bash
pip install -r requirements.txt
```

## Usage

### Command

```bash
python -m src.uploaders.cli [OPTIONS]
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--path` | `-p` | Path to the results directory | `data/results_with_metrics` |
| `--collection` | `-c` | Firestore collection name | `results` |
| `--verbose` | `-v` | Enable debug logging | `False` |

### Examples

```bash
# Upload with default settings 
python -m src.uploaders.cli

# Upload from custom path
python -m src.uploaders.cli --path data/my_results

# Upload to custom collection name with verbose logging
python -m src.uploaders.cli --collection test_results --verbose
```

---

## Input Directory Structure

The uploader expects the following file structure:

```
data/results_with_metrics/
└── {model_id}/
    ├── model_fields.json       # Required: Model metadata
    ├── exams/                   # Optional: Exam results
    │   └── {year}/
    │       └── {exam_type}.jsonl
    └── judgments/               # Optional: Judgment results
        └── all.jsonl
```

### Required Files

Each model directory must contain exactly one JSON file with model metadata.

### Exam Types

Valid exam types are:
- `adwokacki_radcowy`
- `komorniczy`
- `notarialny`

---

## File Formats

### model_fields.json

```json
{
  "model_name": "Gemini 3 Pro Preview",
  "is_polish": false,
  "model_config": {
    "google_search": false
  }
}

```

| Field | Type | Description |
|-------|------|-------------|
| `model_name` | string | Display name for the model |
| `is_polish` | boolean | Whether the model is Polish-specific |
| `model_config` | object | Optional model configuration parameters |

### Exam JSONL Format

Each line in the exam JSONL file represents one question with model response and metrics:

```json
{
  "id": 1,
  "year": 2025,
  "exam_type": "adwokacki_radcowy",
  "question": "Zgodnie z Kodeksem karnym, czyn zabroniony uważa się za popełniony w miejscu, w którym:",
  "choices": {"A": "sprawca działał lub zaniechał działania...", "B": "...", "C": "..."},
  "correct_answer": "A",
  "legal_basis": "art. 6 § 2 k.k.",
  "legal_basis_content": "Czyn zabroniony uważa się za popełniony w miejscu...",
  "model_name": "gemini-3-pro-preview",
  "model_config": "{...}",
  "model_answer": "A",
  "model_legal_basis": "art. 6 § 2 k.k.",
  "model_legal_basis_content": "Czyn zabroniony uważa się za popełniony w miejscu...",
  "accuracy_metrics": {"answer": 1.0, "legal_basis": 1.0},
  "text_metrics": {"exact_match": 1.0, "rouge_n_f1": 1.0, "rouge_n_tfidf": 1.0, "rouge_w": 1.0}
}
```

### Judgment JSONL Format

Each line represents a legal judgment with model response and metrics (no `answer` field):

```json
{
  "id": 39,
  "judgment_link": "https://orzeczenia.lublin.sa.gov.pl/content/...",
  "date": "18-12-2025",
  "legal_basis": "art. 385^1 k.c.",
  "legal_basis_content": "§ 1. Postanowienia umowy zawieranej z konsumentem...",
  "model_name": "gemini-3-pro-preview",
  "model_config": "{...}",
  "model_legal_basis": "art. 385^1 k.c.",
  "model_legal_basis_content": "§ 1. Postanowienia umowy zawieranej z konsumentem...",
  "accuracy_metrics": {"legal_basis": 1.0},
  "text_metrics": {"exact_match": 1.0, "rouge_n_f1": 1.0, "rouge_n_tfidf": 1.0, "rouge_w": 1.0}
}
```

---

## Firestore Document Structure

After upload, data is organized in Firestore as:

```
{collection}/
└── {model_id}/                 # ModelDocument
    ├── model_name
    ├── is_polish
    ├── model_config
    ├── exams/                  # Subcollection
    │   ├── {exam_type}_{year}  # ExamDocument
    │   │   ├── type
    │   │   ├── year
    │   │   ├── questions_count
    │   │   ├── accuracy_metrics
    │   │   └── text_metrics
    │   └── all                 # Aggregate document
    │       ├── type: "all"
    │       ├── year: "all"
    │       ├── questions_count
    │       ├── accuracy_metrics (weighted avg)
    │       └── text_metrics (weighted avg)
    └── judgments/              # Subcollection
        └── all                 # JudgmentDocument
            ├── accuracy_metrics
            └── text_metrics
```

### Aggregate Document

The "all" document is automatically created/updated after each upload. It contains weighted averages of all exam metrics, where weights are the `questions_count` for each exam.

---

## Testing

Tests use the Firebase Emulator to avoid affecting production data.

### Prerequisites

1. Install Firebase CLI:
   ```bash
   npm install -g firebase-tools
   ```

2. Start the Firestore emulator:
   ```bash
   firebase emulators:start --only firestore
   ```

### Running Tests

```bash
# Run all uploader tests
python -m pytest src/uploaders/tests/

# Run with verbose output
python -m pytest src/uploaders/tests/ -v

# Run specific test class
python -m pytest src/uploaders/tests/test_uploader.py::TestUploadCreatesDocuments -v
```

### Test Categories

| Test Class | Description |
|------------|-------------|
| `TestUploadCreatesDocuments` | Verifies model, exam, and aggregate documents are created |
| `TestMetricsCalculation` | Validates accuracy and text metrics calculations |
| `TestMultiUserUpload` | Tests concurrent uploads from different users |
| `TestJudgments` | Tests judgment document handling |
| `TestValidation` | Tests input validation and error handling |
| `TestAverageMetricsStatic` | Unit tests for weighted averaging logic |

### Test Data

Test fixtures are located in `tests/test_data/` with various scenarios:
- `user1_upload/` - Basic model with one exam
- `user2_different_model/` - Different model upload
- `user2_same_model/` - Same model, different exam (tests merging)
- `multi_exam/` - Model with multiple exams (tests aggregation)
- `with_judgments/` - Model with both exams and judgments
- `judgments_only/` - Model with only judgment results
