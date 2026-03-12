from __future__ import annotations

import asyncio

from .mongodb import close_db, connect_db, get_articles_collection


async def create_indexes() -> None:
    await connect_db()
    collection = get_articles_collection()

    await collection.create_index("url", unique=True)
    await collection.create_index("title")
    await collection.create_index("category")
    await collection.create_index("source_name")
    await collection.create_index("published_at")
    await collection.create_index("simhash")
    await collection.create_index([("title", "text"), ("summary", "text")])


async def main() -> None:
    try:
        await create_indexes()
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
