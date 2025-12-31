# Results Uploader

## Uploader assumes this file structure

```text
data/results_with_metrics/
└── {model_id}/
    ├── model_fields.json
    └── exams/
        └── {year}/
            └── {exam_type}.jsonl
    └── judgments/
        └── all.jsonl
```