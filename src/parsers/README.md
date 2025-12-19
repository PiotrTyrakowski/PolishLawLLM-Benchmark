# Polish Law Exam Parser

This tool extracts exam questions, answers, and legal basis content from PDF files and outputs them in a structured JSONL format suitable for the benchmark.

## Features

- 📄 **PDF Parsing**: Extracts questions and answers from exam PDFs
- ⚖️ **Legal Basis Extraction**: Retrieves relevant legal code content from pre-generated corpus files
- 📊 **Structured Output**: Generates JSONL files ready for LLM benchmarking
- 🔍 **Multiple Exam Types**: Supports adwokacki/radcowy, komorniczy, and notarialny exams
- 📁 **Multi-Year Support**: Processes exams from multiple years in a single run

## Architecture

```
parsers/
├── cli.py                  # Command-line interface for parsing exams
├── setup_corpuses.py       # CLI for generating corpus files from legal PDFs
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

## Workflow Overview

The task generation process consists of two steps:

1. **Generate Corpuses**: Extract articles from legal base PDFs into JSON corpus files
2. **Parse Exams**: Process exam PDFs and enrich with legal content from corpuses

## Step 1: Generate Corpuses

Before parsing exams, you need to generate corpus files from the legal base PDFs.

### Command

```bash
python -m src.parsers.setup_corpuses <legal-base-pdf-directory> <output-corpus-directory>
```

### Example

```bash
# Generate corpus for year 2024
python -m src.parsers.setup_corpuses data/pdfs/2024/legal_base data/corpuses/2024

# Generate corpus for year 2025
python -m src.parsers.setup_corpuses data/pdfs/2025/legal_base data/corpuses/2025
```

### Legal Base PDF Directory Structure

```
pdfs/2024/legal_base/
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

The command generates JSON files containing extracted articles:

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

## Step 2: Parse Exams

After generating corpuses, parse the exam PDFs using the corpus files for legal content enrichment.

### Command

```bash
python -m src.parsers.cli <pdfs-directory> <corpuses-directory> [output-directory]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `pdfs-directory` | Path to directory containing exam PDFs (organized by year) |
| `corpuses-directory` | Path to corpuses directory (containing year subdirectories with JSON files) |
| `output-directory` | Optional. Output path for JSONL files (default: `data/tasks/exams`) |

### Example

```bash
python -m src.parsers.cli data/pdfs/ data/corpuses/ data/tasks/exams
```

## Input Directory Structures

### Exam PDFs Directory

```
pdfs/
├── 2024/
│   ├── legal_base/
│   │   └── [same legal code PDFs]
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

### Corpuses Directory

The corpuses directory must contain year subdirectories matching the exam years:

```
corpuses/
├── 2024/
│   ├── kc.json
│   ├── kk.json
│   └── ...
└── 2025/
    ├── kc.json
    ├── kk.json
    └── ...
```

> **Note**: If a corpus directory for a specific year is missing, exams for that year will be skipped with a warning.

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
  "answer": "A",
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
| `answer` | string | The correct answer option ("A", "B", or "C") |
| `legal_basis` | string | Legal reference (e.g., "art. 6 § 2 k.k.") |
| `legal_basis_content` | string | Full text of the referenced legal article/paragraph/point |
| `exam_type` | string | Type of exam (adwokacki_radcowy, komorniczy, notarialny) |
| `year` | int | Year of the exam |

## Development

### Running Tests

```bash
python -m pytest src/parsers/
```

