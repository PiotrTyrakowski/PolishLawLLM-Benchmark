from pydantic import BaseModel, Field
from typing import Annotated, Dict

# model.model_dump()
# model.model_dump_json()

class ExamDocument(BaseModel):
    accuracy_metrics: Dict[str, float]
    text_metics: Dict[str, float]
    type: str
    year: int

class JudgmentDocument(BaseModel):
    accuracy_metrics: Dict[str, float]
    text_metics: Dict[str, float]

    @classmethod
    def from_path(cls, path: Path) -> "ExamFile":
        """Create ExamFile from a path like .../2016/adwokacki_radcowy.jsonl"""
        return cls(
            path=path,
            year=int(path.parent.name),
            exam_type=path.stem,  # filename without extension
        )

class ModelDocument(BaseModel):
    model_name: str
    is_polish: bool
    exams: Dict[str, ExamDocument]
    judgments: Dict[str, JudgmentDocument]

    @classmethod
    def from_path(cls, path: Path) -> "ExamFile":
        """Create ExamFile from a path like .../2016/adwokacki_radcowy.jsonl"""
        return cls(
            path=path,
            year=int(path.parent.name),
            exam_type=path.stem,  # filename without extension
        )
