from typing import Final, Dict
from pathlib import Path

ENCODING: Final[str] = "utf-8"
MAX_NEW_TOKENS: Final[int] = 1024

SYSTEM_PROMPTS: Final[Dict[str, str]] = {
    "EXAMS": (
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
        f"- Maksymalna długość całej odpowiedzi: {MAX_NEW_TOKENS} tokenów"
    ),
    "JUDGMENTS": (
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
    ),
}

TASK_PROMPT: Final[str] = (
    "ROLA: Jesteś ekspertem od tworzenia egzaminów dla modeli językowych.\n\n"
    "ZADANIE:\n"
    "1. Po otrzymaniu orzeczenia sądowego wybierz jeden z podanych w nim artykułów prawa (np. „art. 448 k.c.”).\n"
    "2. W całym tekście orzeczenia zakryj WSZYSTKIE wystąpienia tego artykułu ciągiem znaków ART_MASK.\n"
    "3. Jeżeli w orzeczeniu znajduje się opis treści tego artykułu (np. „przepis ten stanowi, że…”, „zgodnie z tym artykułem…”, „na podstawie tej regulacji…”) — zamaskuj go ciągiem TREŚĆ_MASK.\n\n"
    "# FORMAT ODPOWIEDZI\n"
    "Na końcu zwróć tylko odpowiedź w formacie JSON, bez żadnych dodatkowych komentarzy, objaśnień ani tekstu poza JSON.\n"
    "JSON musi mieć dokładnie dwa klucze:\n"
    '- "masked_judgment_text": pełny tekst orzeczenia po zamaskowaniu (bez skracania, bez „dalsza część bez zmian”).\n'
    '- "legal_basis": wybrany artykuł prawa w formacie: art. XXX k.c\n'
    "  (czyli: art. + spacja + numer + spacja + skrót ustawy, bez żadnych dodatkowych słów, nawiasów, paragrafów, liter, opisów)\n\n"
    "# PRZYKŁAD ODPOWIEDZI\n"
    "{\n"
    '  "masked_judgment_text": "...",\n'
    '  "legal_basis": "art. XYZ k.c"\n'
    "}\n\n"
    "# WYMAGANIA\n"
    "- Niczego nie pomijaj. Zawsze zwróć cały zamaskowany dokument w JSON.\n"
    "- Nie dodawaj żadnych dodatkowych zdań, opisów, analiz ani wytłumaczeń.\n"
)


Żadnych dodatkowych zdań, opisów, analiz, wytłumaczeń.

Chcesz, żebym jeszcze bardziej zoptymalizował go pod modele (np. OpenAI / Anthropic / Mistral) lub dodał wersję angielską?"

DATA_PATH: Final[Path] = Path(__file__).parent.parent / "data"
RESULTS_PATH: Final[Path] = Path(__file__).parent.parent / "results"
ROOT_PATH: Final[Path] = Path(__file__).parent.parent
