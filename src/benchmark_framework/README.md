# Benchmark Framework

A modular framework for benchmarking Large Language Models on Polish legal tasks. The framework supports multiple LLM providers, configurable evaluation metrics, and extensible task types.

## Features

- 🤖 **Multi-Provider Support**: OpenAI, Anthropic, Google Gemini, NVIDIA, and local models
- 📊 **Evaluation Metrics**: Exact match, ROUGE-N, ROUGE-W, TF-IDF weighted ROUGE
- 🔧 **Extensible Architecture**: Abstract base classes for models, managers, and metrics
- ⏱️ **Rate Limiting**: Configurable requests per minute and daily limits
- 💾 **Incremental Processing**: Skip already processed tasks on re-runs
- 📈 **Statistics Calculation**: Aggregate accuracy and text similarity metrics

## Architecture

```
benchmark_framework/
├── cli.py                      # Main CLI entry point for running benchmarks
├── runner.py                   # BenchmarkRunner - orchestrates task execution
├── calculate_metrics.py        # CLI for calculating metrics on results
├── calculate_stats.py          # CLI for aggregating statistics
├── configs/                    # Configuration dataclasses
│   ├── model_config.py         # ModelConfig (google_search, quantize, batch_size)
│   └── runner_config.py        # RunnerConfig (requests_per_minute, daily_limit)
├── getters/                    # Factory functions
│   ├── get_llm_model.py        # Model factory (maps names to implementations)
│   ├── get_manager.py          # Manager factory (maps task types)
│   └── get_type.py             # Task type resolution
├── managers/                   # Task managers (per task type)
│   ├── base_manager.py         # Abstract BaseManager
│   ├── exam_manager.py         # ExamManager for legal exam tasks
│   └── judgment_manager.py     # JudgmentManager for court judgments
├── metrics/                    # Evaluation metrics
│   ├── base_metric.py          # Abstract BaseMetric (normalized [0,1] scores)
│   ├── exact_match.py          # ExactMatchMetric
│   ├── rouge_n.py              # RougeNMetric (configurable n-gram weights)
│   ├── rouge_w.py              # RougeWMetric (weighted longest common subsequence)
│   └── tfidf_rouge_n.py        # TFIDFRougeNMetric (corpus-weighted)
├── models/                     # LLM provider implementations
│   ├── base_model.py           # Abstract BaseModel
│   ├── openai.py               # OpenAI GPT models
│   ├── anthropic.py            # Claude models
│   ├── gemini.py               # Google Gemini (with optional Google Search)
│   ├── nvidia_model.py         # NVIDIA API hosted models
│   ├── nvidia_nim_model.py     # NVIDIA NIM models
│   └── local_model.py          # Local model support
└── utils/
    ├── task_loader.py          # Load tasks from JSONL files
    └── response_parser.py      # Parse JSON fields from model responses
```

---

## CLI Commands

### 1. Run Benchmark

Execute benchmarks against a specified model.

```bash
python -m src.benchmark_framework.cli <model-name> <task-type> [output-path] [input-path] [options]
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `model-name` | Model identifier (e.g., `gemini-2.0-flash`, `gpt-4o`, `claude-3-opus`) |
| `task-type` | Task type to benchmark (e.g., `exams`) |
| `output-path` | Output directory for results (default: `data/results`) |
| `input-path` | Input directory with task files (default: `data/tasks`) |

#### Options

| Option | Description |
|--------|-------------|
| `--google-search` | Enable Google Search grounding (Gemini only) |
| `--year`, `-y` | Filter tasks to a specific year (e.g., `2024`) |

#### Examples

```bash
# Run benchmark with Gemini
python -m src.benchmark_framework.cli gemini-2.0-flash exams data/results data/tasks

# Run with GPT-4o for year 2025 only
python -m src.benchmark_framework.cli gpt-4o exams --year 2025

