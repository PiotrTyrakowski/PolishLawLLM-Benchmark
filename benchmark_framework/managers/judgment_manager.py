import json
import re
from pathlib import Path
from dataclasses import asdict

from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.types.judgment import Judgment
from benchmark_framework.managers.base_manager import BaseManager
from benchmark_framework.constants import DATA_PATH, MAX_NEW_TOKENS


class JudgmentManager(BaseManager):
    """
    Manager for handling legal judgment benchmark evaluations.
    """

    def __init__(self, model: BaseModel, tasks_path: Path = DATA_PATH):
        super().__init__(model, "judgments", tasks_path)

    def get_tasks(self) -> list[Judgment]:
        return self.tasks

    def get_result(self, judgment: Judgment, model_response: str) -> dict:
        extracted_legal_basis = self._extract_legal_basis_from_response(model_response)
        extracted_legal_basis_content = self.extract_legal_basis_content_from_response(
            model_response
        )

        metrics_results = {
            metric.name: metric(
                extracted_legal_basis_content, judgment.legal_basis_content
            )
            for metric in self.get_metrics()
        }

        result = {
            "judgment_link": judgment.judgment_link,
            # "masked_justification_text": judgment.masked_justification_text, TODO: talk what to do with this because its very logn to jsut store it in jsonl
            "legal_basis": judgment.legal_basis,
            "legal_basis_content": judgment.legal_basis_content,
            "model_name": self.model.model_name,
            "model_config": json.dumps(asdict(self.model.model_config)),
            "model_response": model_response,
            "extracted_legal_basis": extracted_legal_basis,
            "extracted_legal_basis_content": extracted_legal_basis_content,
            "metrics": metrics_results,
        }

        self.results.append(result)
        return result

    def get_system_prompt(self, year: int) -> str:
        return (
            "Jesteś ekspertem w polskim prawie, specjalizującym się w analizie uzasadnień orzeczeń sądowych.\n"
            "Twoje zadanie polega na analizie zamaskowanego tekstu uzasadnienia wyroku i wskazaniu kluczowego przepisu prawa, do którego odnosi się orzeczenie.\n\n"
            "# STRUKTURA ZADANIA\n"
            "Każde zadanie zawiera:\n"
            "- Zamaskowany tekst uzasadnienia (fragment orzeczenia, w którym usunięto dosłowne wskazanie artykułu)\n"
            "- Opis sytuacji prawnej\n\n"
            "# INSTRUKCJE ROZWIĄZYWANIA\n"
            "1. ANALIZA UZASADNIENIA\n"
            "   - Przeanalizuj kontekst sprawy i opis sytuacji\n"
            "   - Identyfikuj kluczowe okoliczności i pojęcia prawne\n"
            "   - Zastanów się, który akt prawny i przepis odpowiada opisanej sytuacji\n\n"
            "2. WYBÓR PRZEPISU\n"
            "   - Określ najtrafniejszy artykuł polskiego prawa właściwy dla tej sprawy\n"
            "   - Podaj wyłącznie numer artykułu oraz oznaczenie aktu normatywnego (np. 'art. 415 k.c.'), bez paragrafów czy punktów\n"
            "   - Przytocz dosłowną treść tego artykułu\n\n"
            "# FORMAT ODPOWIEDZI\n"
            "Musisz zwrócić odpowiedź WYŁĄCZNIE w formacie JSON, bez żadnego dodatkowego tekstu przed lub po:\n\n"
            "{\n"
            '  "legal_basis": "art. 415 k.c.",\n'
            '  "legal_basis_content": "Dokładna treść wskazanego artykułu"\n'
            "}\n\n"
            "# WYMAGANIA\n"
            "- 'legal_basis': Tylko numer artykułu i skrót aktu prawnego (np. 'art. 1 k.c.')\n"
            "- 'legal_basis_content': Dosłowna treść wskazanego artykułu\n"
            "  WAŻNE: Podaj TYLKO treść wskazanego artykułu, bez innych fragmentów aktów prawnych\n"
            "# WAŻNE UWAGI\n"
            "- Zwróć TYLKO poprawny JSON - bez markdown, bez dodatkowego tekstu\n"
            f"- Maksymalna długość odpowiedzi: {MAX_NEW_TOKENS} tokenów"
            f"- Zwróć poprawne dane na dzień 20 września {year} roku."
        )

    @staticmethod
    def _extract_legal_basis_from_response(response_text: str) -> str:
        """
        Extract legal basis (art reference) from model response in JSON format.
        Handles markdown code blocks and incomplete/truncated JSON.
        """
        response_text = response_text.strip()

        # Remove markdown code block markers if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response_text = "\n".join(lines).strip()

        try:
            json_response = json.loads(response_text)
            # Try different possible keys
            art = (
                json_response.get("art", "")
                or json_response.get("legal_basis", "")
                or json_response.get("article", "")
            )
            return art.strip() if art else ""
        except json.JSONDecodeError:
            # Try regex patterns for art reference
            art_patterns = [
                r'"art"\s*:\s*"([^"]+)"',
                r'"legal_basis"\s*:\s*"([^"]+)"',
                r'"article"\s*:\s*"([^"]+)"',
                r"art\s*[:=]\s*['\"]([^'\"]+)['\"]",
            ]
            for pattern in art_patterns:
                match = re.search(pattern, response_text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()

            # Try to find JSON object with art field
            json_match = re.search(
                r'\{.*?"art".*?\}', response_text, re.DOTALL | re.IGNORECASE
            )
            if json_match:
                try:
                    json_response = json.loads(json_match.group(0))
                    art = json_response.get("art", "")
                    return art.strip() if art else ""
                except json.JSONDecodeError:
                    pass

        return ""
