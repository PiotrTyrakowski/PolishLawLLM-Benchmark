import json
import logging
from pathlib import Path
from typing import Dict, List

from src.benchmark_framework.calculate_stats import calculate_stats
from src.firebase.types import (
    ModelDocument,
    FirebaseCollection,
    ExamDocument,
    JudgmentDocument,
)

EXAM_TYPES: List[str] = ["adwokacki_radcowy", "komorniczy", "notarialny"]

logger = logging.getLogger(__name__)


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
        self._validate_path()
        self._build_tree()

    def _validate_path(self) -> None:
        if not self.path.exists():
            raise FileNotFoundError(f"Path does not exist: {self.path}")
        if not self.path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self.path}")

    def upload(self) -> None:
        logger.info(f"Uploading collection '{self.root_collection.id}' to Firestore")
        self.root_collection.upload(self.db)
        logger.info("Upload complete")

        for model_id in self.root_collection.documents.keys():
            self._sync_all_exam_aggregate(model_id)

    def _sync_all_exam_aggregate(self, model_id: str) -> None:
        """Fetches all exam docs from Firebase for a model and creates/updates 'all' aggregate."""
        exams_path = f"{self.root_collection.id}/{model_id}/exams"
        exams_ref = self.db.collection(exams_path)
        docs = exams_ref.stream()

        exam_data: List[Dict] = []
        for doc in docs:
            if doc.id == "all":
                continue
            exam_data.append(doc.to_dict())

        if not exam_data:
            logger.warning(f"No exam documents found for model {model_id}")
            return

        averaged = self._average_metrics(exam_data)

        all_doc = ExamDocument(
            id="all",
            fields={
                "accuracy_metrics": averaged["accuracy_metrics"],
                "text_metrics": averaged["text_metrics"],
                "type": "all",
                "year": "all",
            },
        )

        doc_ref = exams_ref.document("all")
        doc_ref.set(all_doc.fields)
        logger.info(f"Created 'all' aggregate document for model {model_id}")

    @staticmethod
    def _average_metrics(docs: List[Dict]) -> Dict[str, Dict]:
        """Averages accuracy_metrics and text_metrics across documents dynamically."""
        if not docs:
            return {"accuracy_metrics": {}, "text_metrics": {}}

        accuracy_sums: Dict[str, List] = {}
        text_sums: Dict[str, List] = {}

        for doc in docs:
            for key, value in doc.get("accuracy_metrics", {}).items():
                if key not in accuracy_sums:
                    accuracy_sums[key] = []
                accuracy_sums[key].append(value)

            for key, value in doc.get("text_metrics", {}).items():
                if key not in text_sums:
                    text_sums[key] = []
                text_sums[key].append(value)

        return {
            "accuracy_metrics": {k: sum(v) / len(v) for k, v in accuracy_sums.items()},
            "text_metrics": {k: sum(v) / len(v) for k, v in text_sums.items()},
        }

    def _build_tree(self) -> None:
        """Traverses: /results/{model_id}/"""
        for model_dir in self.path.iterdir():
            if not model_dir.is_dir():
                logger.warning(f"Skipping non-directory: {model_dir}")
                continue

            json_files = list(model_dir.glob("*.json"))
            if len(json_files) != 1:
                raise ValueError(
                    f"Expected exactly one JSON file in {model_dir}, found {len(json_files)}"
                )

            model_fields_path = json_files[0]
            model_doc = self._create_model_document(model_fields_path)
            logger.info(f"Processing model: {model_doc.id}")

            self._process_exams(model_dir, model_doc)
            self._process_judgments(model_dir, model_doc)

            self.root_collection.add_document(model_doc)

    def _process_exams(self, model_dir: Path, model_doc: ModelDocument) -> None:
        """Traverses: /results/model_id/exams/{year}/{test}.jsonl"""
        exams_root = model_dir / "exams"

        if not exams_root.exists():
            logger.debug(f"No exams directory found in {model_dir}")
            return

        docs: list[ExamDocument] = []
        for year_dir in exams_root.iterdir():
            if not year_dir.is_dir():
                continue
            for jsonl_file in year_dir.glob("*.jsonl"):
                try:
                    doc = self._create_exam_document(jsonl_file)
                    docs.append(doc)
                    logger.debug(f"Created exam document: {doc.id}")
                except ValueError as e:
                    logger.error(f"Failed to process {jsonl_file}: {e}")

        if not docs:
            logger.warning(f"No valid exam documents found in {exams_root}")
            return

        exam_coll = FirebaseCollection(id="exams")
        for doc in docs:
            exam_coll.add_document(doc)

        model_doc.add_collection(exam_coll)
        logger.info(f"Added {len(docs)} exam documents")

    def _process_judgments(self, model_dir: Path, model_doc: ModelDocument) -> None:
        """Traverses: /results/model_id/judgments/all.jsonl"""
        judgments_root = model_dir / "judgments"

        if not judgments_root.exists():
            logger.debug(f"No judgments directory found in {model_dir}")
            return

        jsonl_file = judgments_root / "all.jsonl"
        if not jsonl_file.exists():
            logger.warning(f"No all.jsonl found in {judgments_root}")
            return

        try:
            doc = self._create_judgment_document(jsonl_file)
            logger.debug(f"Created judgment document: {doc.id}")
        except ValueError as e:
            logger.error(f"Failed to process {jsonl_file}: {e}")
            return

        judgment_coll = FirebaseCollection(id="judgments")
        judgment_coll.add_document(doc)

        model_doc.add_collection(judgment_coll)
        logger.info("Added judgment document")

    @staticmethod
    def _create_model_document(json_path: Path) -> ModelDocument:
        """Creates a ModelDocument instance from a given JSON file."""
        with open(json_path, "r", encoding="utf-8") as f:
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
    def _create_exam_document(jsonl_path: Path) -> ExamDocument:
        """Creates an ExamDocument instance from a given JSONL file."""
        exam_type = jsonl_path.stem

        if exam_type not in EXAM_TYPES:
            raise ValueError(
                f"Invalid exam type: '{exam_type}'. Expected one of {EXAM_TYPES}"
            )

        try:
            year = int(jsonl_path.parent.name)
        except ValueError:
            raise ValueError(f"Invalid year directory name: '{jsonl_path.parent.name}'")

        stats = calculate_stats(jsonl_path)
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

    @staticmethod
    def _create_judgment_document(jsonl_path: Path) -> JudgmentDocument:
        """Creates a JudgmentDocument instance from a given JSONL file."""
        stats = calculate_stats(jsonl_path)

        return JudgmentDocument(
            id="all",
            fields={
                "accuracy_metrics": stats["accuracy_metrics"],
                "text_metrics": stats["text_metrics"],
            },
        )