# Run with Google Search enabled (Gemini only)
python -m src.benchmark_framework.cli gemini-2.0-flash exams --google-search
```

---

### 2. Calculate Metrics

Calculate evaluation metrics on benchmark results.

```bash
python -m src.benchmark_framework.calculate_metrics <input-dir> <output-dir> [corpuses-dir] [--force]
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `input-dir` | Directory containing result JSONL files |
| `output-dir` | Directory for processed files with metrics |
| `corpuses-dir` | Corpuses directory for TF-IDF (default: `data/corpuses`) |

#### Options

| Option | Description |
|--------|-------------|
| `--force`, `-f` | Overwrite existing output files |

#### Example

```bash
python -m src.benchmark_framework.calculate_metrics data/results data/metrics data/corpuses
```

---

### 3. Calculate Statistics

Aggregate statistics from metric results.

```bash
python -m src.benchmark_framework.calculate_stats <file-path>
```

#### Example

```bash
python -m src.benchmark_framework.calculate_stats data/metrics/gemini-2.0-flash/exams/2025/adwokacki_radcowy.jsonl
```

#### Output

```
=== Results ===
Accuracy Metrics:
  Answer accuracy: 0.8750
  Legal basis accuracy: 0.7200

Text Metrics:
  exact_match: 0.4500
  rouge_n: 0.7234
  rouge_w: 0.6845
  tfidf_rouge_n: 0.7012

Malformed Response Rate: 0.0200
```

---

## Supported Models

Models are auto-detected by prefix in the model name:

| Prefix | Provider | Example Model Names |
|--------|----------|---------------------|
| `gemini` | Google | `gemini-2.0-flash`, `gemini-2.5-pro` |
| `gpt` | OpenAI | `gpt-4o`, `gpt-4-turbo` |
| `claude` | Anthropic | `claude-3-opus`, `claude-3-sonnet` |
| `speakleash` | NVIDIA | `speakleash/Bielik-11B-v2.3-Instruct` |
| `deepseek` | NVIDIA | `deepseek/deepseek-chat` |
| `meta` | NVIDIA | `meta/llama-3.1-70b-instruct` |
| `CYFRAGOVPL` | NVIDIA NIM | `CYFRAGOVPL/PLLuM-12B-instruct` |

---

## Evaluation Metrics

### Accuracy Metrics
- **Answer**: Exact match of model answer vs correct answer (A/B/C)
- **Legal Basis**: Exact match of cited legal basis

### Text Metrics
All text metrics are normalized to [0.0, 1.0]:

| Metric | Description |
|--------|-------------|
| `exact_match` | Binary 1.0 if texts match exactly, else 0.0 |
| `rouge_n` | N-gram overlap (configurable 1-gram, 2-gram, 3-gram weights) |
| `rouge_w` | Weighted longest common subsequence |
| `tfidf_rouge_n` | ROUGE-N weighted by corpus TF-IDF scores |

---

## Output Format

Results are saved as JSONL files organized by model, task type, year, and exam type:

```
data/results/
└── gemini-2.0-flash/
    └── exams/
        └── 2025/
            └── adwokacki_radcowy.jsonl
```

Each entry contains:
- Original task data (question, choices, correct answer, legal basis)
- Model response (answer, legal_basis, legal_basis_content)
- Model metadata (name, config)

After metric calculation:
- `accuracy_metrics`: `{answer: bool, legal_basis: bool}`
- `text_metrics`: `{exact_match: float, rouge_n: float, ...}`

---

## Environment Variables

Set API keys for the respective providers:

| Provider | Environment Variable |
|----------|---------------------|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Google | `GOOGLE_API_KEY` |
| NVIDIA | `NVIDIA_API_KEY` |

---

## Testing

```bash
python -m pytest src/benchmark_framework/
```

Test directories:
- `src/benchmark_framework/metrics/tests/`
- `src/benchmark_framework/utils/tests/`
