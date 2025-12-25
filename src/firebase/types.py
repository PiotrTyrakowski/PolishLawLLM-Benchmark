from typing import Dict, Any, Set
from pydantic import BaseModel, model_validator

class FirebaseCollection(BaseModel):
    id: str
    documents: Dict[str, "FirebaseDocument"] = {}

    def upload(self, db, parent_path: str = ""):
        collection_path = f"{parent_path}/{self.id}" if parent_path else self.id
        collection_ref = db.collection(collection_path)

        for doc_id, doc in self.documents.items():
            doc_ref = collection_ref.document(doc_id)
            doc_ref.set(doc.fields)

            # Recursively upload nested collections
            for nested_collection in doc.collections.values():
                nested_collection.upload(db, f"{collection_path}/{doc_id}")

    def add_document(self, document: "FirebaseDocument"):
        self.documents[document.id] = document


class FirebaseDocument(BaseModel):
    id: str
    fields: Dict[str, Any] = {}
    collections: Dict[str, "FirebaseCollection"] = {}
    required_fields: Set[str] = set()  # Override in subclasses

    @model_validator(mode="after")
    def validate_fields(self):
        if self.required_fields and not self.required_fields.issubset(
            self.fields.keys()
        ):
            missing = self.required_fields - self.fields.keys()
            raise ValueError(f"Missing fields: {missing} from document {self.id}")
        return self

    def add_collection(self, collection: "FirebaseCollection"):
        self.collections[collection.id] = collection


class ExamDocument(FirebaseDocument):
    required_fields: Set[str] = {"accuracy_metrics", "text_metrics", "type", "year"}


class JudgmentDocument(FirebaseDocument):
    required_fields: Set[str] = {"accuracy_metrics", "text_metrics"}


class ModelDocument(FirebaseDocument):
    required_fields: Set[str] = {"model_name", "is_polish", "model_config"}
