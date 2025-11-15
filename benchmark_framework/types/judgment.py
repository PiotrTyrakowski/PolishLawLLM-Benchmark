import json
from pathlib import Path
from benchmark_framework.types.task import Task
from benchmark_framework.constants import ENCODING


# TODO: align with future implementaion of judgments with metrics
class Judgment(Task):
    """
    Represents a legal judgment with masked legal references.

    Contains masked judgment text where legal article references have been removed,
    and the expected article reference and content that should be identified.
    """

    def __init__(self, id, masked_text, expected_article, expected_content):
        super().__init__()
        self.id = id
        self.masked_text = masked_text
        self.expected_article = expected_article
        self.expected_content = expected_content

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["id"],
            data["masked_text"],
            data["expected_article"],
            data["expected_content"],
        )

    def get_prompt(self) -> str:
        """
        Get the prompt for the judgment task.
        Returns the masked text that needs to be analyzed.
        """
        return self.masked_text

# TODO
def load_judgments(jsonl_path: Path) -> list[Judgment]:
    pass
