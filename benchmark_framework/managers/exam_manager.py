import json
import re
import re
from pathlib import Path
from dataclasses import asdict
from typing import List

from benchmark_framework.metrics.weighted_bleu import WeightedBleuMetric
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.types.exam import Exam
from benchmark_framework.managers.base_manager import BaseManager
from benchmark_framework.constants import DATA_PATH, MAX_NEW_TOKENS
from benchmark_framework.metrics.base_metric import BaseMetric
from benchmark_framework.metrics.exact_match import ExactMatchMetric
from benchmark_framework.metrics.weighted_bleu import WeightedBleuMetric
from parsers.extractors.legal_basis_extractor import LegalBasisExtractor


class ExamManager(BaseManager):
    """
    Manager for handling legal exam benchmark evaluations.
    """

    def __init__(self, model: BaseModel, tasks_path: Path = DATA_PATH):
        super().__init__(model, "exams", tasks_path)

    def get_tasks(self) -> list[Exam]:
        return self.tasks

    def get_result(self, exam: Exam, model_response: str) -> dict:
        extracted_answer = self.extract_answer_from_response(model_response)
        extracted_legal_basis_content = self.extract_legal_basis_content_from_response(
            model_response
        )
        legal_basis_extractor = LegalBasisExtractor()
        extracted_legal_basis = legal_basis_extractor.parse(exam.legal_basis)

        is_correct = extracted_answer == exam.answer

        metrics_results = {
            metric.name: metric(
                extracted_legal_basis_content,
                exam.legal_basis_content,
                legal_basis_extractor.format_code_abbreviation(
                    extracted_legal_basis.code
                ),
            )
            for metric in self.get_metrics()
        }

        result = {
            "year": exam.year,
            "exam_type": exam.exam_type,
            "question": exam.question,
            "choices": exam.choices,
            "answer": exam.answer,
            "legal_basis": exam.legal_basis,
            "model_name": self.model.model_name,
            "model_config": json.dumps(asdict(self.model.model_config)),
            "model_response": model_response,
            "extracted_answer": extracted_answer,
            "extracted_legal_basis_content": extracted_legal_basis_content,
            "is_correct": is_correct,
            "legal_basis_content": exam.legal_basis_content,
            "metrics": metrics_results,
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

    @staticmethod
    def extract_answer_from_response(response_text: str) -> str:
        """
        Extract answer from model response in JSON format.
        Handles markdown code blocks and incomplete/truncated JSON.
        """
        response_text = response_text.strip()
        answer = ""

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
            answer = json_response.get("answer", "").strip().upper()
        except json.JSONDecodeError:
            answer_match = re.search(
                r'"answer"\s*:\s*"([ABC])"', response_text, re.IGNORECASE
            )
            if answer_match:
                answer = answer_match.group(1).upper()
            else:
                json_match = re.search(r'\{.*?"answer".*?\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        json_response = json.loads(json_match.group(0))
                        answer = json_response.get("answer", "").strip().upper()
                    except json.JSONDecodeError:
                        pass

        if answer in ["A", "B", "C"]:
            return answer

        return ""
