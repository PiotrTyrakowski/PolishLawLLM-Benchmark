# Polish Law Exam Parser

This tool extracts exam questions, answers, and legal basis content from PDF files and outputs them in a structured JSONL format suitable for LLM benchmarking.

## Features

- **PDF Parsing**: Extracts questions and answers from exam PDFs using specialized readers
- **Legal Basis Extraction**: Retrieves relevant legal code content from pre-generated corpus files
- **Structured Output**: Generates JSONL files ready for LLM benchmarking
- **Multiple Exam Types**: Supports adwokacki/radcowy, komorniczy, and notarialny exams
- **Multi-Year Support**: Processes exams from multiple years in a single run
- **Year Filtering**: Optional `--year` flag to process specific years only

## Architecture

```
parsers/
├── cli.py                      # Main CLI for parsing exams into JSONL
├── corpuses/                   # Corpus generation module
│   ├── setup_corpuses.py       # CLI for generating corpus files from legal PDFs
│   └── corpuses_config.py      # Configuration: start pages, article filters
├── domain/                     # Domain models
│   ├── question.py             # Question dataclass
│   ├── answer.py               # Answer dataclass
│   └── legal_reference.py      # LegalReference dataclass (article, paragraph, point, code)
├── extractors/                 # Text extraction logic (regex-based)
│   ├── base_extractor.py       # Abstract base extractor
│   ├── question_extractor.py   # Extracts questions from PDF text
│   ├── answer_extractor.py     # Extracts answers from PDF tables
│   ├── legal_reference_extractor.py  # Parses legal basis strings (e.g., "art. 6 § 2 k.k.")
│   ├── legal_content_extractor.py    # Extracts articles/paragraphs/points from corpus
│   └── regex_patterns.py       # Shared regex patterns
├── parsers/                    # PDF parsing orchestration
│   ├── parser.py               # Generic Parser class combining reader + extractor
│   └── getters.py              # Factory functions for parser configurations
├── pdf_readers/                # PDF text extraction
│   ├── base_pdf_reader.py      # Abstract base reader
│   ├── pdf_text_reader.py      # Simple text extraction (for questions)
│   ├── pdf_table_reader.py     # Table extraction using pdfplumber (for answers)
│   └── pdf_legal_text_reader.py # Specialized reader for legal codes
├── services/                   # Business logic
│   ├── exam_service.py         # Orchestrates exam parsing workflow
│   └── legal_basis_service.py  # Loads corpuses and enriches questions with legal content
└── utils/
    └── discover_exams.py       # Auto-discovers exam files by year and type
```

## Installation

```bash
pip install -r requirements.txt
```

## Workflow Overview

The task generation process consists of two steps:

1. **Generate Corpuses**: Extract articles from legal base PDFs into JSON corpus files
2. **Parse Exams**: Process exam PDFs and enrich with legal content from corpuses

---

## Step 1: Generate Corpuses

Before parsing exams, generate corpus files from the legal base PDFs.

### Command

```bash
python -m src.parsers.corpuses.setup_corpuses <input-directory> <output-directory> <year>
```

### Arguments

| Argument | Description |
|----------|-------------|
| `input-directory` | Directory containing legal code PDFs (e.g., `kc.pdf`, `kk.pdf`) |
| `output-directory` | Directory where JSON corpus files will be saved |
| `year` | Year of the legal codes (used for configuration lookup) |

### Example

```bash
# Generate corpus for year 2025
python -m src.parsers.corpuses.setup_corpuses data/pdfs/2025/legal_base data/corpuses/2025 2025
```

### Legal Base PDF Directory Structure

```
pdfs/2025/legal_base/
├── kc.pdf          # Kodeks cywilny
├── kk.pdf          # Kodeks karny
├── kks.pdf         # Kodeks karny skarbowy
├── kp.pdf          # Kodeks pracy
├── kpa.pdf         # Kodeks postępowania administracyjnego
├── kpc.pdf         # Kodeks postępowania cywilnego
├── kpk.pdf         # Kodeks postępowania karnego
├── kpsw.pdf        # Kodeks postępowania w sprawach o wykroczenia
├── krio.pdf        # Kodeks rodzinny i opiekuńczy
├── ksh.pdf         # Kodeks spółek handlowych
└── kw.pdf          # Kodeks wykroczeń
```

### Output Corpus Structure

