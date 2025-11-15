from typing import Final, Dict
from pathlib import Path

ENCODING: Final[str] = "utf-8"
MAX_NEW_TOKENS: Final[int] = 256

SYSTEM_PROMPTS: Final[Dict[str, str]] = {
    "EXAM": (
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
        "Pamiętaj aby zwracana odpowiedź była czystym tekstem bez formatowania."
        "Odpowiedź nie może być formatowana jak dla pliku md."
        f"Odpowiedź powinna mieć maksymalnie {MAX_NEW_TOKENS} tokenów."
    ),
    "JUDGMENTS": (
        "ROLA: Jesteś ekspertem prawnym i analitykiem procesów sądowych, "
        "pracującym z dokumentami, w których celowo usunięto kluczowe odniesienia "
        "do prawa materialnego. "
        "ZADANIE: Na podstawie zamaskowanego tekstu uzasadnienia zidentyfikuj kluczowy artykuł prawny "
        "oznaczenie aktu normatywnego \n"
        "WYMAGANY FORMAT ODPOWIEDZI: \n"
        "Wskaż tylko numer artykułu i oznaczenie aktu normatywnego "
        "(bez paragrafu i bez jednostki redakcyjnej, np. 'art. 1 k.c.') oraz odtwórz dokładne brzmienie "
        "np. Art. 1.§ 1. Kodeks niniejszy reguluje stosunki cywilnoprawne między jednosikami gospodarki uspolecznionej, "
        "miedży osobami fizycznymi oraz między jednostkami gospodarki uspołecznionej a osobami fizycznymi. "
        "§2. Przepisy kodeksu dotyczące jednostek gospodarki uspołecznionej stosuje się także do instytucji państwowych "
        "organizacji społecznych ludu pracującego, których zadanie
        "nie polega na prowadzeniu działalności gospodarczej."
        "§ 3. Jeżeli z przepisów kodeksu lub innych ustaw nie wynika nic innego, przepisy kodeksu dotyczące osób fizycznych"
        "stosuje się odpowiednio do osób prawnych nie bedących jednostkami gospodarki uspołecznionej. \n"

        "którego treść została opisana/zakryta w dokumencie. Wynik zwróć w pojedynczym bloku JSON.\n"
        "{art: '...', content: 'treść artykułu' }"

    )
}

DATA_PATH: Final[Path] = Path(__file__).parent.parent / "data"
RESULTS_PATH: Final[Path] = Path(__file__).parent.parent / "results"
ROOT_PATH: Final[Path] = Path(__file__).parent.parent
