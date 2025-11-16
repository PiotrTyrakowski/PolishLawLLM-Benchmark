import os
import pytest
from pathlib import Path

from parsers.parsers.legal_base_parser import LegalBaseParser


def get_pdf_path():
    """Helper function to get the path to the 2025 exam PDF."""
    file_path = (
        Path(__file__).parent
        / ".."
        / ".."
        / ".."
        / "pdfs"
        / "2025"
        / "legal_base"
        / "kk.pdf"
    )
    return file_path.resolve()


@pytest.fixture(scope="session")
def parser_instance():
    """Create a single LegalBaseParser instance for all tests in the session."""
    pdf_path = get_pdf_path()
    if not os.path.exists(pdf_path):
        pytest.skip(f"PDF path set in LEGAL_PDF_PATH does not exist: {pdf_path}")
    parser = LegalBaseParser(pdf_path)
    return parser


@pytest.mark.parametrize(
    "article_num,expected_text",
    [
        (
            1,
            "Art. 1. § 1. Odpowiedzialności karnej podlega ten tylko, kto popełnia czyn zabroniony pod groźbą kary przez ustawę obowiązującą w czasie jego popełnienia. § 2. Nie stanowi przestępstwa czyn zabroniony, którego społeczna szkodliwość jest znikoma. § 3. Nie popełnia przestępstwa sprawca czynu zabronionego, jeżeli nie można mu przypisać winy w czasie czynu.",
        ),
        (
            2,
            "Art. 2. Odpowiedzialności karnej za przestępstwo skutkowe popełnione przez zaniechanie podlega ten tylko, na kim ciążył prawny, szczególny obowiązek zapobiegnięcia skutkowi.",
        ),
        (
            47,
            "Art. 47. § 1. W razie skazania sprawcy za umyślne przestępstwo przeciwko życiu lub zdrowiu albo za inne przestępstwo umyślne, którego skutkiem jest śmierć człowieka, ciężki uszczerbek na zdrowiu, naruszenie czynności narządu ciała lub rozstrój zdrowia, sąd może orzec nawiązkę na rzecz Funduszu Pomocy Pokrzywdzonym oraz Pomocy Postpenitencjarnej. § 2. W razie skazania sprawcy za umyślne przestępstwo przeciwko środowisku sąd orzeka, a w wypadku skazania sprawcy za nieumyślne przestępstwo przeciwko środowisku sąd może orzec, nawiązkę w wysokości od 10 000 do 10 000 000 złotych na rzecz Narodowego Funduszu Ochrony Środowiska i Gospodarki Wodnej, o którym mowa w art. 400 ust. 1 ustawy z dnia 27 kwietnia 2001 r. – Prawo ochrony środowiska (Dz. U. z 2024 r. poz. 54, z późn. zm. ). § 2a. W przypadkach, o których mowa w art. 44a § 4–6, sąd może orzec nawiązkę w wysokości do 1 000 000 złotych na rzecz pokrzywdzonego lub Funduszu Pomocy Pokrzywdzonym oraz Pomocy Postpenitencjarnej. § 3. W razie skazania sprawcy za przestępstwo określone w art. 173, art. 174, art. 177 lub w art. 355, jeżeli sprawca był w stanie nietrzeźwości lub pod wpływem środka odurzającego lub zbiegł z miejsca zdarzenia, sąd orzeka nawiązkę na rzecz pokrzywdzonego, a w razie jego śmierci w wyniku popełnionego przez skazanego przestępstwa nawiązkę na rzecz osoby najbliższej, której sytuacja życiowa wskutek śmierci pokrzywdzonego uległa znacznemu pogorszeniu. W razie gdy ustalono więcej niż jedną taką osobę, nawiązki orzeka się na rzecz każdej z nich. Jeśli ustalenie takiej osoby nie jest możliwe, sąd orzeka nawiązkę na rzecz Funduszu Pomocy Pokrzywdzonym oraz Pomocy Postpenitencjarnej. Sąd orzeka nawiązkę w wysokości co najmniej 10 000 złotych. § 4. W szczególnie uzasadnionych okolicznościach, gdy wymierzona nawiązka powodowałaby dla sprawcy uszczerbek dla niezbędnego utrzymania siebie i rodziny lub gdy pokrzywdzony pojednał się ze sprawcą, sąd może ją wymierzyć w wysokości niższej niż wysokość wskazana w § 2 i 3. § 5. Przepisu § 3 nie stosuje się, jeżeli sąd orzekł obowiązek naprawienia wyrządzonej przestępstwem szkody lub zadośćuczynienia za doznaną krzywdę w wysokości wyższej niż 10 000 złotych.",
        ),
        (
            "37b",
            "Art. 37b. W sprawie o występek zagrożony karą pozbawienia wolności, niezależnie od dolnej granicy ustawowego zagrożenia przewidzianego w ustawie za dany czyn, sąd może orzec jednocześnie karę pozbawienia wolności w wymiarze nieprzekraczającym 3 miesięcy, a jeżeli górna granica ustawowego zagrożenia wynosi przynajmniej 10 lat – 6 miesięcy, oraz karę ograniczenia wolności do lat 2. Przepisów art. 69–75 nie stosuje się. W pierwszej kolejności wykonuje się wówczas karę pozbawienia wolności, chyba że ustawa stanowi inaczej.",
        ),
    ],
)
def test_extract_article(parser_instance, article_num, expected_text):
    """Test that article extraction returns the expected text."""
    result = parser_instance.get_article(article_num)
    assert (
        result == expected_text
    ), f"Article {article_num} does not match expected text"


