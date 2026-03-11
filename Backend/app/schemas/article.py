from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Category(str, Enum):
    POLITICS = "Politics"
    SPORTS = "Sports"
    TECHNOLOGY = "Technology"
    LOCAL = "Local"
    INTERNATIONAL = "International"
    BUSINESS = "Business"
    ENTERTAINMENT = "Entertainment"
    HEALTH = "Health"
    SCIENCE = "Science"
    UNCATEGORIZED = "Uncategorized"


class ArticleCreate(BaseModel):
    title: str
    url: str
    source_name: str
    summary: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    image_url: Optional[str] = None
    category: Category = Category.UNCATEGORIZED
    tags: List[str] = Field(default_factory=list)
    simhash: Optional[int] = None
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArticleResponse(ArticleCreate):
    id: str
