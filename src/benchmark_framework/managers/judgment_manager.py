import json
from pathlib import Path
from typing import Optional
from dataclasses import asdict

from src.benchmark_framework.models.base_model import BaseModel
from src.domain.judgment import Judgment, JudgmentResult
from src.benchmark_framework.managers.base_manager import BaseManager
from src.benchmark_framework.utils.response_parser import extract_json_field


class JudgmentManager(BaseManager):
    """
    Manager for handling legal judgment benchmark evaluations.
    """

    def __init__(self, model: BaseModel, tasks_path: Path, year: Optional[int] = None):
        super().__init__(model, "judgments", tasks_path, year)

    def get_output_path(self, task: Judgment, results_dir: Path) -> Path:
        filename = f"{self.task_type}.jsonl"
        return results_dir / self.model.model_name / filename

    def get_result(self, judgment: Judgment, model_response: str) -> JudgmentResult:
        model_legal_basis = extract_json_field(model_response, "legal_basis")
        model_legal_basis_content = extract_json_field(
            model_response, "legal_basis_content"
        )

        result: JudgmentResult = {
            "id": judgment.id,
            "judgment_link": judgment.judgment_link,
            "legal_basis": judgment.legal_basis,
            "legal_basis_content": judgment.legal_basis_content,
            "model_name": self.model.model_name,
            "model_config": json.dumps(asdict(self.model.model_config)),
            "model_response": model_response,
            "model_legal_basis": model_legal_basis,
            "model_legal_basis_content": model_legal_basis_content,
        }
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
            f"- Zwróć poprawne dane na dzień 20 września {year} roku."
        )
