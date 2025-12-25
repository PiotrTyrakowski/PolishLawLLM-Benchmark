import json
from pathlib import Path
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

        for year_dir in exams_root.iterdir():
            for jsonl_file in year_dir.glob("*.jsonl"):
                exam_doc = self.create_exam_document(jsonl_file)
                exam_coll.add_document(exam_doc)

        model_doc.add_collection(exam_coll)

    @staticmethod
    def create_model_document(json_path: Path) -> ModelDocument:
        with open(json_path, "r") as f:
            data = json.load(f)

        doc_id = json_path.stem
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


if __name__ == "__main__":
    u = Uploader(
        firestore_db,
        "/Users/piotrtyrakowski/repos/PolishLawLLM-Benchmark/data/results_with_metrics_test",
        "test_results",
    )

    u.upload()
