import json
from pathlib import Path
from benchmark_framework.types.task import Task
from benchmark_framework.constants import ENCODING


# TODO: align with future implementaion of judgments with metrics
class Judgment(Task):
    """
    Represents a legal judgment with masked legal references.

    Contains masked justification text where legal article references have been removed,
    and the expected article reference and content that should be identified.
    """

    def __init__(self, id, judgment_link, masked_justification_text, legal_basis, legal_basis_content):
        super().__init__()
        self.id = id
        self.judgment_link = judgment_link
        self.masked_justification_text = masked_justification_text
        self.legal_basis = legal_basis
        self.legal_basis_content = legal_basis_content

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["id"],
            data["judgment_link"],
            data["masked_justification_text"],
            data["legal_basis"],
            data["legal_basis_content"],
        )

    def get_prompt(self) -> str:
        """
        Get the prompt for the judgment task.
        Returns the masked justification text that needs to be analyzed.
        """
        return self.masked_justification_text

def load_judgments(jsonl_path: Path) -> list["Judgment"]:
    judgments = []
    with open(jsonl_path, encoding=ENCODING) as f:
        for line in f:
            obj = json.loads(line)
            judgments.append(
                Judgment(
                    obj["id"],
                    obj["judgment_link"],
                    obj["masked_justification_text"],
                    obj["legal_basis"],
                    obj["legal_basis_content"],
                )
            )
    return judgments

