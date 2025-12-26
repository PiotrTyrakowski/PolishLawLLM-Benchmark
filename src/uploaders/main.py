import json
from pathlib import Path
from typing import List

from benchmark_framework.calculate_stats import calculate_stats
from firebase.types import ModelDocument, FirebaseCollection, ExamDocument
from firebase.main import firestore_db


class Uploader:
    def __init__(
        self,
        db,
        path: Path | str,
        collection_id: str = "results",
    ):
        self.path = Path(path)
        self.db = db
        if not self.validate_dir_structure():
            raise ValueError(f"Invalid path structure provided: {path}")

        self.root_collection = FirebaseCollection(id=collection_id)
        self._build_tree()

    def upload(self):
        self.root_collection.upload(self.db)

    def validate_dir_structure(self):
        return True

    def _build_tree(self):
        """
        Traverses: /results/{model_name}/
        """

        for model_dir in self.path.iterdir():
            model_fields_path = list(model_dir.glob("*.json"))[0]
            model_doc = self.create_model_document(model_fields_path)

            # Look for exams: /results/model/exams/{year}/*.jsonl
            self._process_exams(model_dir, model_doc)

            # Look for judgments
            # TODO: implement _process_judgments

            self.root_collection.add_document(model_doc)

    def _process_exams(self, model_dir: Path, model_doc: ModelDocument):
        """
        Traverses: /results/model/exams/{year}/{test}.jsonl
        """

        exams_root = model_dir / "exams"
        exam_coll = FirebaseCollection(id="exams")
        docs = [
            self.create_exam_document(f)
            for d in exams_root.iterdir()
            for f in d.glob("*.jsonl")
        ]

        for doc in docs:
            exam_coll.add_document(doc)

        if docs:
            avg_doc = self.create_avg_exam_document(docs)
            exam_coll.add_document(avg_doc)

    @staticmethod
    def create_model_document(json_path: Path) -> ModelDocument:
        """
        Creates a ModelDocument instance from a given JSON file.
        """
        with open(json_path, "r") as f:
            data = json.load(f)

        doc_id = json_path.parent.name
        return ModelDocument(
            id=doc_id,
            fields={
                "model_name": data.get("model_name", doc_id),
                "is_polish": data.get("is_polish", False),
                "model_config": data.get("model_config", {}),
            },
        )

    @staticmethod
    def create_exam_document(jsonl_path: Path) -> ExamDocument:
        """
        Creates an ExamDocument instance from a given JSONL file.
        """
        try:
            stats = calculate_stats(jsonl_path)
            exam_type = jsonl_path.stem
            year = jsonl_path.parent.name
            doc_id = f"{exam_type}_{year}"
            return ExamDocument(
                id=doc_id,
                fields={
                    "accuracy_metrics": stats["accuracy_metrics"],
                    "text_metrics": stats["text_metrics"],
                    "type": exam_type,
                    "year": year,
                },
            )

        except Exception as e:
            raise ValueError(f"Failed to create exam document for {jsonl_path}: {e}")

    @staticmethod
    def create_avg_exam_document(exam_documents: List[ExamDocument]) -> ExamDocument:
        """
        Creates an averaged exam document by aggregating data across a list of exam documents.
        """
        avg = lambda keys, d_list: {
            k: sum(d[k] for d in d_list) / len(d_list) for k in keys
        }
        avg_accuracy_metrics = avg(
            exam_documents[0].fields["accuracy_metrics"].keys(),
            [d.fields["accuracy_metrics"] for d in exam_documents],
        )
        avg_text_metrics = avg(
            exam_documents[0].fields["text_metrics"].keys(),
            [d.fields["text_metrics"] for d in exam_documents],
        )

        all_fields = {
            "accuracy_metrics": avg_accuracy_metrics,
            "text_metrics": avg_text_metrics,
            "type": "all",
            "year": "all",
        }
        return ExamDocument(id="all", fields=all_fields)


if __name__ == "__main__":
    u = Uploader(
        firestore_db,
        "/Users/piotrtyrakowski/repos/PolishLawLLM-Benchmark/data/results_with_metrics_test",
        "test_results",
    )

    u.upload()
