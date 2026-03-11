from __future__ import annotations

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

from ..core.config import settings


client: Optional[AsyncIOMotorClient] = None


def _ensure_client() -> AsyncIOMotorClient:
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
    return client


async def connect_db() -> None:
    _ensure_client()


async def close_db() -> None:
    global client
    if client is not None:
        client.close()
        client = None


def get_db():
    return _ensure_client()[settings.MONGODB_DB_NAME]


def get_articles_collection():
    return get_db()["articles"]


def get_sources_collection():
    return get_db()["sources"]
