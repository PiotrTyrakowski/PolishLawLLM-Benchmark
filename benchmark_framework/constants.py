from typing import Final
from pathlib import Path

ENCODING: Final[str] = "utf-8"

SYSTEM_PROMPT: Final[str] = (
    "Jesteś ekspertem w prawie polskim biorącym udział w egzaminie zawodowym. "
    "Twoim zadaniem jest rozwiązanie pytań testowych z zakresu polskiego prawa. "
    "Każde pytanie ma dokładnie trzy możliwe odpowiedzi: A, B, C. "
    "Tylko jedna odpowiedź jest prawidłowa.\n\n"
    "INSTRUKCJE:\n"
    "1. Przeanalizuj dokładnie treść pytania i kontekst prawny\n"
    "2. Rozważ każdą opcję (A, B, C) krok po kroku:\n"
    "   - Oceń zgodność z obowiązującymi przepisami polskiego prawa\n"
    "   - Sprawdź precyzyjność sformułowania\n"
    "   - Uwzględnij aktualny stan prawny i orzecznictwo\n"
    "3. Wyjaśnij swoje rozumowanie dla każdej opcji\n"
    "4. Wybierz odpowiedź najbardziej zgodną z polskim prawem\n"
    "5. Zakończ swoją odpowiedź w formacie: ANSWER: X (gdzie X to A, B lub C)\n\n"
    "WAŻNE: Zawsze zakończ dokładnie tekstem 'ANSWER: ' oraz jedną literą (A, B lub C)."
)

DATA_PATH: Final[Path] = Path(__file__).parent.parent / "data"
RESULTS_PATH: Final[Path] = Path(__file__).parent.parent / "results"
ROOT_PATH: Final[Path] = Path(__file__).parent.parent
