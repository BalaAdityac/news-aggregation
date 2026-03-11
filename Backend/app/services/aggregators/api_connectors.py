from __future__ import annotations

from typing import Any

import httpx

from ...core.config import settings
from ...schemas.article import Category
from .ingest import coerce_datetime, persist_article

NEWSAPI_BASE = "https://newsapi.org/v2"
GNEWS_BASE = "https://gnews.io/api/v4"


async def _save_api_articles(
    items: list[dict[str, Any]], *, source_fallback: str, default_category: Category
) -> dict:
    saved = 0
    for item in items:
        source_name = source_fallback
        source = item.get("source")
        if isinstance(source, dict):
            source_name = source.get("name") or source_name

        created = await persist_article(
            title=item.get("title", ""),
            url=item.get("url", ""),
            source_name=source_name,
            summary=item.get("description"),
            content=item.get("content"),
            author=item.get("author"),
            published_at=coerce_datetime(item.get("publishedAt")),
            image_url=item.get("urlToImage") or item.get("image"),
            default_category=default_category,
        )
        if created:
            saved += 1

    return {"fetched": len(items), "saved": saved}


async def fetch_newsapi(query: str = "India", page_size: int = 50) -> dict:
    if not settings.NEWSAPI_KEY:
        return {"status": "skipped", "reason": "NEWSAPI_KEY not configured"}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{NEWSAPI_BASE}/everything",
                params={
                    "apiKey": settings.NEWSAPI_KEY,
                    "q": query,
                    "language": "en",
                    "pageSize": page_size,
                    "sortBy": "publishedAt",
                },
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        return {"status": "error", "reason": str(exc)}

    payload = response.json()
    result = await _save_api_articles(
        payload.get("articles", []),
        source_fallback="NewsAPI",
        default_category=Category.INTERNATIONAL,
    )
    return {"status": "ok", **result}


async def fetch_gnews(query: str = "India", max_articles: int = 20) -> dict:
    if not settings.GNEWS_API_KEY:
        return {"status": "skipped", "reason": "GNEWS_API_KEY not configured"}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{GNEWS_BASE}/search",
                params={
                    "apikey": settings.GNEWS_API_KEY,
                    "q": query,
                    "lang": "en",
                    "max": max_articles,
                },
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        return {"status": "error", "reason": str(exc)}

    payload = response.json()
    result = await _save_api_articles(
        payload.get("articles", []),
        source_fallback="GNews",
        default_category=Category.INTERNATIONAL,
    )
    return {"status": "ok", **result}


async def fetch_all_apis() -> dict:
    return {
        "newsapi": await fetch_newsapi(),
        "gnews": await fetch_gnews(),
    }
