# Polish Law Exam Parser

This tool extracts exam questions, answers, and legal basis content from PDF files and outputs them in a structured JSONL format suitable for the benchmark.

## Features

- 📄 **PDF Parsing**: Extracts questions and answers from exam PDFs
- ⚖️ **Legal Basis Extraction**: Automatically retrieves relevant legal code content (articles, paragraphs, points)
- 📊 **Structured Output**: Generates JSONL files ready for LLM benchmarking
- 🔍 **Multiple Exam Types**: Supports adwokacki/radcowy, komorniczy, and notarialny exams
- 📁 **Multi-Year Support**: Processes exams from multiple years in a single run

## Architecture

```
parsers/
├── cli.py                  # Command-line interface
├── domain/                 # Domain models (Question, Answer, Exam, etc.)
├── extractors/            # Text extraction logic (regex-based)
├── parsers/               # PDF parsing logic
├── services/              # Business logic orchestration
├── repositories/          # Data persistence (JSONL)
└── utils/                 # Utility functions
```

## Installation

Ensure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Command

```bash
python -m parsers.cli parse <path-to-pdfs-directory>
```

### Example

```bash
python -m parsers.cli parse pdfs/
```

## Input Directory Structure

The parser expects a specific directory structure with year-based subdirectories:

```
pdfs/
├── 2024/
│   ├── legal_base/
│   │   ├── kc.pdf          # Kodeks cywilny
│   │   ├── kk.pdf          # Kodeks karny
│   │   ├── kks.pdf         # Kodeks karny skarbowy
│   │   ├── kp.pdf          # Kodeks pracy
│   │   ├── kpa.pdf         # Kodeks postępowania administracyjnego
│   │   ├── kpc.pdf         # Kodeks postępowania cywilnego
│   │   ├── kpk.pdf         # Kodeks postępowania karnego
│   │   ├── kpsw.pdf        # Kodeks postępowania w sprawach o wykroczenia
│   │   ├── krio.pdf        # Kodeks rodzinny i opiekuńczy
│   │   ├── ksh.pdf         # Kodeks spółek handlowych
│   │   └── kw.pdf          # Kodeks wykroczeń
│   ├── Zestaw_pytań_testowych_..._2024.pdf         # Questions PDF
│   └── Wykaz_prawidłowych_odpowiedzi_..._2024.pdf  # Answers PDF
└── 2025/
    ├── legal_base/
    │   └── [same legal code PDFs]
    ├── Zestaw_pytań_testowych_..._2025.pdf
    └── Wykaz_prawidłowych_odpowiedzi_..._2025.pdf
```

### Required Files per Year

For each year directory, you need:

1. **Questions PDF**: Filename must start with `Zestaw_pytań`
2. **Answers PDF**: Filename must start with `Wykaz_prawidłowych_odpowiedzi`
3. **Legal Base Directory**: A `legal_base/` subdirectory containing PDF files for Polish legal codes

## Output Format

### Directory Structure

Output files are saved to `data/exams/` with the following structure:

```
data/exams/
└── adwokacki_radcowy/
    ├── 2024.jsonl
    └── 2025.jsonl
```

### JSONL Format

Each line in the output JSONL file represents one exam question and follows this schema:

```json
{
  "id": 1,
  "question": "Zgodnie z Kodeksem karnym, czyn zabroniony uważa się za popełniony w miejscu, w którym:",
  "choices": {
    "A": "sprawca działał lub zaniechał działania, do którego był obowiązany...",
    "B": "ujawniono czyn zabroniony,",
    "C": "zatrzymano sprawcę czynu zabronionego."
  },
  "correct_answer": "A",
  "legal_basis": "art. 6 § 2 k.k.",
  "legal_basis_content": "Czyn zabroniony uważa się za popełniony w miejscu...",
  "exam_type": "adwokacki_radcowy",
  "year": 2025
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Question number (1-indexed) |
| `question` | string | The question text |
| `choices` | object | Multiple choice options with keys "A", "B", "C" |
| `correct_answer` | string | The correct answer option ("A", "B", or "C") |
| `legal_basis` | string | Legal reference (e.g., "art. 6 § 2 k.k.") |
| `legal_basis_content` | string | Full text of the referenced legal article/paragraph/point |
| `exam_type` | string | Type of exam (adwokacki_radcowy, komorniczy, notarialny) |
| `year` | int | Year of the exam |

## Development

### Running Tests

```bash
python -m pytest parsers/
```

