from __future__ import annotations

import hashlib
from typing import Any

from ...db.mongodb import get_articles_collection

SIMILARITY_THRESHOLD = 3


def compute_simhash(text: str) -> int:
    words = text.lower().split()
    if not words:
        return 0

    vector = [0] * 64
    for word in words:
        digest = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
        for bit in range(64):
            vector[bit] += 1 if digest & (1 << bit) else -1
    return sum(1 << bit for bit in range(64) if vector[bit] > 0)


def _hamming_distance(left: int, right: int) -> int:
    return bin(left ^ right).count("1")


async def is_duplicate(
    title: str,
    simhash_value: int,
    collection: Any | None = None,
) -> bool:
    articles: Any = collection or get_articles_collection()

    if await articles.find_one({"title": title}):
        return True

    cursor = (
        articles.find({"simhash": {"$exists": True}}, {"simhash": 1})
        .sort("fetched_at", -1)
        .limit(5000)
    )
    async for document in cursor:
        existing_simhash = document.get("simhash")
        if (
            isinstance(existing_simhash, int)
            and _hamming_distance(simhash_value, existing_simhash)
            <= SIMILARITY_THRESHOLD
        ):
            return True
    return False
