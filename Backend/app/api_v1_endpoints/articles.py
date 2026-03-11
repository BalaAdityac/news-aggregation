from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pymongo.errors import PyMongoError

from ..core.scheduler import run_full_aggregation
from ..db.mongodb import get_articles_collection
from ..schemas.article import Category

try:
    from bson.objectid import ObjectId
except ImportError:  # pragma: no cover - bson is installed with pymongo/motor in production.
    ObjectId = None


router = APIRouter(prefix="/articles", tags=["articles"])


def _serialize_article(document: dict[str, Any]) -> dict[str, Any]:
    article = dict(document)
    article["id"] = str(article.pop("_id"))
    return article


def _database_unavailable() -> HTTPException:
    return HTTPException(status_code=503, detail="Database unavailable")


@router.get("/")
async def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[Category] = None,
    source: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> dict:
    try:
        collection = get_articles_collection()
        query: dict[str, Any] = {}

        if category:
            query["category"] = category.value
        if source:
            query["source_name"] = {"$regex": source, "$options": "i"}
        if from_date or to_date:
            published_at_query = {}
            if from_date:
                published_at_query["$gte"] = from_date
            if to_date:
                published_at_query["$lte"] = to_date
            query["published_at"] = published_at_query

        cursor = (
            collection.find(query)
            .sort("published_at", -1)
            .skip((page - 1) * page_size)
            .limit(page_size)
        )
        items = [_serialize_article(document) async for document in cursor]
        total = await collection.count_documents(query)
    except PyMongoError as exc:
        raise _database_unavailable() from exc

    return {"page": page, "page_size": page_size, "total": total, "items": items}


@router.get("/category/{cat}")
async def list_articles_by_category(cat: Category) -> dict:
    return await list_articles(category=cat)


@router.get("/source/{src}")
async def list_articles_by_source(src: str) -> dict:
    return await list_articles(source=src)


@router.get("/search/")
async def search_articles(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    query = {
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"summary": {"$regex": q, "$options": "i"}},
            {"content": {"$regex": q, "$options": "i"}},
        ]
    }
    try:
        collection = get_articles_collection()
        cursor = (
            collection.find(query)
            .sort("published_at", -1)
            .skip((page - 1) * page_size)
            .limit(page_size)
        )
        items = [_serialize_article(document) async for document in cursor]
        total = await collection.count_documents(query)
    except PyMongoError as exc:
        raise _database_unavailable() from exc

    return {"page": page, "page_size": page_size, "total": total, "items": items}


@router.get("/{article_id}")
async def get_article(article_id: str) -> dict[str, Any]:
    if ObjectId is None:
        raise HTTPException(status_code=500, detail="ObjectId support is unavailable")

    if not ObjectId.is_valid(article_id):
        raise HTTPException(status_code=400, detail="Invalid article id")

    try:
        collection = get_articles_collection()
        article = await collection.find_one({"_id": ObjectId(article_id)})
    except PyMongoError as exc:
        raise _database_unavailable() from exc

    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return _serialize_article(article)


@router.post("/trigger")
async def trigger_aggregation(background_tasks: BackgroundTasks) -> dict[str, str]:
    background_tasks.add_task(run_full_aggregation)
    return {"status": "aggregation started"}
