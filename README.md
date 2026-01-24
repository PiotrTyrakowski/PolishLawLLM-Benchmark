# Polish Law LLM Benchmark

A benchmark framework for evaluating Large Language Models on Polish legal tasks, including exam questions and court judgment analysis.

## Project Structure

```
PolishLawLLM-Benchmark/
├── src/
│   ├── benchmark_framework/    # LLM benchmarking framework
│   ├── parsers/                # PDF parsing for exam data extraction
│   ├── uploaders/              # Upload results to Firebase
│   └── common/                 # Shared utilities and domain models
├── data/
│   ├── pdfs/                   # Source PDF files (exams, legal codes)
│   ├── corpuses/               # Extracted legal code articles (JSON)
│   ├── tasks/                  # Benchmark tasks (JSONL)
│   └── results/                # Benchmark results
└── frontend/                   # Results visualization dashboard
```

## Quick Start

### Installation

```bash
git clone <repository-url>
cd PolishLawLLM-Benchmark
pip install -r requirements.txt
```

### Environment Variables

```bash
export GOOGLE_API_KEY="..."      # For Gemini models
export OPENAI_API_KEY="..."      # For GPT models
export ANTHROPIC_API_KEY="..."   # For Claude models
export OPENROUTER_API_KEY="..."  # For OpenRouter-hosted models
export HF_TOKEN="..."            # For models hosted using Hugging Face Inference Endpoints
export HF_ENDPOINT_URL="..."     # Custom endpoint URL for Hugging Face Inference Endpoints
export MISTRAL_API_KEY="..."     # For Mistral models
```

### Run the tests

```bash
python -m src.benchmark_framework.cli gpt-5.2 exams
```

---

## Modules

### Benchmark Framework

Run LLM evaluations, calculate metrics, and aggregate statistics.

```bash
# Run benchmark
python -m src.benchmark_framework.cli <model-name> <task-type>

# Calculate metrics on results
python -m src.benchmark_framework.calculate_metrics <input-dir> <output-dir>

# Get aggregate statistics
python -m src.benchmark_framework.stats.cli stats <file-path>
```

**[Detailed documentation →](src/benchmark_framework/README.md)**

---

### Parsers

Extract exam questions and legal code articles from PDF files.

```bash
# Generate legal code corpuses
python -m src.parsers.corpuses.setup_corpuses <pdf-dir> <output-dir> <year>

# Parse exam PDFs
python -m src.parsers.cli <pdfs-dir> <corpuses-dir> <output-dir>
```

**[Detailed documentation →](src/parsers/README.md)**

---

### Uploaders

Upload benchmark results to Firebase for visualization in the frontend dashboard.

```bash
python -m src.uploaders.cli <results-dir>
```

**[Detailed documentation →](src/uploaders/Readme.md)**

---

### Frontend

Next.js web dashboard for visualizing benchmark results stored in Firebase.

```bash
cd frontend
bun install
bun run dev
```

**[Detailed documentation →](frontend/README.md)**

---

## Task Types

| Task | Description |
|------|-------------|
| `exams` | Polish legal bar exam questions (adwokacki, radcowy, komorniczy, notarialny) |
| `judgments` | Court judgment analysis tasks |

---

## Development

```bash
# Run tests
python -m pytest src/

# Code formatting
black src/
```
