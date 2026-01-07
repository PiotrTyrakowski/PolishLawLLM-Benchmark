#!/bin/bash

# Script to calculate metrics and stats for exams on models that have exams folders
# Models with exams: perplexity-sonar, perplexity-sonar-pro-search, x-ai-grok-4.1-fast

set -e  # Exit on error

# Base directories
RESULTS_DIR="data/results"
METRICS_DIR="data/results_with_metrics"
CORPUSES_DIR="data/corpuses"

# Models with exams folders
MODELS=(
    "perplexity-sonar"
    "perplexity-sonar-pro-search"
    "x-ai-grok-4.1-fast"
)

echo "=========================================="
echo "Running metrics and stats for exams"
echo "=========================================="
echo ""

# Step 1: Calculate metrics for each model
echo "Step 1: Calculating metrics..."
echo ""

for model in "${MODELS[@]}"; do
    input_dir="${RESULTS_DIR}/${model}/exams"
    output_dir="${METRICS_DIR}/${model}/exams"

    if [ ! -d "$input_dir" ]; then
        echo "Warning: Input directory '$input_dir' does not exist. Skipping $model."
        continue
    fi

    echo "Processing $model..."
    echo "  Input:  $input_dir"
    echo "  Output: $output_dir"

    # Create output directory if it doesn't exist
    mkdir -p "$output_dir"

    # Run calculate_metrics
    python -m src.benchmark_framework.calculate_metrics \
        "$input_dir" \
        "$output_dir" \
        "$CORPUSES_DIR" \
        --force

    echo "  Completed metrics for $model"
    echo ""
done

echo "=========================================="
echo "Step 2: Calculating statistics..."
echo "=========================================="
echo ""

# Step 2: Calculate stats for each model
for model in "${MODELS[@]}"; do
    metrics_dir="${METRICS_DIR}/${model}/exams"

    if [ ! -d "$metrics_dir" ]; then
        echo "Warning: Metrics directory '$metrics_dir' does not exist. Skipping stats for $model."
        continue
    fi

    echo "Calculating stats for $model..."
    echo "  Directory: $metrics_dir"

    # Run calculate_stats
    python -m src.benchmark_framework.calculate_stats "$metrics_dir"

    echo ""
    echo "  Completed stats for $model"
    echo "----------------------------------------"
    echo ""
done

echo "=========================================="
echo "All done!"
echo "=========================================="
