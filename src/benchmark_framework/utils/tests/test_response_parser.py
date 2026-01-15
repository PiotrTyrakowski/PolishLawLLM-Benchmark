import pytest
from src.benchmark_framework.utils.response_parser import (
    strip_markdown_code_blocks,
    extract_json_field,
)


# --- Tests for strip_markdown_code_blocks ---
@pytest.mark.parametrize(
    "text,expected",
    [
        ('{"answer": "B"}', '{"answer": "B"}'),
        ('```json\n{"answer": "B"}\n```', '{"answer": "B"}'),
        ('```\n{"answer": "B"}\n```', '{"answer": "B"}'),
        ('```python\nprint("hello")\n```', 'print("hello")'),
        ('  \n```json\n{"answer": "B"}\n```\n  ', '{"answer": "B"}'),
        (
            '```json\n{\n  "answer": "B",\n  "reasoning": "test"\n}\n```',
            '{\n  "answer": "B",\n  "reasoning": "test"\n}',
        ),
        ("", ""),
        ("```json", ""),
    ],
)
def test_strip_markdown_code_blocks(text, expected):
    assert strip_markdown_code_blocks(text) == expected


# --- Tests for extract_json_field: valid JSON ---
@pytest.mark.parametrize(
    "response,field_name,expected",
    [
        ('{"answer": "B", "reasoning": "test"}', "answer", "B"),
        ('{"legal_basis": "Art. 123 k.c."}', "legal_basis", "Art. 123 k.c."),
        ('```json\n{"answer": "C"}\n```', "answer", "C"),
        ('{"answer": ""}', "answer", ""),
        (
            '{"legal_basis": "Art. 123 § 2 pkt 3 k.k."}',
            "legal_basis",
            "Art. 123 § 2 pkt 3 k.k.",
        ),
    ],
)
def test_extract_json_field_valid_json(response, field_name, expected):
    assert extract_json_field(response, field_name) == expected


# --- Tests for extract_json_field: missing field ---
@pytest.mark.parametrize(
    "response,field_name,default,expected",
    [
        ('{"answer": "B"}', "missing", "", ""),
        ('{"answer": "B"}', "missing", "fallback", "fallback"),
        ("{}", "answer", "default", "default"),
    ],
)
def test_extract_json_field_missing_returns_default(
    response, field_name, default, expected
):
    assert extract_json_field(response, field_name, default) == expected


# --- Tests for extract_json_field: regex fallback ---
@pytest.mark.parametrize(
    "response,field_name,expected",
    [
        ('{"answer": "A", "reasoning": "This is a very long...', "answer", "A"),
        ('Here is my answer: "answer": "B" and that is final.', "answer", "B"),
        ('"answer":"B"', "answer", "B"),
        ('"answer" : "B"', "answer", "B"),
        ('"answer"  :  "B"', "answer", "B"),
        ('"answer"\n:\n"B"', "answer", "B"),
    ],
)
def test_extract_json_field_regex_fallback(response, field_name, expected):
    assert extract_json_field(response, field_name) == expected


# --- Tests for extract_json_field: JSON object extraction fallback ---
@pytest.mark.parametrize(
    "response,field_name,expected",
    [
        ('Some text {"answer": "A"} more text', "answer", "A"),
        ('Response: {"answer": "B", "legal_basis": "Art. 1"} done', "answer", "B"),
        (
            'Response: {"answer": "B", "legal_basis": "Art. 1"} done',
            "legal_basis",
            "Art. 1",
        ),
    ],
)
def test_extract_json_field_object_fallback(response, field_name, expected):
    assert extract_json_field(response, field_name) == expected


# --- Tests for extract_json_field: edge cases ---
@pytest.mark.parametrize(
    "response,field_name,default,expected",
    [
        ("Just random text", "answer", "", ""),
        ("", "answer", "", ""),
        ("No JSON here!", "answer", "fallback", "fallback"),
    ],
)
def test_extract_json_field_invalid_returns_default(
    response, field_name, default, expected
):
    assert extract_json_field(response, field_name, default) == expected


# --- Test realistic model response ---
def test_extract_json_field_realistic_response():
    response = """```json
{
    "reasoning": "Analiza opcji A, B, C...",
    "answer": "B",
    "legal_basis": "Art. 415 § 1 k.c.",
    "legal_basis_content": "Kto z winy swojej wyrządził drugiemu szkodę..."
}
```"""
    assert extract_json_field(response, "answer") == "B"
    assert extract_json_field(response, "legal_basis") == "Art. 415 § 1 k.c."
    assert "winy swojej" in extract_json_field(response, "legal_basis_content")


# --- Test realistic model response ---
def test_extract_json_field_realistic_response2():
    response = "```json\n{\n  \"answer\": \"C\",\n  \"legal_basis\": \"art. 821 § 1 k.p.c.\",\n  \"legal_basis_content\": \"§ 1. Organ egzekucyjny zawiesza postępowanie, jeżeli: 1) tytuł wykonawczy został pozbawiony wykonalności albo wykonanie tytułu zostało wstrzymane, albo 2) egzekucja ze względu na jej przedmiot lub osobę dłużnika jest niedopuszczalna, albo dłużnik jest: a) „funkcjonariuszem publicznym”, b) „osobą pełniącą urząd publiczny”, c) „urzędnikiem państwowym”, d) „członkiem personelu dyplomatycznego lub konsularnego państwa obcego”. § 2. Jeżeli organ egzekucyjny jest jednocześnie organem sądowym, który wydał tytuł wykonawczy, a wierzyciel domaga się przeprowadzenia egzekucji na jego podstawie przeciwko osobie, o której mowa w § 1 pkt 2, organ ten wyda postanowienie odmowne. § 3. W przypadku określonym w § 1 pkt 2, dłużnik może w drodze powództwa żądać pozbawienia tytułu wykonawczego wykonalności. Jeżeli dłużnikiem jest Skarb Państwa, w drodze powództwa przeciwegzekucyjnego można żądać niedopuszczenia do egzekucji, a w razie jej wszczęcia – umorzenia postępowania. § 4. Jeżeli postępowanie egzekucyjne prowadzi komornik, a egzekucja dotyczy świadczenia pieniężnego, a z okoliczności sprawy wynika, że dłużnik nie ma prawa do lokalu socjalnego lub zamiennego, komornik zawiesza postępowanie do czasu ustalenia tego prawa, chyba że interes wierzyciela sprzeciwia się takiemu zawieszeniu. § 5. Przepisów § 1 pkt 2 i § 4 nie stosuje się do egzekucji świadczeń alimentacyjnych.”\n}\n```"
    assert extract_json_field(response, "answer") == "C"
    assert extract_json_field(response, "legal_basis") == "art. 821 § 1 k.p.c."
    legal_basis_content = extract_json_field(response, "legal_basis_content")
    assert len(legal_basis_content) > 0
    print("lbc:" + legal_basis_content)

