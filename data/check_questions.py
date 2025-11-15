#!/usr/bin/env python3

import argparse
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple

"""
This script is responsible for checking that model responses are unique across evaluation files.
It verifies that:
1. Each question in results matches a real exam question
2. There are no duplicate questions within a results file 
3. All exam questions are covered by the results

This helps ensure model evaluations are valid and complete without redundant entries.
"""



def normalize_question(text: str) -> str:
    """Normalize question text for robust matching across files."""
    if text is None:
        return ""
    # Collapse whitespace and strip
    return " ".join(str(text).split()).strip()


def load_exam_questions(data_root: Path):
    """
    Load questions from data/exams/*/*.jsonl

    Returns:
    - all_rows: list of all parsed rows
    - by_exam_file: mapping of exam file path (str) -> list of rows
    """
    all_rows: List[str] = []
    for jsonl_path in sorted((data_root / "exams").glob("*/*.jsonl")):
        with jsonl_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Invalid JSON in {jsonl_path}:{line_num}: {e}", file=sys.stderr)
                    continue

                question_text = normalize_question(obj.get("question", ""))
                exam_type = obj.get("exam_type", "")
                year = obj.get("year")
                row = f"{year}-{exam_type}-{question_text}"

                all_rows.append(row)

    return all_rows


def check_results_against_exam(results_root: Path, exam_questions: Set[str], list_limit: int = 20) -> int:
    """
    For each results/exams/*.jsonl file, verify that every (year-exam_type-question)
    exists in the exam_questions set, detect duplicates within the file, and report
    exam questions missing in that results file.

    Returns number of files that had any issues.
    """
    problems = 0
    for jsonl_path in sorted((results_root / "exams").glob("*.jsonl")):
        seen: Counter = Counter()
        seen_lines: Dict[str, List[int]] = defaultdict(list)
        unknown: List[str] = []
        total = 0

        with jsonl_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                total += 1
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Invalid JSON in {jsonl_path}:{line_num}: {e}", file=sys.stderr)
                    continue

                question_text = normalize_question(obj.get("question", ""))
                exam_type = obj.get("exam_type", "")
                year = obj.get("year")
                triple = f"{year}-{exam_type}-{question_text}"

                seen[triple] += 1
                seen_lines[triple].append(line_num)
                if triple not in exam_questions:
                    unknown.append(triple)

        seen_set = set(seen.keys())
        duplicates = [t for t, c in seen.items() if c > 1]
        missing = sorted(list(exam_questions - seen_set))

        has_issue = bool(unknown or duplicates or missing)
        if has_issue:
            problems += 1

        print(f"- {jsonl_path.name}: total={total} unique={len(seen_set)} duplicates={len(duplicates)} unknown={len(unknown)} missing={len(missing)}")
        if duplicates:
            print("  Duplicates (up to {0}):".format(list_limit))
            for t in duplicates[:list_limit]:
                lines = seen_lines.get(t, [])
                first = lines[0] if lines else None
                repeats = lines[1:] if len(lines) > 1 else []
                print(f"    {t}  lines={lines}  first={first} repeats={repeats}")
        if unknown:
            print("  Unknown (not in exams) (up to {0}):".format(list_limit))
            for t in unknown[:list_limit]:
                print(f"    {t}")
        if missing:
            print("  Missing from results (up to {0}):".format(list_limit))
            for t in missing[:list_limit]:
                print(f"    {t}")

    return problems

def main() -> int:
    parser = argparse.ArgumentParser(description="Check results against exam questions using (year-exam_type-question) triples")
    parser.add_argument("--data", default="data", help="Path to data directory (default: data)")
    parser.add_argument("--results", default="results", help="Path to results directory (default: results)")
    parser.add_argument("--list-limit", type=int, default=20, help="Max number of items to list per category")
    args = parser.parse_args()

    data_root = Path(args.data).resolve()
    results_root = Path(args.results).resolve()

    if not (data_root / "exams").exists():
        print(f"[ERROR] Not found: {data_root / 'exams'}", file=sys.stderr)
        return 2
    if not (results_root / "exams").exists():
        print(f"[ERROR] Not found: {results_root / 'exams'}", file=sys.stderr)
        return 2

    exam_list = load_exam_questions(data_root)
    exam_set = set(exam_list)

    print("=== Data/exams summary ===")
    print(f"Questions: {len(exam_list)}  Unique (year-exam_type-question): {len(exam_set)}")

    print("\n=== Results/exams check ===")
    problems = check_results_against_exam(results_root, exam_set, list_limit=args.list_limit)

    if problems:
        print("\nCheck: issues found")
        return 1
    print("\nCheck: OK (no duplicates, no unknown, no missing)")
    return 0


if __name__ == "__main__":
    sys.exit(main())


