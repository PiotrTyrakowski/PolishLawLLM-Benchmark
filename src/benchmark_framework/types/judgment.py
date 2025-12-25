import json
from pathlib import Path
from typing import TypedDict

from src.benchmark_framework.types.task import Task
from src.benchmark_framework.constants import ENCODING


class JudgmentResult(TypedDict):
    id: int
    judgment_link: str
    legal_basis: str
    legal_basis_content: str

    model_name: str
    model_config: str
    model_response: str
    model_legal_basis: str
    model_legal_basis_content: str


# TODO: align with future implementaion of judgments with metrics
class Judgment(Task):
    """
    Represents a legal judgment with masked legal references.

    Contains masked justification text where legal article references have been removed,
    and the expected article reference and content that should be identified.
    """

    def __init__(
        self,
        id,
        judgment_link,
        masked_justification_text,
        legal_basis,
        legal_basis_content,
    ):
        super().__init__(id=id)
        self.judgment_link = judgment_link
        self.masked_justification_text = masked_justification_text
        self.legal_basis = legal_basis
        self.legal_basis_content = legal_basis_content

    @classmethod
    def from_dict(cls, data: dict):
        # Handle both masked_judgment_text and masked_justification_text field names
        masked_text = data.get("masked_justification_text") or data.get(
            "masked_judgment_text"
        )
        return cls(
            data["id"],
            data["judgment_link"],
            masked_text,
            data["legal_basis"],
            data["legal_basis_content"],
        )

    def get_prompt(self) -> str:
        """
        Get the prompt for the judgment task.
        Returns the masked justification text that needs to be analyzed.
        """
        return self.masked_justification_text

    def get_year(self) -> int:
        # TODO: implement year extraction if needed
        return 2025


def load_judgments(jsonl_path: Path) -> list["Judgment"]:
    judgments = []
    with open(jsonl_path, encoding=ENCODING) as f:
        for line in f:
            obj = json.loads(line)
            judgments.append(Judgment.from_dict(obj))
    return judgments
