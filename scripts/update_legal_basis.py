"""
Script to update legal_basis and legal_basis_content fields in judgment result files
by reading the correct values from task files.
"""

import json
from pathlib import Path


def load_tasks(tasks_dir: Path) -> dict:
    """Load all task files and build a mapping of id -> {legal_basis, legal_basis_content}."""
    task_data = {}

    for task_file in tasks_dir.glob("*.jsonl"):
        print(f"Loading tasks from: {task_file.name}")
        with open(task_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    task_id = record.get("id")
                    if task_id is not None:
                        task_data[task_id] = {
                            "legal_basis": record.get("legal_basis"),
                            "legal_basis_content": record.get("legal_basis_content"),
                        }

    print(f"Loaded {len(task_data)} tasks total\n")
    return task_data


def update_result_file(result_file: Path, task_data: dict) -> tuple[int, int]:
    """Update a single result file with legal_basis data from tasks.

    Returns: (updated_count, not_found_count)
    """
    updated_records = []
    updated_count = 0
    not_found_count = 0

    with open(result_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                record_id = record.get("id")

                if record_id in task_data:
                    record["legal_basis"] = task_data[record_id]["legal_basis"]
                    record["legal_basis_content"] = task_data[record_id]["legal_basis_content"]
                    updated_count += 1
                else:
                    not_found_count += 1
                    print(f"  Warning: ID {record_id} not found in tasks")

                updated_records.append(record)

    with open(result_file, "w", encoding="utf-8") as f:
        for record in updated_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return updated_count, not_found_count


def main():
    # Get repository root (parent of scripts directory)
    repo_root = Path(__file__).parent.parent
    base_dir = repo_root / "data"
    tasks_dir = base_dir / "tasks" / "judgments"
    results_dir = base_dir / "results"

    print("=" * 60)
    print("Loading task data...")
    print("=" * 60)
    task_data = load_tasks(tasks_dir)

    print("=" * 60)
    print("Updating result files...")
    print("=" * 60)

    result_files = list(results_dir.glob("*/judgments/all.jsonl"))
    print(f"Found {len(result_files)} result files to process\n")

    total_updated = 0
    total_not_found = 0

    for result_file in sorted(result_files):
        model_name = result_file.parent.parent.name
        print(f"Processing: {model_name}")

        updated, not_found = update_result_file(result_file, task_data)
        total_updated += updated
        total_not_found += not_found

        print(f"  Updated: {updated} records")
        if not_found > 0:
            print(f"  Not found: {not_found} records")
        print()

    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total records updated: {total_updated}")
    print(f"Total records not found in tasks: {total_not_found}")


if __name__ == "__main__":
    main()
