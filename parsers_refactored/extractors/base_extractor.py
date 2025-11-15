from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseExtractor(ABC):
    """Abstract base class for text extractors."""

    @abstractmethod
    def extract(self, text: str) -> List[Dict[str, Any]]:
        """Extract structured data from text."""
        pass
