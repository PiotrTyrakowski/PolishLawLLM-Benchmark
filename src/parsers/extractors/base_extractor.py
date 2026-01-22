from abc import ABC, abstractmethod


class BaseExtractor(ABC):
    """Abstract base class for text extractors."""

    @abstractmethod
    def extract(self, text: str):
        pass
