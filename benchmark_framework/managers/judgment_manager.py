import json
import re
from pathlib import Path
from dataclasses import asdict

from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.types.judgment import Judgment
from benchmark_framework.managers.base_manager import BaseManager
from benchmark_framework.constants import DATA_PATH


def extract_judgment_answer(response_text: str) -> dict:
    """
    Extract answer from model response in JSON format: {art: '...', content: '...'}
    Returns:
        Dictionary with 'art' and 'content' keys, or empty dict if parsing fails
    """
    response_text = response_text.strip()
    
    # Try to find JSON block in the response
    # Look for {art: ...} or {"art": ...} pattern
    
    # Try to find JSON object
    json_match = re.search(r'\{[^{}]*["\']?art["\']?\s*[:=]\s*["\']?([^"\'}]+)["\']?[^{}]*["\']?content["\']?\s*[:=]\s*["\']?([^"\'}]+)["\']?[^{}]*\}', response_text, re.IGNORECASE | re.DOTALL)
    if json_match:
        return {
            "art": json_match.group(1).strip(),
            "content": json_match.group(2).strip()
        }
    
    # Try to parse as JSON directly
    try:
        # Remove markdown code blocks if present
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*', '', cleaned)
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict) and "art" in parsed and "content" in parsed:
            return parsed
    except:
        pass
    
    return {}


class JudgmentManager(BaseManager):
    """
    Manager for handling legal judgment benchmark evaluations.
    """

    def __init__(self, model: BaseModel, tasks_path: Path = DATA_PATH):
        super().__init__(model, "judgments", tasks_path)

    def get_tasks(self) -> list[Judgment]:
        return self.tasks

    def get_result(self, judgment: Judgment, model_response: str) -> dict:
        extracted_answer = extract_judgment_answer(model_response)
        is_correct = (
            extracted_answer.get("art", "").strip().lower() == judgment.expected_article.strip().lower()
            and extracted_answer.get("content", "").strip() == judgment.expected_content.strip()
        )

        result = {
            "id": judgment.id,
            "masked_text": judgment.masked_text,
            "expected_article": judgment.expected_article,
            "expected_content": judgment.expected_content,
            "model_name": self.model.model_name,
            "model_config": json.dumps(asdict(self.model.model_config)),
            "model_response": model_response,
            "extracted_answer": extracted_answer,
            "is_correct": is_correct,
        }

        self.results.append(result)
        return result
