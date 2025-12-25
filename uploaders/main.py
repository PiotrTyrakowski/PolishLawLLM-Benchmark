"""
Main upload logic for exam results to Firebase.

This module handles:
1. Discovering model directories in results_with_metrics/exams/
2. Reading and parsing JSONL result files
3. Aggregating metrics per exam (year + exam_type)
4. Uploading to Firestore in the format expected by the frontend
"""

import json
from pathlib import Path
from typing import Optional

from google.cloud import firestore

from uploaders.types.exams import (
    ExamResultEntry,
    FirestoreExamDoc,
    FirestoreModelDoc,
    FirestoreAccuracyMetrics,
    FirestoreTextMetrics,
    ModelDirectory,
    ExamFile,
)


# Known Polish models - add model IDs here
POLISH_MODELS = {
    "bielik",
    "CYFRAGOVPL__PLLuM-12B-instruct",
    "speakleash__Bielik-11B-v2.3-Instruct",
}


def discover_models(base_path: Path) -> list[ModelDirectory]:
    """
    Discover all model directories under the base path.
    
    Handles both flat (e.g., bielik/) and nested (e.g., CYFRAGOVPL/PLLuM-12B-instruct/)
    directory structures.
    
    Args:
        base_path: Path to results_with_metrics/exams/
        
    Returns:
        List of ModelDirectory objects
    """
    models = []
    
    def has_year_subdirs(path: Path) -> bool:
        """Check if directory contains year subdirectories."""
        return any(
            d.is_dir() and d.name.isdigit() and len(d.name) == 4
            for d in path.iterdir()
        )
    
    def scan_directory(current_path: Path):
        """Recursively scan for model directories."""
        if not current_path.is_dir():
            return
            
        # If this directory has year subdirs, it's a model directory
        if has_year_subdirs(current_path):
            model = ModelDirectory.from_path(base_path, current_path)
            if model.exam_files:  # Only add if there are actual exam files
                models.append(model)
        else:
            # Otherwise, scan subdirectories
            for subdir in current_path.iterdir():
                if subdir.is_dir() and not subdir.name.startswith('.'):
                    scan_directory(subdir)
    
    scan_directory(base_path)
    return models