@pytest.mark.parametrize(
    "article_num,paragraph_num,expected_text",
    [
        (
            1,
            1,
            "Odpowiedzialności karnej podlega ten tylko, kto popełnia czyn zabroniony pod groźbą kary przez ustawę obowiązującą w czasie jego popełnienia.",
        ),
        (
            1,
            2,
            "Nie stanowi przestępstwa czyn zabroniony, którego społeczna szkodliwość jest znikoma.",
        ),
        (
            10,
            "2a",
            "Nieletni, który po ukończeniu 14 lat, a przed ukończeniem 15 lat, dopuszcza się czynu zabronionego określonego w art. 148 § 2 lub 3, może odpowiadać na zasadach określonych w tym kodeksie, jeżeli okoliczności sprawy oraz stopień rozwoju sprawcy, jego właściwości i warunki osobiste za tym przemawiają oraz zachodzi uzasadnione przypuszczenie, że stosowanie środków wychowawczych lub poprawczych nie jest w stanie zapewnić resocjalizacji nieletniego.",
        ),
    ],
)
def test_extract_paragraph(parser_instance, article_num, paragraph_num, expected_text):
    """Test that paragraph extraction returns the expected text."""
    result = parser_instance.get_paragraph(article_num, paragraph_num)
    assert (
        result == expected_text
    ), f"Art. {article_num} § {paragraph_num} does not match expected text"


@pytest.mark.parametrize(
    "article_num,paragraph_num,point_num,expected_text",
    [
        (39, None, 1, "pozbawienie praw publicznych;"),
        (
            40,
            2,
            1,
            "na karę pozbawienia wolności na czas nie krótszy od lat 3 za przestępstwo popełnione w wyniku motywacji zasługującej na szczególne potępienie;",
        ),
        (
            40,
            2,
            2,
            "za przestępstwa określone w art. 228 § 1 i 3–6, art. 229 § 1 i 3–5, art. 230 § 1, art. 230a § 1, art. 250a § 1 i 2, art. 271 § 3, art. 296a § 1, 2 i 4, art. 305 § 1–4 oraz art. 306b.",
        ),
    ],
)
def test_extract_point(
    parser_instance, article_num, paragraph_num, point_num, expected_text
):
    """Test that point extraction returns the expected text."""
    result = parser_instance.get_point(article_num, point_num, paragraph_num)
    assert (
        result == expected_text
    ), f"Art. {article_num} § {paragraph_num} does not match expected text"
