# Polish Law Exam PDF Parser

A tool to parse Polish legal examination PDFs and convert them into structured JSONL format for the benchmark framework.

## 📋 Overview

This parser processes Polish bar exam PDFs (questions and answers) and creates unified JSONL files that can be used with the PolishLawLLM-Benchmark framework. It supports three types of legal exams:
- Adwokacki/Radcowy (Attorney/Legal Counsel)
- Komorniczy (Bailiff)
- Notarialny (Notary)

## 🗂️ Input Data Structure

### 1. Create the PDFs Directory

Create a directory for your exam PDFs (e.g., `pdfs/` or `pdfs/2024/`). This directory should contain:
- Exam PDF files (questions and answers)
- A `legal_base/` subdirectory with legal reference documents

```bash
cd /path/to/PolishLawLLM-Benchmark
mkdir -p pdfs/legal_base
```

### 2. PDF File Naming Conventions

Place your exam PDFs in your chosen directory following these naming requirements:

#### Questions File
- **Must start with**: `Zestaw_pytań`
- **Example**: `Zestaw_pytań_2024_adwokacki.pdf`

#### Answers File
- **Must start with**: `Wykaz_prawidłowych_odpowiedzi`
- **Example**: `Wykaz_prawidłowych_odpowiedzi_2024_adwokacki.pdf`

#### Required Components in Filename
1. **Year**: Must contain a 4-digit year (e.g., `2024`, `2023`, `2022`)
2. **Exam Type**: Must contain one of these keywords:
   - `adwokack` or `radcow` → Parsed as `adwokacki_radcowy`
   - `komornic` → Parsed as `komorniczy`
   - `notarialn` → Parsed as `notarialny`

### 3. Example Directory Structure

```
PolishLawLLM-Benchmark/
├── pdfs/
│   ├── legal_base/          # Required subdirectory for legal reference documents
│   │   ├── kc.pdf           # Civil Code
│   │   ├── kk.pdf           # Criminal Code
│   │   ├── kpc.pdf          # Civil Procedure Code
│   │   └── ...              # Other legal references
│   ├── Zestaw_pytań_2024_adwokacki.pdf
│   ├── Wykaz_prawidłowych_odpowiedzi_2024_adwokacki.pdf
│   ├── Zestaw_pytań_2024_notarialny.pdf
│   ├── Wykaz_prawidłowych_odpowiedzi_2024_notarialny.pdf
│   ├── Zestaw_pytań_2023_komorniczy.pdf
│   └── Wykaz_prawidłowych_odpowiedzi_2023_komorniczy.pdf
└── ...
```

## 🚀 Usage

### Basic Command

Run the parser from the repository root, providing the path to your PDFs directory:

```bash
python -m parsers.cli parse pdfs/
```

### Command Arguments & Options

| Argument/Option | Type | Description | Default |
|----------------|------|-------------|---------|
| `pdfs_path` | Argument (required) | Path to the directory containing exam PDFs and legal_base/ folder | - |
| `--stats` | Option | Generate detailed statistics about parsed data | `False` |
| `--no-validate` | Option | Disable validation of parsed questions/answers | `True` (validation enabled) |

### Examples

**Basic parsing:**
```bash
python -m parsers.cli pdfs/
```

**Parse with statistics:**
```bash
python -m parsers.cli pdfs/ --stats
```

**Parse without validation (not recommended):**
```bash
python -m parsers.cli pdfs/ --no-validate
```

**Parse with both options:**
```bash
python -m parsers.cli pdfs/ --stats --no-validate
```

## 📤 Output Structure

### Output Directory

Parsed data is saved to: `data/exams/{exam_type}/{year}.jsonl`

### Example Output Structure

```
data/
└── exams/
    ├── adwokacki_radcowy/
    │   ├── 2024.jsonl
    │   ├── 2023.jsonl
    │   └── stats_2024.json (if --stats used)
    ├── komorniczy/
    │   ├── 2024.jsonl
    │   └── 2023.jsonl
    └── notarialny/
        ├── 2024.jsonl
        └── stats_2023.json (if --stats used)
```

### Output Format (JSONL)

Each line in the output JSONL file contains one question with this structure:

```json
{
  "id": 1,
  "year": 2024,
  "exam_type": "adwokacki_radcowy",
  "question": "Question text here?",
  "choices": [
    "A) First option text",
    "B) Second option text",
    "C) Third option text"
  ],
  "answer": "A",
  "legal_basis": "art. 65 ust. 3 Konstytucji..."
}
```

## 📝 Expected PDF Format

### Questions PDF Format

The questions PDF should:
- Contain **exactly 150 questions**
- Start questions from **page 2** (page 1 typically contains exam info)
- Follow this format:

```
1. Question text here about legal topic?
A. First answer option
B. Second answer option
C. Third answer option

2. Next question text here?
A. First answer option
B. Second answer option
C. Third answer option
```

### Answers PDF Format

The answers PDF should:
- Contain **exactly 150 answers**
- Be formatted as a table with: question number, correct answer, and legal basis

```
1. A art. 65 ust. 3 Konstytucji...
2. B art. 120 k.p.c...
3. C art. 45 § 1 k.c...
```

## ⚠️ Parser Behavior

### Validation (Default: Enabled)

When validation is enabled (`--validate`, which is the default), the parser checks:
- ✅ Question number exists
- ✅ Question text is not empty
- ✅ All three options (A, B, C) are present and not empty
- ✅ Question text is at least 10 characters
- ✅ Answer is one of: A, B, or C

Invalid questions are reported but not included in the output.

### Expected Counts

- **Questions**: 150 per exam
- **Answers**: 150 per exam

If the parser finds a different number, it will display a warning but still process the data.

### Console Output

The parser provides real-time feedback:

```
$ python -m parsers.cli pdfs/

Processing exam: Year - 2024, Type - adwokacki_radcowy
Parsing questions from: pdfs/Zestaw_pytań_2024_adwokacki.pdf
  Processing page 2/42...
  Found 150 potential questions
  - Successfully parsed 150 questions.
Parsing answers from: pdfs/Wykaz_prawidłowych_odpowiedzi_2024_adwokacki.pdf
  Processing page 1/3...
  Found 150 answers using table pattern
  - Successfully parsed 150 answers.
  - Saved unified format: data/exams/adwokacki_radcowy/2024.jsonl
```

## 📊 Statistics Output

When using the `--stats` flag, the parser generates a JSON file with:

```json
{
  "total_questions": 150,
  "avg_question_length": 234.5,
  "avg_option_length": 87.3,
  "questions_with_short_text": 2,
  "questions_with_long_text": 15,
  "year": 2024,
  "exam_type": "adwokacki_radcowy"
}
```

## 🔍 Technical Details

### Dependencies

The parser uses:
- `pdfplumber` - For PDF text extraction
- `typer` - For CLI interface
- Standard Python libraries (re, json, pathlib)

## 🧪 Running Tests

The parser includes unit tests to ensure the regex patterns and parsing logic work correctly.

### Prerequisites

Make sure pytest is installed:

```bash
pip install pytest
```

### Running All Parser Tests

To run all tests in the parsers module:

```bash
# From the repository root
python -m pytest parsers/tests/ -v
```

### Running Specific Test Files

```bash
python -m pytest parsers/tests/test_answers_regexp.py -v
```

