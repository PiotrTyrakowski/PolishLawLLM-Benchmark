"""
Pydantic models for exam results data - used for reading from JSONL files
and uploading to Firebase.
"""

from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class FirestoreExamDoc(BaseModel):
    """Document structure for individual exam in Firebase."""
    accuracy_metrics: dict
    text_metrics: dict
    type: str  # exam_type
    year: int

    def to_dict(self) -> dict:
        return {
            "accuracy_metrics": self.accuracy_metrics,
            "text_metrics": self.text_metrics,
            "type": self.type,
            "year": self.year,
        }


class FirestoreModelDoc(BaseModel):
    """Document structure for model in Firebase."""
    model_name: str
    is_polish_model: bool = False

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "is_polish_model": self.is_polish_model,
        }


# ============= Helper Models for Directory Structure =============

class ExamFile(BaseModel):
    """Represents a single exam JSONL file."""
    path: Path
    year: int
    exam_type: str
    
    @classmethod
    def from_path(cls, path: Path) -> "ExamFile":
        """Create ExamFile from a path like .../2016/adwokacki_radcowy.jsonl"""
        return cls(
            path=path,
            year=int(path.parent.name),
            exam_type=path.stem,  # filename without extension
        )


class ModelDirectory(BaseModel):
    """Represents a model's directory containing year subdirectories."""
    model_id: str  # Used as document ID in Firebase (e.g., "bielik" or "CYFRAGOVPL__PLLuM-12B-instruct")
    model_name: str  # Human readable name
    path: Path
    exam_files: list[ExamFile] = Field(default_factory=list)
    
    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def from_path(cls, base_path: Path, model_path: Path) -> "ModelDirectory":
        """
        Create ModelDirectory from paths.
        
        Args:
            base_path: The root results_with_metrics/exams path
            model_path: The specific model directory path
        """
        # Get relative path from base to create model_id
        relative = model_path.relative_to(base_path)
        # Convert path parts to ID (replace / with __)
        model_id = "__".join(relative.parts)
        model_name = "/".join(relative.parts)
        
        # Discover all exam files
        exam_files = []
        for year_dir in sorted(model_path.iterdir()):
            if year_dir.is_dir() and year_dir.name.isdigit():
                for jsonl_file in sorted(year_dir.glob("*.jsonl")):
                    exam_files.append(ExamFile.from_path(jsonl_file))
        
        return cls(
            model_id=model_id,
            model_name=model_name,
            path=model_path,
            exam_files=exam_files,
        )
