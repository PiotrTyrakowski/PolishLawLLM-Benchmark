import json
from pathlib import Path
from typing import List
from enum import Enum


from benchmark_framework.calculate_stats import calculate_stats
from firebase.types import (
    ModelDocument,
    FirebaseCollection,
    ExamDocument,
    JudgmentDocument,
)
from firebase.main import firestore_db


class ExamType(str, Enum):
    ADWOKACKI_RADCOWY = "adwokacki_radcowy"
    KOMORNICZY = "komorniczy"
    NOTARIALNY = "notarialny


class Uploader:
    def __init__(
        self,
        db,
        path: Path | str,
        collection_id: str,
    ):
        self.path = Path(path)
        self.db = db
        self.root_collection = FirebaseCollection(id=collection_id)
        self._build_tree()

    def upload(self):
        self.root_collection.upload(self.db)

    def _build_tree(self):
        """
        Traverses: /results/{model_name}/
        """

        assert (
            self.path.exists() and self.path.is_dir()
        ), "Path does not exist or is not a directory"

        for model_dir in self.path.iterdir():
            json_files = list(model_dir.glob("*.json"))
            assert (
                len(json_files) == 1
            ), "There should be exactly one json file representing model fields"

            model_fields_path = json_files[0]
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
        if not exams_root.exists():
            return

        docs = [
            self.create_exam_document(f)
            for d in exams_root.iterdir()
            for f in d.glob("*.jsonl")
        ]

        if not docs:
            return

        exam_coll = FirebaseCollection(id="exams")
        for doc in docs:
            exam_coll.add_document(doc)

        avg_doc = self.create_avg_exam_document(docs)
        exam_coll.add_document(avg_doc)
        model_doc.add_collection(exam_coll)

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
            assert exam_type in EXAM_TYPES, f"Invalid exam type: {exam_type}"

            year = int(jsonl_path.parent.name)
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

        assert exam_documents, "Exam documents list cannot be empty"

        def avg_metrics(name: str) -> dict:
            keys = exam_documents[0].fields[name].keys()
            sum_d = {k: 0 for k in keys}

            for doc in exam_documents:
                assert keys == doc.fields[name].keys(), f"Keys mismatch for {name}"
                for k in keys:
                    sum_d[k] += doc.fields[name][k]

            return {k: v / len(exam_documents) for k, v in sum_d.items()}

        return ExamDocument(
            id="all",
            fields={
                "accuracy_metrics": avg_metrics("accuracy_metrics"),
                "text_metrics": avg_metrics("text_metrics"),
                "type": "all",
                "year": "all",
            },
        )

    @staticmethod
    def create_judgment_document(json_path: Path) -> JudgmentDocument:  # TODO:
        """
        Creates a JudgmentDocument instance from a given JSON file.
        """
        pass


if __name__ == "__main__":
    u = Uploader(
        firestore_db,
        "/Users/piotrtyrakowski/repos/PolishLawLLM-Benchmark/data/results_with_metrics_test",
        "test_results",
    )

    u.upload()
