from pathlib import Path
from parsers_refactored.domain.exam import Exam, ExamTask
from parsers_refactored.repositories.exam_repository import ExamRepository
from parsers_refactored.utils.file_utils import FileOperations


class JSONLRepository(ExamRepository):
    """JSONL file-based exam repository."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.file_ops = FileOperations()

    def save(self, exam: Exam) -> None:
        output_dir = self.base_dir / exam.exam_type
        output_file = output_dir / f"{exam.year}.jsonl"

        data = exam.to_jsonl_data()
        self.file_ops.save_jsonl(data, output_file)

    def load(self, exam_type: str, year: int) -> Exam:
        file_path = self.base_dir / exam_type / f"{year}.jsonl"
        data = self.file_ops.load_jsonl(file_path)

        tasks = [ExamTask.from_dict(task_data) for task_data in data]
        return Exam(year=year, exam_type=exam_type, tasks=tasks)
