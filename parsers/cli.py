import json
import os
import re
from pathlib import Path

import typer

from parsers.combiner import create_unified_jsonl
from parsers.pdf_parser import parse_answers, parse_questions
from parsers.stats import generate_statistics
from parsers.utils import save_as_jsonl

app = typer.Typer()


@app.command()
def parse(
    stats: bool = typer.Option(False, "--stats", help="Generate statistics"),
    validate: bool = typer.Option(True, "--validate", help="Validate parsed data"),
):
    """
    Parse Polish law exam PDFs from the 'pdfs' directory and create unified JSONL files.
    """
    pdf_dir = "pdfs"
    if not os.path.exists(pdf_dir):
        if not os.path.exists(f"../{pdf_dir}"):
            typer.echo(f"Error: '{pdf_dir}' directory not found")
            raise typer.Exit(code=1)
        pdf_dir = f"../{pdf_dir}"

    all_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]

    exams = {}

    for pdf_file in all_files:
        year_match = re.search(r"\d{4}", pdf_file)
        if not year_match:
            typer.echo(f"Warning: Could not find a year in '{pdf_file}', skipping.")
            continue
        year = year_match.group(0)

        exam_type = None
        if "adwokack" in pdf_file or "radcow" in pdf_file:
            exam_type = "adwokacki_radcowy"
        elif "komornic" in pdf_file:
            exam_type = "komorniczy"
        elif "notarialn" in pdf_file:
            exam_type = "notarialny"

        if not exam_type:
            typer.echo(f"Warning: Could not determine exam type for '{pdf_file}', skipping.")
            continue

        if year not in exams:
            exams[year] = {}
        if exam_type not in exams[year]:
            exams[year][exam_type] = {}

        if pdf_file.startswith("Zestaw_pytań"):
            exams[year][exam_type]["questions_pdf"] = pdf_file
        elif pdf_file.startswith("Wykaz_prawidłowych_odpowiedzi"):
            exams[year][exam_type]["answers_pdf"] = pdf_file

    for year, types in exams.items():
        for exam_type, files in types.items():
            typer.echo(f"Processing exam: Year - {year}, Type - {exam_type}")

            root_dir = Path(__file__).parent.parent
            output_dir = root_dir / "data" / "exams" / exam_type
            os.makedirs(output_dir, exist_ok=True)

            parsed_questions = None
            parsed_answers = None

            if "questions_pdf" in files:
                questions_pdf_path = os.path.join(pdf_dir, files["questions_pdf"])
                parsed_questions = parse_questions(questions_pdf_path, validate=validate)
                typer.echo(
                    f"  - Successfully parsed {len(parsed_questions['questions'])} questions."
                )

                if "invalid_questions" in parsed_questions:
                    typer.echo(
                        f"    Warning: {len(parsed_questions['invalid_questions'])} invalid questions found"
                    )
            else:
                typer.echo("  - Warning: Questions file not found for this exam.")
                continue

            if "answers_pdf" in files:
                answers_pdf_path = os.path.join(pdf_dir, files["answers_pdf"])
                parsed_answers = parse_answers(answers_pdf_path, validate=validate)
                typer.echo(
                    f"  - Successfully parsed {len(parsed_answers['answers'])} answers."
                )
            else:
                typer.echo("  - Warning: Answers file not found for this exam.")
                parsed_answers = {"answers": []}

            unified_data = create_unified_jsonl(
                parsed_questions["questions"],
                parsed_answers["answers"],
                exam_type,
                year,
            )

            unified_path = output_dir / f"{year}.jsonl"
            save_as_jsonl(unified_data, str(unified_path))
            typer.echo(f"  - Saved unified format: {unified_path}")

            if stats:
                stats_data = generate_statistics(parsed_questions)
                stats_data["year"] = year
                stats_data["exam_type"] = exam_type
                stats_path = output_dir / f"stats_{year}.json"
                with open(stats_path, "w", encoding="utf-8") as f:
                    json.dump(stats_data, f, ensure_ascii=False, indent=2)
                typer.echo(f"    Statistics saved to {stats_path}")


if __name__ == "__main__":
    app()
