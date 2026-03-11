from __future__ import annotations

from typing import Final

from ...schemas.article import Category


CATEGORY_KEYWORDS: Final[dict[Category, list[str]]] = {
    Category.POLITICS: [
        "parliament",
        "election",
        "minister",
        "government",
        "policy",
        "senate",
        "congress",
    ],
    Category.SPORTS: [
        "cricket",
        "ipl",
        "football",
        "fifa",
        "wicket",
        "match",
        "tournament",
    ],
    Category.TECHNOLOGY: [
        "ai",
        "startup",
        "software",
        "openai",
        "chip",
        "cloud",
        "cybersecurity",
    ],
    Category.BUSINESS: [
        "sensex",
        "rbi",
        "ipo",
        "inflation",
        "market",
        "stocks",
        "economy",
    ],
    Category.LOCAL: [
        "bengaluru",
        "bangalore",
        "namma metro",
        "bbmp",
        "karnataka",
        "traffic",
    ],
    Category.INTERNATIONAL: [
        "world",
        "nato",
        "ukraine",
        "conflict",
        "global",
        "diplomacy",
        "international",
    ],
    Category.ENTERTAINMENT: [
        "movie",
        "film",
        "actor",
        "music",
        "celebrity",
        "streaming",
    ],
    Category.HEALTH: [
        "health",
        "hospital",
        "disease",
        "covid",
        "vaccine",
        "medical",
    ],
    Category.SCIENCE: [
        "science",
        "space",
        "nasa",
        "research",
        "quantum",
        "telescope",
    ],
}


def categorize(title: str, content: str = "") -> Category:
    text = f"{title} {content}".lower()
    scores: dict[Category, int] = {
        category: sum(1 for keyword in keywords if keyword in text)
        for category, keywords in CATEGORY_KEYWORDS.items()
    }
    scores = {category: score for category, score in scores.items() if score > 0}
    if not scores:
        return Category.UNCATEGORIZED
    return max(scores, key=scores.__getitem__)
