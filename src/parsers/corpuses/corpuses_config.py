"""
Configuration for filtering articles when processing legal PDF corpuses.

Structure: year -> kodeks_name -> list of ArticleFilter entries to skip
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ArticleFilter:
    article: str
    paragraph: Optional[str] = None
    point: Optional[str] = None

    def matches(
        self, article: str, paragraph: Optional[str] = None, point: Optional[str] = None
    ) -> bool:
        """
        Check if the given article/paragraph/point matches this filter.

        If paragraph or point is None in the filter, it matches any value.
        """
        if self.article != article:
            return False

        # temporary
        return True

        # If filter has paragraph specified, it must match
        if self.paragraph is not None and self.paragraph != paragraph:
            return False

        # If filter has point specified, it must match
        if self.point is not None and self.point != point:
            return False

        return True


ArticleSkipConfig = Dict[int, Dict[str, List[ArticleFilter]]]

ARTICLES_TO_SKIP: ArticleSkipConfig = {
    2025: {
        "kks": [
            ArticleFilter(article="31", paragraph="6"),
            ArticleFilter(article="53", paragraph="30d"),
            ArticleFilter(article="56b", paragraph="2"),
            ArticleFilter(article="83", paragraph="1"),
        ],
        "kpc": [
            ArticleFilter(article="477^8", paragraph="2", point="4b"),
            ArticleFilter(article="479^61", paragraph="1"),
            ArticleFilter(article="479^66a", paragraph="1"),
            ArticleFilter(article="479^57", point="2"),
            ArticleFilter(article="479^58", paragraph="1"),
        ],
        "kpsw": [ArticleFilter(article="96", paragraph="1a", point="2")],
        "krio": [
            ArticleFilter(article="99"),
            ArticleFilter(article="99^1"),
            ArticleFilter(article="99^2"),
            ArticleFilter(article="99^2a"),
            ArticleFilter(article="99^3"),
            ArticleFilter(article="183", paragraph="1"),
            ArticleFilter(article="183", paragraph="1^1"),
            ArticleFilter(article="183", paragraph="1^2"),
            ArticleFilter(article="183", paragraph="1^3"),
            ArticleFilter(article="183", paragraph="1^4"),
        ],
        "kw": [ArticleFilter(article="82b")],
    },
}

START_PAGE = {
    2025: {
        "kc": 3,
        "kk": 2,
        "kks": 4,
        "kp": 4,
        "kpa": 2,
        "kpc": 6,
        "kpk": 3,
        "kpsw": 2,
        "krio": 3,
        "ksh": 3,
        "kw": 3,
    }
}


def should_skip_article(
    year: int,
    kodeks_name: str,
    article: str,
    paragraph: Optional[str] = None,
    point: Optional[str] = None,
) -> bool:
    if year not in ARTICLES_TO_SKIP:
        return False

    year_config = ARTICLES_TO_SKIP[year]
    if kodeks_name not in year_config:
        return False

    for filter_entry in year_config[kodeks_name]:
        if filter_entry.matches(article, paragraph, point):
            return True

    return False
