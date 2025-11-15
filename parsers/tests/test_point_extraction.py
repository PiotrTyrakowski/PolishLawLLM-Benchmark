import pytest


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
    extractor_instance, article_num, paragraph_num, point_num, expected_text
):
    """Test that point extraction returns the expected text."""
    result = extractor_instance.get_point(article_num, point_num, paragraph_num)
    assert (
        result == expected_text
    ), f"Art. {article_num} § {paragraph_num} does not match expected text"