```
corpuses/
├── 2024/
│   ├── kc.json
│   ├── kk.json
│   └── ... (one JSON file per legal code)
└── 2025/
    └── ... (same structure)
```

Each JSON file is a dictionary mapping article numbers to their full text content.

### Configuration

The `corpuses_config.py` file contains:
- **START_PAGE**: Per-year, per-code start page configuration (skips table of contents, etc.)
- **SKIP_ARTICLES**: Articles to exclude from specific codes (per year)
- **should_skip_article()**: Function to determine if an article should be filtered

---

## Step 2: Parse Exams

After generating corpuses, parse the exam PDFs.

### Command

```bash
python -m src.parsers.cli <pdfs-directory> <corpuses-directory> [output-directory] [--year YEAR]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `pdfs-directory` | Path to directory containing exam PDFs (organized by year) |
| `corpuses-directory` | Path to corpuses directory (containing year subdirectories with JSON files) |
| `output-directory` | Optional. Output path for JSONL files (default: `data/tasks/exams`) |
| `--year`, `-y` | Optional. Process only exams from a specific year (e.g., `2024`) |

### Examples

```bash
# Parse all years
python -m src.parsers.cli data/pdfs/ data/corpuses/ data/tasks/exams

# Parse only 2025 exams
python -m src.parsers.cli data/pdfs/ data/corpuses/ data/tasks/exams --year 2025
```

---

## Input Directory Structures

### Exam PDFs Directory

```
pdfs/
├── 2024/
│   ├── legal_base/
│   │   └── [legal code PDFs]
│   ├── Zestaw_pytań_testowych_..._2024.pdf         # Questions PDF
│   └── Wykaz_prawidłowych_odpowiedzi_..._2024.pdf  # Answers PDF
└── 2025/
    ├── legal_base/
    │   └── [legal code PDFs]
    ├── Zestaw_pytań_testowych_..._2025.pdf
    └── Wykaz_prawidłowych_odpowiedzi_..._2025.pdf
```

### Required Files per Year

For each year directory, you need:

1. **Questions PDF**: Filename must start with `Zestaw`
2. **Answers PDF**: Filename must start with `Wykaz`

The exam type is auto-detected from filename keywords:
- `adwokack` or `radcow` → `adwokacki_radcowy`
- `komornic` → `komorniczy`
- `notarialn` → `notarialny`

---

## Output Format

### Directory Structure

```
data/tasks/exams/
├── 2024/
│   └── adwokacki_radcowy.jsonl
└── 2025/
    └── adwokacki_radcowy.jsonl
```

### JSONL Format

Each line in the output JSONL file represents one exam question:

```json
{
  "id": 1,
  "year": 2025,
  "exam_type": "adwokacki_radcowy",
  "question": "Zgodnie z Kodeksem karnym, czyn zabroniony uważa się za popełniony w miejscu, w którym:",
  "choices": {
    "A": "sprawca działał lub zaniechał działania, do którego był obowiązany...",
    "B": "ujawniono czyn zabroniony,",
    "C": "zatrzymano sprawcę czynu zabronionego."
  },
  "answer": "A",
  "legal_basis": "art. 6 § 2 k.k.",
  "legal_basis_content": "Czyn zabroniony uważa się za popełniony w miejscu..."
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Question number (1-indexed) |
| `year` | int | Year of the exam |
| `exam_type` | string | Type of exam (adwokacki_radcowy, komorniczy, notarialny) |
| `question` | string | The question text |
| `choices` | object | Multiple choice options with keys "A", "B", "C" |
| `answer` | string | The correct answer option ("A", "B", or "C") |
| `legal_basis` | string | Legal reference (e.g., "art. 6 § 2 k.k.") |
| `legal_basis_content` | string | Full text of the referenced legal article/paragraph/point |

---

## Domain Models

### Question
Represents a parsed exam question with ID, text, and three options (A, B, C).

### Answer
Contains the question ID, correct answer letter, and legal basis reference string.

### LegalReference
Structured representation of a legal reference:
- `article`: Article number (e.g., "6")
- `paragraph`: Optional paragraph (e.g., "2")
- `point`: Optional point number
- `code`: Code abbreviation (e.g., "k.k.")

### ExamQuestion
The enriched output model combining question, answer, and legal content.

---

## Testing

```bash
python -m pytest src/parsers/
```

Test directories are located in:
- `src/parsers/extractors/tests/`
- `src/parsers/parsers/tests/`
