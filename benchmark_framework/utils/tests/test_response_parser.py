import pytest
from benchmark_framework.utils.response_parser import (
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
