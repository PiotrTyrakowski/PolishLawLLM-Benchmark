# Polish Law LLM Benchmark

A comprehensive benchmark framework for evaluating Large Language Models (LLMs) on Polish legal examination questions. This project provides tools to test various LLMs against real Polish legal bar exam questions across different legal specializations.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- API keys for the LLM services you want to test

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd PolishLawLLM-Benchmark
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # For Google Gemini models
   export GEMINI_API_KEY="your_gemini_api_key_here"
   
   # Add other API keys as needed when more models are supported
   ```

### Basic Usage

Run a benchmark using the command-line interface:

```bash
python -m benchmark_framework.cli <path_to_questions> <model_name>
```

**Example:**
```bash
python -m benchmark_framework.cli exams/2024/adwokacki_radcowy/questions.jsonl gemini-2.5-flash
```

## 🤖 Supported Models

Currently supported models:

| Model Name | Provider | Description |
|------------|----------|-------------|
| `gemini-2.5-flash` | Google | Google Gemini 2.5 Flash model |

## 📈 Evaluation Metrics

The benchmark currently provides:
- **Accuracy**: Percentage of correctly answered questions

## 📝 Data Format

### Input Format (JSONL)
Each line contains a single question object:
```jsonl
{"question": "Question text...", "choices": ["A) ...", "B) ...", "C) ..."], "answer": "A"}
{"question": "Another question...", "choices": ["A) ...", "B) ...", "C) ..."], "answer": "B"}
```

## 🛠️ Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run code formatting
black benchmark_framework/

# Run linting
pylint benchmark_framework/
```