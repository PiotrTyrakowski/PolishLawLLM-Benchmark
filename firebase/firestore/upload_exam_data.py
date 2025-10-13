import json
import sys
import os
import typer
from google.cloud import firestore
from constants import ROOT_PATH

app = typer.Typer()


@app.command()
def upload_exam_data_to_firestore(
    year: str = typer.Argument(..., help='Year of the exam (e.g., "2024")')
):
    """
    Upload exam data from all JSONL files for a given year to Firestore.
    """
    exam_types = ["adwokacki_radcowy", "komorniczy", "notarialny"]

    try:
        # Initialize Firestore client
        db = firestore.Client()
        total_uploaded = 0

        for exam_type in exam_types:
            # Construct path to JSONL file
            jsonl_path = ROOT_PATH / "data" / "exams" / exam_type / f"{year}.jsonl"

            if not os.path.exists(jsonl_path):
                typer.echo(f"Warning: File not found: {jsonl_path}")
                continue

            # Read JSONL file
            exam_data = []
            with open(jsonl_path, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        exam_data.append(json.loads(line))

            typer.echo(f"Found {len(exam_data)} entries in {jsonl_path}")

            # Create collection reference
            collection_ref = (
                db.collection("data")
                .document("exams")
                .collection(f"{exam_type}_{year}")
            )

            # Upload data in batches (Firestore batch limit is 500)
            batch_size = 500
            uploaded_count = 0

            for i in range(0, len(exam_data), batch_size):
                batch = db.batch()
                batch_data = exam_data[i : i + batch_size]

                for item in batch_data:
                    # Format document ID with leading zeros (3 digits)
                    doc_id = str(item.get("id", uploaded_count + 1)).zfill(3)
                    doc_ref = collection_ref.document(doc_id)
                    batch.set(doc_ref, item)
                    uploaded_count += 1

                # Commit the batch
                batch.commit()
                typer.echo(f"  Uploaded batch {i//batch_size + 1}: {len(batch_data)} documents")

            typer.echo(
                f"Successfully uploaded {uploaded_count} documents to collection: data/exams/{exam_type}_{year}"
            )
            total_uploaded += uploaded_count

        typer.echo(f"\nTotal uploaded: {total_uploaded} documents across all exam types")

    except Exception as e:
        typer.echo(f"Error: {str(e)}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()