from pathlib import Path
from src.uploaders.main import Uploader
from src.firebase.types import ExamDocument

def test_create_avg_exam_document():
    docs = [
        ExamDocument(
            id="exam1",
            fields={
                "accuracy_metrics": {"acc": 0.5, "f1": 0.4},
                "text_metrics": {"len": 100},
                "type": "adwokacki_radcowy",
                "year": 2023
            }
        ),
        ExamDocument(
            id="exam2",
            fields={
                "accuracy_metrics": {"acc": 0.7, "f1": 0.6},
                "text_metrics": {"len": 200},
                "type": "komorniczy",
                "year": 2024
            }
        )
    ]
    
    try:
        avg_doc = Uploader.create_avg_exam_document(docs)
        print("Success!")
        print(avg_doc.fields)
    except Exception as e:
        print(f"Failed with error: {e}")

if __name__ == "__main__":
    test_create_avg_exam_document()
