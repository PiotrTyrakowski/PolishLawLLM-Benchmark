from parsers.parse_answers import ANSWERS_REGEXP


class TestAnswersRegexp:
    """Tests for the ANSWERS_REGEXP pattern used to parse answer entries."""

    def test_match_with_paragraph_example_1(self):
        """Test matching: art. 17 § 1 k.s.h."""
        text = "1. A art. 17 § 1 k.s.h."
        match = ANSWERS_REGEXP.search(text)

        assert match is not None
        assert match.group(1) == "1"  # question number
        assert match.group(2) == "A"  # correct answer
        assert match.group(3) == "art. 17 § 1 k.s.h."  # legal basis

    def test_match_without_paragraph_example_2(self):
        """Test matching: art. 272 k.s.h."""
        text = "2. B art. 272 k.s.h."
        match = ANSWERS_REGEXP.search(text)

        assert match is not None
        assert match.group(1) == "2"  # question number
        assert match.group(2) == "B"  # correct answer
        assert match.group(3) == "art. 272 k.s.h."  # legal basis

    def test_match_with_paragraph_example_3(self):
        """Test matching: art. 505 § 1 k.p.c."""
        text = "3. C art. 505 § 1 k.p.c."
        match = ANSWERS_REGEXP.search(text)

        assert match is not None
        assert match.group(1) == "3"  # question number
        assert match.group(2) == "C"  # correct answer
        assert match.group(3) == "art. 505 § 1 k.p.c."  # legal basis

    def test_multiple_abbreviation_parts(self):
        """Test legal basis with multiple abbreviation parts (e.g., k.p.a.)"""
        text = "10. A art. 123 k.p.a."
        match = ANSWERS_REGEXP.search(text)

        assert match is not None
        assert match.group(1) == "10"
        assert match.group(2) == "A"
        assert match.group(3) == "art. 123 k.p.a."

    def test_case_insensitive_answer(self):
        """Test that answer letters are case insensitive"""
        text = "5. a art. 100 k.c."
        match = ANSWERS_REGEXP.search(text)

        assert match is not None
        assert match.group(2) == "a"

    def test_multiline_text(self):
        """Test matching across multiple lines in text"""
        text = """100. A art. 15 k.c.
101. B art. 20 § 2 k.p.c.
102. C art. 300 k.s.h."""

        matches = list(ANSWERS_REGEXP.finditer(text))

        assert len(matches) == 3
        assert matches[0].group(1) == "100"
        assert matches[1].group(1) == "101"
        assert matches[2].group(1) == "102"

    def test_no_match_without_article(self):
        """Test that pattern doesn't match without 'art.' prefix"""
        text = "1. A 17 § 1 k.s.h."
        match = ANSWERS_REGEXP.search(text)

        assert match is None

    def test_no_match_with_invalid_answer(self):
        """Test that pattern doesn't match with invalid answer (not A, B, or C)"""
        text = "1. D art. 17 k.s.h."
        match = ANSWERS_REGEXP.search(text)

        assert match is None

    def test_no_match_without_abbreviation(self):
        """Test that pattern doesn't match without legal abbreviation"""
        text = "1. A art. 17"
        match = ANSWERS_REGEXP.search(text)

        assert match is None

    def test_varying_whitespace(self):
        """Test matching with varying amounts of whitespace"""
        text = "1.  A  art.  17  §  1  k.s.h."
        match = ANSWERS_REGEXP.search(text)

        assert match is not None
        assert match.group(1) == "1"
        assert match.group(2) == "A"
        # Note: the regex captures with spaces, normalization happens in parse_answers function

    def test_three_digit_question_number(self):
        """Test matching with three-digit question numbers"""
        text = "150. C art. 999 § 10 k.p.c."
        match = ANSWERS_REGEXP.search(text)

        assert match is not None
        assert match.group(1) == "150"
        assert match.group(2) == "C"
        assert match.group(3) == "art. 999 § 10 k.p.c."

    def test_paragraph_is_optional(self):
        """Test that § (paragraph) is optional in the pattern"""
        text_with_para = "1. A art. 17 § 1 k.s.h."
        text_without_para = "2. B art. 272 k.s.h."

        match_with = ANSWERS_REGEXP.search(text_with_para)
        match_without = ANSWERS_REGEXP.search(text_without_para)

        assert match_with is not None
        assert match_without is not None
        assert "§" in match_with.group(3)
        assert "§" not in match_without.group(3)
