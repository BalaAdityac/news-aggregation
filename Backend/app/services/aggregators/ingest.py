from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Mapping, Optional, Protocol, cast

from ...db.mongodb import get_articles_collection
from ...schemas.article import ArticleCreate, Category
from .categorizer import categorize
from .deduplicator import compute_simhash, is_duplicate


class ArticleCollection(Protocol):
    async def find_one(self, *args: Any, **kwargs: Any) -> Any: ...
    async def insert_one(self, *args: Any, **kwargs: Any) -> Any: ...


def coerce_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    if isinstance(value, str):
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)

    if isinstance(value, tuple) and len(value) >= 6:
        return datetime(*value[:6], tzinfo=timezone.utc)

    return None


def extract_image_url(payload: Any) -> Optional[str]:
    if not hasattr(payload, "get"):
        return None

    direct = payload.get("image") or payload.get("image_url") or payload.get("urlToImage")
    if isinstance(direct, str) and direct:
        return direct

    for key in ("media_content", "media_thumbnail", "enclosures"):
        items = payload.get(key) or []
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, Mapping):
                url = item.get("url") or item.get("href")
                if isinstance(url, str) and url:
                    return url

    return None


def extract_content(payload: Any) -> str:
    content_blocks = payload.get("content") if hasattr(payload, "get") else None
    if not isinstance(content_blocks, list):
        return ""

    parts = []
    for block in content_blocks:
        if isinstance(block, Mapping):
            value = block.get("value")
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())
    return "\n\n".join(parts)


def _normalize_category(category: Optional[Category | str]) -> Optional[Category]:
    if category is None:
        return None
    if isinstance(category, Category):
        return category
    normalized = category.strip().lower()
    for member in Category:
        if member.value.lower() == normalized:
            return member
    return None


async def persist_article(
    *,
    title: str,
    url: str,
    source_name: str,
    summary: Optional[str] = None,
    content: Optional[str] = None,
    author: Optional[str] = None,
    published_at: Any = None,
    image_url: Optional[str] = None,
    category: Optional[Category | str] = None,
    default_category: Optional[Category | str] = None,
    tags: Optional[list[str]] = None,
    collection: Optional[ArticleCollection] = None,
) -> bool:
    normalized_title = title.strip()
    normalized_url = url.strip()
    if not normalized_title or not normalized_url:
        return False

    articles = cast(ArticleCollection, collection or get_articles_collection())
    if await articles.find_one({"url": normalized_url}):
        return False

    simhash_value = compute_simhash(normalized_title)
    if await is_duplicate(normalized_title, simhash_value, collection=articles):
        return False

    combined_text = " ".join(part for part in (summary, content) if part)
    resolved_category = _normalize_category(category) or categorize(normalized_title, combined_text)
    if resolved_category == Category.UNCATEGORIZED:
        resolved_category = _normalize_category(default_category) or resolved_category

    article = ArticleCreate(
        title=normalized_title,
        url=normalized_url,
        source_name=source_name.strip(),
        summary=summary.strip() if isinstance(summary, str) and summary.strip() else None,
        content=content.strip() if isinstance(content, str) and content.strip() else None,
        author=author.strip() if isinstance(author, str) and author.strip() else None,
        published_at=coerce_datetime(published_at),
        image_url=image_url.strip() if isinstance(image_url, str) and image_url.strip() else None,
        category=resolved_category,
        tags=tags or [],
        simhash=simhash_value,
    )
    document = article.model_dump(mode="python")
    document["category"] = article.category.value
    await articles.insert_one(document)
    return True
