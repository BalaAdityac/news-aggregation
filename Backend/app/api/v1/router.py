from fastapi import APIRouter

from .endpoints.articles import router as articles_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(articles_router)
