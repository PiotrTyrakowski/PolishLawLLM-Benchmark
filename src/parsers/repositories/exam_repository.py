from abc import ABC, abstractmethod
from src.parsers.domain.exam import Exam


class ExamRepository(ABC):
    """Abstract repository for exam persistence."""

    @abstractmethod
    def save(self, exam: Exam) -> None:
        """Save exam to storage."""
        pass

    @abstractmethod
    def load(self, exam_type: str, year: int) -> Exam:
        """Load exam from storage."""
        pass
