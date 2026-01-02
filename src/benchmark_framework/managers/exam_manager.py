import json
from pathlib import Path
from typing import Optional
from dataclasses import asdict

from src.benchmark_framework.models.base_model import BaseModel
from src.common.domain.exam import ExamQuestion, ExamResult
from src.benchmark_framework.managers.base_manager import BaseManager
from src.benchmark_framework.utils.response_parser import extract_json_field

EXACT_DATE_DICT: dict[int, str] = {
    2025: "17 marca 2025",
    2024: "29 marca 2024",
    2023: "23 marca 2024",
    2022: "16 marca 2022",
    2021: "25 marca 2021",
    2020: "10 kwietnia 2020",
    2019: "9 kwietnia 2019",
    2018: "11 kwietnia 2018",
    2017: "4 kwietnia 2017",
    2016: "9 marca 2016",
}


class ExamManager(BaseManager):
    """
    Manager for handling legal exam benchmark evaluations.
    """

    def __init__(self, model: BaseModel, tasks_path: Path, year: Optional[int] = None):
        super().__init__(model, "exams", tasks_path, year)

    def get_output_path(self, task: ExamQuestion, results_dir: Path) -> Path:
        year_str = str(task.year)
        filename = f"{task.exam_type}.jsonl"
        model_name = self.model.model_name.replace("/", "-")
        return results_dir / model_name / self.task_type / year_str / filename

    def get_result(self, exam: ExamQuestion, model_response: str) -> ExamResult:
        model_answer = extract_json_field(model_response, "answer").upper()
        model_legal_basis = extract_json_field(model_response, "legal_basis")
        model_legal_basis_content = extract_json_field(
            model_response, "legal_basis_content"
        )

        result: ExamResult = {
            "id": exam.id,
            "year": exam.year,
            "exam_type": exam.exam_type,
            "question": exam.question,
            "choices": exam.choices,
            "correct_answer": exam.answer,
            "legal_basis": exam.legal_basis,
            "legal_basis_content": exam.legal_basis_content,
            "model_name": self.model.model_name,
            "model_response": model_response,
            "model_config": json.dumps(asdict(self.model.model_config)),
            "model_answer": model_answer,
            "model_legal_basis": model_legal_basis,
            "model_legal_basis_content": model_legal_basis_content,
        }
        return result

    def get_system_prompt(self, year: int) -> str:
        return f"""**ROLA I ZAKRES**
Jesteś ekspertem w polskim prawie biorącym udział w egzaminu zawodowym. Twoim zadaniem jest analiza pytań testowych z zakresu prawa polskiego (jedno pytanie naraz) i zwrócenie WYŁĄCZNIE poprawnej odpowiedzi w ściśle określonym formacie JSON wraz z jednoznaczną podstawą prawną i cytatem przepisu. Odpowiadaj WYŁĄCZNIE w języku polskim.

WAŻNE: Nie ujawniaj wewnętrznego łańcucha myślenia (chain-of-thought). Podaj tylko finalny wynik jako JSON w ściśle określonym formacie (patrz przykład).

**WEJŚCIE**
Każde zadanie wejściowe zawiera treść pytania oraz trzy opcje: A, B, C. Dokładnie jedna opcja jest prawidłowa.

**FORMAT WYJŚCIA**
Odpowiedź musi być WYŁĄCZNIE w formacie JSON (bez żadnego innego tekstu przed/po).

WYMÓG DOT. PODSTAWY PRAWNEJ:
legal_basis - pełne oznaczenie przepisu (np. „art. 415 § 1 k.c.”, jeżeli numer artykułu, paragrafu lub punktu zawiera indeks górny, to indeks ten musi być zapisany poprzedzając go znakiem ^, np. "art. 139^1 § 1^1 k.p.c.").
legal_basis_content - dosłowna treść cytowanego paragrafu/punktu lub artykułu.
WAŻNE: Jeśli podstawą odpowiedzi jest konkretny paragraf lub punkt artykułu, podaj WYŁĄCZNIE treść tego paragrafu/punktu, a nie całego artykułu, np. jeśli podstawa prawna to. „art. 32 pkt 1 k.k.”, to legal_basis_content powinno zawierać wyłącznie treść punktu 1 tego artykułu („grzywna;”). W przypadku jednak gdy podstawą prawną jest konkretny artykuł, przytocz jego pełną treść.

Pola JSON:
"answer": "A" lub "B" lub "C"
"legal_basis": np. "art. 415 § 1 k.c."
"legal_basis_content": dosłowna treść cytowanego paragrafu/punktu lub artykułu

**DODATKOWE OGRANICZENIA**
- Stan prawny: na dzień {EXACT_DATE_DICT[year]} roku. (Upewnij się, że przytaczany przepis obowiązywał w tym brzmieniu na tę datę.)
- Maksymalna długość odpowiedzi: ogranicz do niezbędnego minimum (tylko wymagane pole JSON).

**PRZYKŁAD**
<example>
<input>
Pytanie: Zgodnie z Kodeksem karnym, jeżeli według nowej ustawy czyn objęty wyrokiem nie jest już zabroniony pod groźbą kary, skazanie ulega zatarciu:

Odpowiedzi:
A) na wniosek prokuratora,
B) na wniosek skazanego,
C) z mocy prawa.
</input>

<output>
{{
"answer": "C",
"legal_basis": "art. 4 § 4 k.k.",
"legal_basis_content": "Jeżeli według nowej ustawy czyn objęty wyrokiem nie jest już zabroniony pod groźbą kary, skazanie ulega zatarciu z mocy prawa."
}}
</output>
</example>

(Uwaga: powyższy przykład ma służyć jako wzorzec formatu; przy rzeczywistym pytaniu zastąp treść faktycznymi dnaymi.)

**CHECKLISTA PRZED ZWROCENIEM ODPOWIEDZI**
- Czy odpowiedź to jedna z liter A/B/C?
- Czy legal_basis jest pełne i jednoznaczne?
- Czy legal_basis_content to wyłącznie dosłowna treść cytowanego paragrafu/punktu lub artykułu?
- Czy cały output to wyłącznie poprawny JSON i nic poza nim?"""
