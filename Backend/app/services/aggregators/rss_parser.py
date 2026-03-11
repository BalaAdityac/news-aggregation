from __future__ import annotations

import feedparser

from .ingest import coerce_datetime, extract_content, extract_image_url, persist_article
from .sources import RSS_SOURCES


async def fetch_rss_source(source: dict) -> int:
    feed = feedparser.parse(source["url"])
    saved = 0

    for entry in getattr(feed, "entries", []):
        title = getattr(entry, "title", "").strip()
        url = getattr(entry, "link", "").strip()
        if not title or not url:
            continue

        summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
        content = extract_content(entry)
        published_at = (
            getattr(entry, "published", None)
            or getattr(entry, "updated", None)
            or getattr(entry, "published_parsed", None)
            or getattr(entry, "updated_parsed", None)
        )

        created = await persist_article(
            title=title,
            url=url,
            source_name=source["name"],
            summary=summary,
            content=content,
            author=getattr(entry, "author", None),
            published_at=coerce_datetime(published_at),
            image_url=extract_image_url(entry),
            default_category=source.get("default_category"),
        )
        if created:
            saved += 1

    return saved


async def fetch_all_rss() -> dict:
    results = {}
    total_saved = 0

    for source in RSS_SOURCES:
        saved = await fetch_rss_source(source)
        results[source["name"]] = saved
        total_saved += saved

    return {"sources": results, "total_saved": total_saved}
