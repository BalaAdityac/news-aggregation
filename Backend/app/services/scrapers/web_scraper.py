from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
from urllib.parse import urljoin
from typing import TYPE_CHECKING, Any, TypeAlias

import httpx
from bs4 import BeautifulSoup, Tag

if TYPE_CHECKING:
    from ...schemas.article import Category

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
    RuntimeCategory = import_module("Backend.app.schemas.article").Category
    persist_article = import_module(
        "Backend.app.services.aggregators.ingest"
    ).persist_article
else:
    from ...schemas.article import Category as RuntimeCategory
    from ..aggregators.ingest import persist_article


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}


ScrapedArticle: TypeAlias = dict[str, str]


async def _save_scraped_articles(
    articles: list[ScrapedArticle],
    source_name: str,
    default_category: Category,
) -> dict[str, Any]:
    saved = 0
    for article in articles:
        created = await persist_article(
            title=article.get("title", ""),
            url=article.get("url", ""),
            source_name=source_name,
            default_category=default_category,
        )
        if created:
            saved += 1

    return {"status": "ok", "fetched": len(articles), "saved": saved}


async def _scrape_listing(
    *,
    url: str,
    selectors: str,
    source_name: str,
    default_category: Category,
) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(
            headers=HEADERS, timeout=20, follow_redirects=True
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        return {"status": "error", "reason": str(exc)}

    soup = BeautifulSoup(response.text, "html.parser")
    seen_urls: set[str] = set()
    articles: list[ScrapedArticle] = []

    for tag in soup.select(selectors):
        if not isinstance(tag, Tag):
            continue
        title = tag.get_text(" ", strip=True)
        href_value = tag.get("href")
        if not isinstance(href_value, str) or not href_value:
            continue
        href = href_value
        article_url = urljoin(str(response.url), href)
        if not title or article_url in seen_urls:
            continue
        seen_urls.add(article_url)
        articles.append({"title": title, "url": article_url})

    return await _save_scraped_articles(articles, source_name, default_category)


async def scrape_bangalore_mirror() -> dict[str, Any]:
    return await _scrape_listing(
        url="https://bangaloremirror.indiatimes.com/",
        selectors="h2 a, h3 a, .top-story a, .news-list a",
        source_name="Bangalore Mirror",
        default_category=RuntimeCategory.LOCAL,
    )


async def scrape_deccan_herald() -> dict[str, Any]:
    return await _scrape_listing(
        url="https://www.deccanherald.com/",
        selectors="h2 a, h3 a, .dh-card__title a, .headline a",
        source_name="Deccan Herald",
        default_category=RuntimeCategory.LOCAL,
    )


async def run_all_scrapers() -> dict[str, dict[str, Any]]:
    return {
        "bangalore_mirror": await scrape_bangalore_mirror(),
        "deccan_herald": await scrape_deccan_herald(),
    }
