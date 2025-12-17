import json
import pytest
from pathlib import Path

from parsers.parsers.legal_base_parser import LegalBaseParser
from parsers.utils.text_utils import TextFormatter


def get_corpus_path(code: str) -> Path:
    """Helper function to get the path to the 2025 corpus JSON."""
    file_path = (
        Path(__file__).parent
        / ".."
        / ".."
        / ".."
        / "corpuses"
        / "2025"
        / f"{code}.json"
    )
    return file_path.resolve()


def load_corpus(code: str) -> dict:
    """Load a corpus JSON file."""
    corpus_path = get_corpus_path(code)
    if not corpus_path.exists():
        pytest.skip(f"Corpus file not found: {corpus_path}")
    with open(corpus_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def kk_corpus():
    """Load the kk (criminal code) corpus."""
    return load_corpus("kk")


@pytest.fixture(scope="session")
def kks_corpus():
    """Load the kks (fiscal criminal code) corpus."""
    return load_corpus("kks")


@pytest.fixture(scope="session")
def kc_corpus():
    """Load the kc (civil code) corpus."""
    return load_corpus("kc")


@pytest.mark.parametrize(
    "article_num,expected_text",
    [
        (
            "1",
            "§ 1. Odpowiedzialności karnej podlega ten tylko, kto popełnia czyn zabroniony pod groźbą kary przez ustawę obowiązującą w czasie jego popełnienia. § 2. Nie stanowi przestępstwa czyn zabroniony, którego społeczna szkodliwość jest znikoma. § 3. Nie popełnia przestępstwa sprawca czynu zabronionego, jeżeli nie można mu przypisać winy w czasie czynu.",
        ),
        (
            "2",
            "Odpowiedzialności karnej za przestępstwo skutkowe popełnione przez zaniechanie podlega ten tylko, na kim ciążył prawny, szczególny obowiązek zapobiegnięcia skutkowi.",
        ),
        (
            "47",
            "§ 1. W razie skazania sprawcy za umyślne przestępstwo przeciwko życiu lub zdrowiu albo za inne przestępstwo umyślne, którego skutkiem jest śmierć człowieka, ciężki uszczerbek na zdrowiu, naruszenie czynności narządu ciała lub rozstrój zdrowia, sąd może orzec nawiązkę na rzecz Funduszu Pomocy Pokrzywdzonym oraz Pomocy Postpenitencjarnej. § 2. W razie skazania sprawcy za umyślne przestępstwo przeciwko środowisku sąd orzeka, a w wypadku skazania sprawcy za nieumyślne przestępstwo przeciwko środowisku sąd może orzec, nawiązkę w wysokości od 10 000 do 10 000 000 złotych na rzecz Narodowego Funduszu Ochrony Środowiska i Gospodarki Wodnej, o którym mowa w art. 400 ust. 1 ustawy z dnia 27 kwietnia 2001 r. – Prawo ochrony środowiska (Dz. U. z 2024 r. poz. 54, z późn. zm. ). § 2a. W przypadkach, o których mowa w art. 44a § 4–6, sąd może orzec nawiązkę w wysokości do 1 000 000 złotych na rzecz pokrzywdzonego lub Funduszu Pomocy Pokrzywdzonym oraz Pomocy Postpenitencjarnej. § 3. W razie skazania sprawcy za przestępstwo określone w art. 173, art. 174, art. 177 lub w art. 355, jeżeli sprawca był w stanie nietrzeźwości lub pod wpływem środka odurzającego lub zbiegł z miejsca zdarzenia, sąd orzeka nawiązkę na rzecz pokrzywdzonego, a w razie jego śmierci w wyniku popełnionego przez skazanego przestępstwa nawiązkę na rzecz osoby najbliższej, której sytuacja życiowa wskutek śmierci pokrzywdzonego uległa znacznemu pogorszeniu. W razie gdy ustalono więcej niż jedną taką osobę, nawiązki orzeka się na rzecz każdej z nich. Jeśli ustalenie takiej osoby nie jest możliwe, sąd orzeka nawiązkę na rzecz Funduszu Pomocy Pokrzywdzonym oraz Pomocy Postpenitencjarnej. Sąd orzeka nawiązkę w wysokości co najmniej 10 000 złotych. § 4. W szczególnie uzasadnionych okolicznościach, gdy wymierzona nawiązka powodowałaby dla sprawcy uszczerbek dla niezbędnego utrzymania siebie i rodziny lub gdy pokrzywdzony pojednał się ze sprawcą, sąd może ją wymierzyć w wysokości niższej niż wysokość wskazana w § 2 i 3. § 5. Przepisu § 3 nie stosuje się, jeżeli sąd orzekł obowiązek naprawienia wyrządzonej przestępstwem szkody lub zadośćuczynienia za doznaną krzywdę w wysokości wyższej niż 10 000 złotych.",
        ),
        (
            "37b",
            "W sprawie o występek zagrożony karą pozbawienia wolności, niezależnie od dolnej granicy ustawowego zagrożenia przewidzianego w ustawie za dany czyn, sąd może orzec jednocześnie karę pozbawienia wolności w wymiarze nieprzekraczającym 3 miesięcy, a jeżeli górna granica ustawowego zagrożenia wynosi przynajmniej 10 lat – 6 miesięcy, oraz karę ograniczenia wolności do lat 2. Przepisów art. 69–75 nie stosuje się. W pierwszej kolejności wykonuje się wówczas karę pozbawienia wolności, chyba że ustawa stanowi inaczej.",
        ),
    ],
)
def test_get_article_from_corpus(kk_corpus, article_num, expected_text):
    """Test that article retrieval from corpus returns the expected text."""
    article_text = kk_corpus.get(article_num)
    assert article_text is not None, f"Article {article_num} not found in corpus"
    result = TextFormatter.format_extracted_text(article_text)
    assert (
        result == expected_text
    ), f"Article {article_num} does not match expected text"


@pytest.mark.parametrize(
    "article_num,paragraph_num,expected_text",
    [
        (
            "1",
            "1",
            "Odpowiedzialności karnej podlega ten tylko, kto popełnia czyn zabroniony pod groźbą kary przez ustawę obowiązującą w czasie jego popełnienia.",
        ),
        (
            "1",
            "2",
            "Nie stanowi przestępstwa czyn zabroniony, którego społeczna szkodliwość jest znikoma.",
        ),
        (
            "10",
            "2a",
            "Nieletni, który po ukończeniu 14 lat, a przed ukończeniem 15 lat, dopuszcza się czynu zabronionego określonego w art. 148 § 2 lub 3, może odpowiadać na zasadach określonych w tym kodeksie, jeżeli okoliczności sprawy oraz stopień rozwoju sprawcy, jego właściwości i warunki osobiste za tym przemawiają oraz zachodzi uzasadnione przypuszczenie, że stosowanie środków wychowawczych lub poprawczych nie jest w stanie zapewnić resocjalizacji nieletniego.",
        ),
        (
            "18",
            "3",
            "Odpowiada za pomocnictwo, kto w zamiarze, aby inna osoba dokonała czynu zabronionego, swoim zachowaniem ułatwia jego popełnienie, w szczególności dostarczając narzędzie, środek przewozu, udzielając rady lub informacji; odpowiada za pomocnictwo także ten, kto wbrew prawnemu, szczególnemu obowiązkowi niedopuszczenia do popełnienia czynu zabronionego swoim zaniechaniem ułatwia innej osobie jego popełnienie.",
        ),
        (
            "25",
            "3",
            "Nie podlega karze, kto przekracza granice obrony koniecznej pod wpływem strachu lub wzburzenia usprawiedliwionych okolicznościami zamachu.",
        ),
    ],
)
def test_extract_paragraph_kk(kk_corpus, article_num, paragraph_num, expected_text):
    """Test that paragraph extraction from kk corpus returns the expected text."""
    article_text = kk_corpus.get(article_num)
    assert article_text is not None, f"Article {article_num} not found in corpus"
    result = LegalBaseParser.get_paragraph(article_text, paragraph_num)
    assert (
        result == expected_text
    ), f"Art. {article_num} § {paragraph_num} does not match expected text"


@pytest.mark.parametrize(
    "article_num,paragraph_num,expected_text",
    [
        (
            "50",
            "1",
            "Jeżeli jednocześnie orzeka się o ukaraniu za dwa albo więcej wykroczeń skarbowych, sąd wymierza łącznie karę grzywny w wysokości do górnej granicy ustawowego zagrożenia zwiększonego o połowę, co nie stoi na przeszkodzie orzeczeniu także innych środków za pozostające w zbiegu wykroczenia.",
        ),
        (
            "51",
            "3",
            "Orzeczona kara lub środek karny wymieniony w art. 47 § 2 pkt 2 i 3 nie podlega wykonaniu, jeżeli od daty uprawomocnienia się orzeczenia upłynęły 3 lata.",
        ),
    ],
)
def test_extract_paragraph_kks(kks_corpus, article_num, paragraph_num, expected_text):
    """Test that paragraph extraction from kks corpus returns the expected text."""
    article_text = kks_corpus.get(article_num)
    assert article_text is not None, f"Article {article_num} not found in corpus"
    result = LegalBaseParser.get_paragraph(article_text, paragraph_num)
    assert (
        result == expected_text
    ), f"Art. {article_num} § {paragraph_num} does not match expected text"


@pytest.mark.parametrize(
    "article_num,paragraph_num,expected_text",
    [
        (
            "365",
            "3",
            "Jeżeli strona uprawniona do wyboru świadczenia wyboru tego nie dokona, druga strona może jej wyznaczyć w tym celu odpowiedni termin. Po bezskutecznym upływie wyznaczonego terminu uprawnienie do dokonania wyboru przechodzi na stronę drugą.",
        ),
        (
            "7",
            None,
            "Jeżeli ustawa uzależnia skutki prawne od dobrej lub złej wiary, domniemywa się istnienie dobrej wiary.",
        ),
        (
            "454",
            None,
            "§ 1. Jeżeli miejsce spełnienia świadczenia nie jest oznaczone ani nie wynika z właściwości zobowiązania, świadczenie powinno być spełnione w miejscu, gdzie w chwili powstania zobowiązania dłużnik miał zamieszkanie lub siedzibę. Jednakże świadczenie pieniężne powinno być spełnione w miejscu zamieszkania lub w siedzibie wierzyciela w chwili spełnienia świadczenia; jeżeli wierzyciel zmienił miejsce zamieszkania lub siedzibę po powstaniu zobowiązania, ponosi spowodowaną przez tę zmianę nadwyżkę kosztów przesłania. § 2. Jeżeli zobowiązanie ma związek z przedsiębiorstwem dłużnika lub wierzyciela, o miejscu spełnienia świadczenia rozstrzyga siedziba przedsiębiorstwa.",
        ),
    ],
)
def test_extract_paragraph_kc(kc_corpus, article_num, paragraph_num, expected_text):
    """Test that paragraph/article extraction from kc corpus returns the expected text."""
    article_text = kc_corpus.get(article_num)
    assert article_text is not None, f"Article {article_num} not found in corpus"
    if paragraph_num:
        result = LegalBaseParser.get_paragraph(article_text, paragraph_num)
    else:
        result = TextFormatter.format_extracted_text(article_text)
    assert (
        result == expected_text
    ), f"Art. {article_num} § {paragraph_num} does not match expected text"


@pytest.mark.parametrize(
    "article_num,paragraph_num,point_num,expected_text",
    [
        ("39", None, "1", "pozbawienie praw publicznych;"),
        (
            "40",
            "2",
            "1",
            "na karę pozbawienia wolności na czas nie krótszy od lat 3 za przestępstwo popełnione w wyniku motywacji zasługującej na szczególne potępienie;",
        ),
        (
            "40",
            "2",
            "2",
            "za przestępstwa określone w art. 228 § 1 i 3–6, art. 229 § 1 i 3–5, art. 230 § 1, art. 230a § 1, art. 250a § 1 i 2, art. 271 § 3, art. 296a § 1, 2 i 4, art. 305 § 1–4 oraz art. 306b.",
        ),
    ],
)
def test_extract_point(kk_corpus, article_num, paragraph_num, point_num, expected_text):
    """Test that point extraction from corpus returns the expected text."""
    article_text = kk_corpus.get(article_num)
    assert article_text is not None, f"Article {article_num} not found in corpus"
    result = LegalBaseParser.get_point(article_text, point_num, paragraph_num)
    assert (
        result == expected_text
    ), f"Art. {article_num} § {paragraph_num} pkt {point_num} does not match expected text"
