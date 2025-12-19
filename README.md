# Polish Law LLM Benchmark

A comprehensive benchmark framework for evaluating Large Language Models (LLMs) on Polish legal tasks. This project provides tools to test various LLMs against real Polish legal bar exam questions and court judgment analysis tasks.

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
   
   # For NVIDIA models (Bielik, DeepSeek, Meta, CYFRAGOVPL)
   export NVIDIA_API_KEY="your_nvidia_api_key_here"
   ```

### Basic Usage

Run a benchmark using the command-line interface:

```bash
python -m benchmark_framework.cli <model_name> <dataset_name> [OPTIONS]
```

**Examples:**
```bash
# Run on legal exams dataset with Gemini
python -m benchmark_framework.cli gemini-2.5-flash exams

# Run with Google Search enabled (Gemini only)
python -m benchmark_framework.cli gemini-2.5-pro exams --google-search

# Run on judgments dataset with NVIDIA model
python -m benchmark_framework.cli deepseek/deepseek-r1-turbo judgments
```

## 🤖 Supported Models

| Model Prefix | Provider | Description |
|--------------|----------|-------------|
| `gemini-*` | Google | Google Gemini models (e.g., `gemini-2.5-flash`, `gemini-2.5-pro`) |
| `bielik-*` | NVIDIA | Polish Bielik 11B model via NVIDIA API |
| `speakleash/*` | Local | Local model inference using HuggingFace Transformers |
| `deepseek/*` | NVIDIA | DeepSeek models via NVIDIA API |
| `meta/*` | NVIDIA | Meta LLaMA models via NVIDIA API |
| `CYFRAGOVPL/*` | NVIDIA NIM | Polish government LLM models via NVIDIA NIM |

## 📊 Datasets

### Legal Exams (`exams`)
Polish legal bar exam questions from multiple exam types:
- **Adwokacki/Radcowy** - Bar attorney and legal counsel exams
- **Komorniczy** - Bailiff exams  
- **Notarialny** - Notary exams

Each question includes:
- Question text with 3 answer options (A, B, C)
- Correct answer
- Legal basis reference (article, paragraph, point)
- Legal basis content (exact text of the law)

### Court Judgments (`judgments`)
Tasks involving analysis of masked court judgment reasoning to identify the applicable legal provisions.

## 📈 Evaluation Metrics

| Metric            | Description                                                  |
|-------------------|--------------------------------------------------------------|
| **Exact Match**   | Accuracy for answer selection (A, B, C)                      |
| **BLEU**          | Standard BLEU metric                                         |
| **Weighted BLEU** | TF-IDF weighted BLEU score for legal basis content evaluation |

## 📝 Data Format

### Exam Questions (JSONL)
```json
{
  "id": 1,
  "question": "Zgodnie z Kodeksem karnym, czyn zabroniony uważa się za...",
  "choices": {
    "A": "sprawca działał lub zaniechał działania...",
    "B": "ujawniono czyn zabroniony,",
    "C": "zatrzymano sprawcę czynu zabronionego."
  },
  "answer": "A",
  "legal_basis": "art. 6 § 2 k.k.",
  "legal_basis_content": "Czyn zabroniony uważa się za popełniony w miejscu...",
  "exam_type": "adwokacki_radcowy",
  "year": 2024
}
```

### Model Response Format (JSON)
```json
{
  "reasoning": "Brief analysis of each option",
  "answer": "A",
  "legal_basis": "Art. 123 § 2 k.k.",
  "legal_basis_content": "Exact text of the cited legal provision"
}
```

## 🔧 Parsing Exam PDFs

The project includes tools to extract exam data from official PDF files:

```bash
python -m parsers.cli parse <path-to-pdfs-directory>
```

See [parsers/README.md](src/parsers/README.md) for detailed instructions.

## 🛠️ Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run code formatting
black benchmark_framework/ parsers/

# Run 
python -m pytest
```
