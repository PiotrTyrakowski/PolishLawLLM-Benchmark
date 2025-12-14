import json
from pathlib import Path
from dataclasses import asdict

from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.types.exam import Exam, ExamResult
from benchmark_framework.managers.base_manager import BaseManager
from benchmark_framework.constants import DATA_PATH, MAX_NEW_TOKENS
from benchmark_framework.utils.response_parser import extract_json_field


class ExamManager(BaseManager):
    """
    Manager for handling legal exam benchmark evaluations.
    """

    def __init__(self, model: BaseModel, tasks_path: Path = DATA_PATH):
        super().__init__(model, "exams", tasks_path)

    def get_tasks(self) -> list[Exam]:
        return self.tasks

    def get_result(self, exam: Exam, model_response: str) -> ExamResult:
        model_answer = extract_json_field(model_response, "answer").upper()
        model_legal_basis = extract_json_field(model_response, "legal_basis")
        model_legal_basis_content = extract_json_field(
            model_response, "legal_basis_content"
        )

        result: ExamResult = {
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

        self.results.append(result)
        return result

    def get_system_prompt(self, year: int) -> str:
        return (
            "Jesteś ekspertem w polskim prawie, biorącym udział w egzaminie zawodowym. "
            "Twoje zadanie polega na analizie pytań testowych z zakresu prawa polskiego i wyborze prawidłowej odpowiedzi "
            "wraz z podaniem podstawy prawnej.\n\n"
            "# STRUKTURA PYTANIA\n"
            "Każde pytanie zawiera:\n"
            "- Treść pytania\n"
            "- Trzy opcje odpowiedzi: A, B, C\n"
            "- Dokładnie jedna odpowiedź jest prawidłowa\n\n"
            "# INSTRUKCJE ROZWIĄZYWANIA\n"
            "1. ANALIZA PYTANIA\n"
            "   - Zidentyfikuj dziedzinę prawa (np. prawo cywilne, karne, administracyjne)\n"
            "   - Wyodrębnij kluczowe pojęcia prawne i zagadnienia\n"
            "   - Określ, które przepisy prawne są istotne dla odpowiedzi\n\n"
            "2. OCENA KAŻDEJ OPCJI\n"
            "   Dla każdej opcji (A, B, C):\n"
            "   - Zweryfikuj zgodność z obowiązującymi przepisami prawa polskiego\n"
            "   - Sprawdź dokładność i precyzję sformułowania\n"
            "   - Uwzględnij aktualny stan prawny\n"
            "   - Odnieś się do konkretnych artykułów, paragrafów lub punktów\n\n"
            "3. WYBÓR ODPOWIEDZI\n"
            "   - Wybierz odpowiedź w pełni zgodną z przepisami prawa\n"
            "   - Zidentyfikuj dokładną podstawę prawną (artykuł, paragraf, punkt)\n"
            "   - Przytocz treść odpowiedniego przepisu\n"
            "   - Zawsze tylko jeden przepis podstawy prawnej jest poprawny\n\n"
            "# FORMAT ODPOWIEDZI\n"
            "Musisz zwrócić odpowiedź WYŁĄCZNIE w formacie JSON, bez żadnego dodatkowego tekstu przed lub po:\n\n"
            "{\n"
            '  "reasoning": "Krotko opisany proces myślenia i analizy każdej opcji",\n'
            '  "answer": "A",\n'
            '  "legal_basis": "Art. 123 § 2 pkt 3 k.k.",\n'
            '  "legal_basis_content": "Dokładna treść cytowanego przepisu prawnego"\n'
            "}\n\n"
            "# WYMAGANIA\n"
            "- 'reasoning': Krótka, zwięzła analiza każdej opcji max 50 znaków na opcję\n"
            "- 'answer': Pojedyncza litera - A, B lub C\n"
            "- 'legal_basis': Pełne oznaczenie przepisu (np. 'Art. 415 § 1 k.c.', 'Art. 148 § 2 pkt 1 k.p.k.')\n"
            "- 'legal_basis_content': Dosłowna treść przepisu, na którym oparłeś swoją odpowiedź\n"
            "  WAŻNE: Jeśli podstawą odpowiedzi jest konkretny paragraf lub punkt artykułu, podaj WYŁĄCZNIE treść tego paragrafu/punktu, a nie całego artykułu\n"
            "  PRZYKŁAD: Jeśli podstawą odpowiedzi jest Art. 32 pkt 1 k.k., wówczas legal_basis_content powinno mieć 'grzywna;' i nic więcej.\n"
            "# WAŻNE UWAGI\n"
            "- Zwróć TYLKO poprawny JSON - bez markdown, bez dodatkowego tekstu\n"
            f"- Maksymalna długość całej odpowiedzi: {MAX_NEW_TOKENS} tokenów\n"
            f"- Zwróć poprawne dane na dzień 20 września {year} roku."
        )
