from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .api.v1.router import api_router
from .core.scheduler import start_scheduler, stop_scheduler
from .db.mongodb import close_db, connect_db

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_db()
    start_scheduler()
    try:
        yield
    finally:
        stop_scheduler()
        await close_db()


app = FastAPI(
    title="News Aggregation API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "news-aggregation-backend"}
