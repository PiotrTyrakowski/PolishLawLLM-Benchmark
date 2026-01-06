import json
from pathlib import Path
from typing import Optional
from dataclasses import asdict

from src.benchmark_framework.models.base_model import BaseModel
from src.common.domain.judgment import Judgment, JudgmentResult
from src.benchmark_framework.managers.base_manager import BaseManager
from src.benchmark_framework.utils.response_parser import extract_json_field


class JudgmentManager(BaseManager):
    """
    Manager for handling legal judgment benchmark evaluations.
    """

    def __init__(self, model: BaseModel, tasks_path: Path, year: Optional[int] = None):
        super().__init__(model, "judgments", tasks_path, year)

    def get_output_path(self, task: Judgment, results_dir: Path) -> Path:
        model_name = self.model.model_name.replace("/", "-")
        return results_dir / model_name / self.task_type / "all.jsonl"

    def get_result(self, judgment: Judgment, model_response: str) -> JudgmentResult:
        model_legal_basis = extract_json_field(model_response, "legal_basis")
        model_legal_basis_content = extract_json_field(
            model_response, "legal_basis_content"
        )

        result: JudgmentResult = {
            "id": judgment.id,
            "judgment_link": judgment.judgment_link,
            "date": judgment.date,
            "legal_basis": judgment.legal_basis,
            "legal_basis_content": judgment.legal_basis_content,
            "model_name": self.model.model_name,
            "model_config": json.dumps(asdict(self.model.model_config)),
            "model_response": model_response,
            "model_legal_basis": model_legal_basis,
            "model_legal_basis_content": model_legal_basis_content,
        }
        return result

    def get_system_prompt(self, task: Judgment) -> str:
        return f"""**ROLA I ZAKRES**
        Jesteś ekspertem w polskim prawie, specjalizującym się w analizie orzecznictwa sądowego. Twoim zadaniem jest analiza zamaskowanego tekstu uzasadnienia wyroku i zwrócenie numeru zamaskowanego artykułu oraz jego treści w określonym formacie. Odpowiadaj WYŁĄCZNIE w języku polskim.
    
        WAŻNE: Nie ujawniaj wewnętrznego łańcucha myślenia (chain-of-thought). Podaj tylko finalny wynik jako JSON w ściśle określonym formacie.
    
        **WEJŚCIE**
        Każde zadanie zawiera zamaskowany tekst uzasadnienia. W którym mogą pojawić się 2 typy zamaskowań:
            - <ART_MASK> - zamaskowany identyfikator artykułu (np. "art. 415 k.c." lub "art. 139^1 k.p.c.")
            - <TREŚĆ_MASK> - zamaskowana dosłowna treść artykułu.
    
        **FORMAT WYJŚCIA**
        Odpowiedź musi być WYŁĄCZNIE w formacie JSON (bez żadnego innego tekstu przed/po).
    
        WYMÓG DOT. PODSTAWY PRAWNEJ:
        Twoim celem jest wskazanie **TYLKO IDENTYFIKATOR ARTYKUŁU I AKTU PRAWNEGO**, bez schodzenia do poziomu paragrafów czy punktów, nawet w przypadku gdy zamaskowano przepis na poziomie niższym niż artykuł.
    
        Pola JSON:
        "legal_basis": oznaczenie zamaskowanego artykułu (np. "art. 415 k.c.", "art. 148 k.k.",  jeżeli numer artykułu zawiera indeks górny, to indeks ten musi być zapisany poprzedzając go znakiem ^, np. "art. 139^1 k.p.c."). Zwracaj WYŁĄCZNIE numer artykułu i skrót aktu prawnego bez paragrafów/punktów/ustępów.
        "legal_basis_content": dosłowna treść zamaskowanego artykułu (zgodnie ze stanem prawnym na wskazaną datę).
    
        **ISTOTNE OGRANICZENIA**
        - Stan prawny: na dzień {task.date}. (Upewnij się, że przytaczany przepis obowiązywał w tym brzmieniu w tej dacie).
        - Maksymalna długość odpowiedzi: ogranicz do niezbędnego minimum (tylko JSON).
        - Jeśli w tekście występuje wiele przepisów, wybierz ten, który stanowi **główną oś sporu** lub rozstrzygnięcia w analizowanym fragmencie.
    
        **CHECKLISTA PRZED ZWRÓCENIEM ODPOWIEDZI**
        - Czy output to wyłącznie poprawny JSON?
        - Czy legal_basis zawiera tylko artykuł i skrót aktu (bez paragrafów/ustępów)?
        - Czy legal_basis_content to dosłowna treść przepisu obowiązująca w dacie {task.date}?
        """
