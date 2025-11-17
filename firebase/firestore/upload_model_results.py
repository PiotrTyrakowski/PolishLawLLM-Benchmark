import json
import sys
import os
import typer
from google.cloud import firestore
from constants import ROOT_PATH

app = typer.Typer()


@app.command()
def upload_model_results_to_firestore(
    model_file: str = typer.Argument(
        None,
        help="Optional specific model file to upload (without .jsonl extension). If None, uploads all JSONL files in results/exams/",
    )
):
    """
    Upload model results from JSONL files in results/exams folder to Firestore.
    """
    try:
        # Initialize Firestore client
        db = firestore.Client()
        total_uploaded = 0

        # Get results directory path
        results_dir = ROOT_PATH / "results" / "exams"

        if not os.path.exists(results_dir):
            typer.echo(f"Error: Results directory not found: {results_dir}")
            raise typer.Exit(code=1)

        # Get list of JSONL files to process
        if model_file:
            jsonl_files = [f"{model_file}.jsonl"]
        else:
            jsonl_files = [f for f in os.listdir(results_dir) if f.endswith(".jsonl")]

        if not jsonl_files:
            typer.echo("No JSONL files found in results/exams directory")
            raise typer.Exit()

        for jsonl_file in jsonl_files:
            jsonl_path = results_dir / jsonl_file

            if not os.path.exists(jsonl_path):
                typer.echo(f"Warning: File not found: {jsonl_path}")
                continue

            # Extract model name from filename (remove .jsonl extension)
            model_name = jsonl_file.replace(".jsonl", "")

            # Read JSONL file
            model_results = []
            with open(jsonl_path, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        model_results.append(json.loads(line))

            typer.echo(f"Found {len(model_results)} entries in {jsonl_path}")

            if not model_results:
                typer.echo(f"No data found in {jsonl_path}")
                continue

            # Group results by exam_type and year
            grouped_results = {}
            for result in model_results:
                exam_type = result.get("exam_type", "unknown")
                year = result.get("year", "unknown")
                key = f"{exam_type}_{year}"

                if key not in grouped_results:
                    grouped_results[key] = []
                grouped_results[key].append(result)

            # Prepare stats data for all exams
            all_stats = {}

            # Upload each group to its own collection and calculate stats
            for exam_key, results in grouped_results.items():
                # Create collection reference: results/{model_name}/exams/{exam_type}_{year}
                collection_ref = (
                    db.collection("results")
                    .document(model_name)
                    .collection("exams")
                    .document(exam_key)
                    .collection("responses")
                )

                # Upload data in batches (Firestore batch limit is 500)
                batch_size = 500
                uploaded_count = 0

                for i in range(0, len(results), batch_size):
                    batch = db.batch()
                    batch_data = results[i : i + batch_size]

                    for item in batch_data:
                        # Use a combination of question hash or index as document ID
                        doc_id = str(uploaded_count + 1).zfill(4)
                        doc_ref = collection_ref.document(doc_id)
                        batch.set(doc_ref, item)
                        uploaded_count += 1

                    # Commit the batch
                    batch.commit()
                    typer.echo(
                        f"  Uploaded batch {i//batch_size + 1}: {len(batch_data)} documents to results/{model_name}/exams/{exam_key}"
                    )

                typer.echo(
                    f"Successfully uploaded {uploaded_count} documents to collection: results/{model_name}/exams/{exam_key}"
                )
                total_uploaded += uploaded_count

                # Calculate stats for this exam
                correct_responses = sum(
                    1 for result in results if result.get("is_correct", False)
                )
                total_responses = len(results)
                accuracy = (
                    round(correct_responses / total_responses, 4)
                    if total_responses > 0
                    else 0
                )

                all_stats[exam_key] = {
                    "correct_responses": correct_responses,
                    "total_responses": total_responses,
                    "accuracy": accuracy,
                }

                typer.echo(
                    f"  Stats: {correct_responses}/{total_responses} correct ({accuracy*100:.2f}%)"
                )

            # Upload all stats as one document
            if all_stats:
                stats_ref = (
                    db.collection("results")
                    .document(model_name)
                    .collection("stats")
                    .document("exams")
                )
                stats_ref.set(all_stats)
                typer.echo(
                    f"Uploaded stats document to results/{model_name}/stats/exams"
                )

        typer.echo(
            f"\nTotal uploaded: {total_uploaded} documents across all model results"
        )

    except Exception as e:
        typer.echo(f"Error: {str(e)}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