def read_exam_results(exam_file: ExamFile) -> list[ExamResultEntry]:
    """
    Read and parse a JSONL exam results file.
    
    Args:
        exam_file: ExamFile object with path information
        
    Returns:
        List of ExamResultEntry objects
    """
    results = []
    with open(exam_file.path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                data = json.loads(line)
                results.append(ExamResultEntry.model_validate(data))
    return results


def aggregate_exam_metrics(results: list[ExamResultEntry]) -> FirestoreExamDoc:
    """
    Aggregate metrics from individual question results into exam-level metrics.
    
    Args:
        results: List of individual question results
        
    Returns:
        FirestoreExamDoc with averaged metrics
    """
    if not results:
        raise ValueError("Cannot aggregate empty results list")
    
    n = len(results)
    
    # Calculate averages
    avg_answer = sum(r.accuracy_metrics.answer for r in results) / n
    avg_legal_basis = sum(r.accuracy_metrics.legal_basis for r in results) / n
    avg_exact_match = sum(r.text_metrics.exact_match for r in results) / n
    avg_bleu = sum(r.text_metrics.bleu for r in results) / n
    avg_weighted_bleu = sum(r.text_metrics.weighted_bleu for r in results) / n
    
    # Use first result to get exam metadata (they should all be the same)
    first = results[0]
    
    return FirestoreExamDoc(
        accuracy_metrics=FirestoreAccuracyMetrics(
            answer=avg_answer,
            identification=avg_legal_basis,  # Rename legal_basis -> identification
        ),
        text_metrics=FirestoreTextMetrics(
            exact_match=avg_exact_match,
            bleu=avg_bleu,
            weighted_bleu=avg_weighted_bleu,
        ),
        type=first.exam_type,
        year=first.year,
    )


def is_polish_model(model_id: str, model_name: str) -> bool:
    """
    Determine if a model is a Polish model.
    
    Can be extended to use more sophisticated detection.
    """
    model_id_lower = model_id.lower()
    model_name_lower = model_name.lower()
    
    # Check explicit list
    if model_id in POLISH_MODELS:
        return True
    
    # Check for common Polish model indicators
    polish_indicators = ['bielik', 'pllum', 'polish', 'pl-']
    return any(
        indicator in model_id_lower or indicator in model_name_lower
        for indicator in polish_indicators
    )


class ResultsUploader:
    """
    Uploads exam results to Firestore.
    
    Handles the full workflow:
    1. Discover models in the source directory
    2. Read and aggregate results
    3. Upload to Firestore
    """
    
    def __init__(
        self,
        source_path: Path,
        collection_name: str = "results",
        dry_run: bool = False,
    ):
        """
        Initialize the uploader.
        
        Args:
            source_path: Path to results_with_metrics/exams/
            collection_name: Firestore collection name
            dry_run: If True, don't actually upload to Firestore
        """
        self.source_path = source_path
        self.collection_name = collection_name
        self.dry_run = dry_run
        self._db: Optional[firestore.Client] = None
    
    @property
    def db(self) -> firestore.Client:
        """Lazy initialization of Firestore client."""
        if self._db is None:
            self._db = firestore.Client()
        return self._db
    
    def discover_models(self) -> list[ModelDirectory]:
        """Discover all models in the source path."""
        return discover_models(self.source_path)
    
    def upload_model(
        self,
        model: ModelDirectory,
        verbose: bool = True,
    ) -> tuple[int, int]:
        """
        Upload a single model's results to Firestore.
        
        Args:
            model: ModelDirectory to upload
            verbose: Print progress messages
            
        Returns:
            Tuple of (exams_uploaded, questions_processed)
        """
        exams_uploaded = 0
        questions_processed = 0
        
        # Create/update model document
        model_doc = FirestoreModelDoc(
            model_name=model.model_name,
            is_polish_model=is_polish_model(model.model_id, model.model_name),
        )
        
        if verbose:
            print(f"\nUploading model: {model.model_name} (id: {model.model_id})")
            print(f"  Polish model: {model_doc.is_polish_model}")
            print(f"  Exam files: {len(model.exam_files)}")
        
        if not self.dry_run:
            # Upload model document
            model_ref = self.db.collection(self.collection_name).document(model.model_id)
            model_ref.set(model_doc.to_dict())
        
        # Process each exam file
        for exam_file in model.exam_files:
            try:
                # Read results
                results = read_exam_results(exam_file)
                if not results:
                    if verbose:
                        print(f"  ⚠ Skipping empty file: {exam_file.path}")
                    continue
                
                questions_processed += len(results)
                
                # Aggregate metrics
                exam_doc = aggregate_exam_metrics(results)
                
                # Create exam document ID
                exam_doc_id = f"{exam_file.exam_type}_{exam_file.year}"
                
                if verbose:
                    print(f"  ✓ {exam_doc_id}: {len(results)} questions, "
                          f"accuracy={exam_doc.accuracy_metrics.answer:.2%}")
                
                if not self.dry_run:
                    # Upload exam document
                    exam_ref = (
                        self.db.collection(self.collection_name)
                        .document(model.model_id)
                        .collection("exams")
                        .document(exam_doc_id)
                    )
                    exam_ref.set(exam_doc.to_dict())
                
                exams_uploaded += 1
                
            except Exception as e:
                if verbose:
                    print(f"  ✗ Error processing {exam_file.path}: {e}")
        
        return exams_uploaded, questions_processed
    
    def upload_all(self, verbose: bool = True) -> tuple[int, int, int]:
        """
        Upload all models' results to Firestore.
        
        Args:
            verbose: Print progress messages
            
        Returns:
            Tuple of (models_uploaded, exams_uploaded, questions_processed)
        """
        models = self.discover_models()
        
        if verbose:
            print(f"Discovered {len(models)} model(s) in {self.source_path}")
            if self.dry_run:
                print("DRY RUN - no data will be uploaded")
        
        total_models = 0
        total_exams = 0
        total_questions = 0
        
        for model in models:
            exams, questions = self.upload_model(model, verbose=verbose)
            total_models += 1
            total_exams += exams
            total_questions += questions
        
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"Upload complete!")
            print(f"  Models: {total_models}")
            print(f"  Exams: {total_exams}")
            print(f"  Questions processed: {total_questions}")
            print(f"{'=' * 60}")
        
        return total_models, total_exams, total_questions

