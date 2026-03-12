# models/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


def generate_id() -> str:
    """Generate a unique ID for each article.
    
    UUID4 creates a random unique identifier like:
    '550e8400-e29b-41d4-a716-446655440000'
    
    This ensures no two articles ever have the same ID,
    even if they come from different sources.
    """
    return str(uuid.uuid4())


class RawArticle(BaseModel):
    """
    Represents a news article as fetched from a source.
    
    This is the 'raw' form — before AI processes it.
    BaseModel is from Pydantic — it gives us:
    - Automatic type validation (if you pass an int where str is expected, it errors)
    - Easy conversion to/from JSON
    - Clean documentation
    
    Field() lets us set default values and descriptions.
    """
    id: str = Field(default_factory=generate_id, description="Unique article ID")
    title: str = Field(..., description="Article headline")  
    # ... means "this field is required, no default"
    
    source: str = Field(..., description="News source name (e.g., 'BBC News')")
    category: str = Field(default="General", description="News category")
    url: str = Field(..., description="Link to original article")
    content: str = Field(default="", description="Full article text")
    
    # Optional means this field can be None
    image_url: Optional[str] = Field(default=None, description="Article image URL")
    published_at: Optional[str] = Field(default=None, description="Publication date")
    
    # Automatically set when the article object is created
    fetched_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="When we fetched this article"
    )


class SummarizedArticle(BaseModel):
    """
    An article after AI processing.
    
    Contains everything from RawArticle PLUS:
    - A 60-word AI-generated summary
    - An importance score (1-10)
    - Sentiment analysis
    """
    id: str = Field(default_factory=generate_id)
    original_id: str = Field(..., description="ID of the raw article this came from")
    title: str
    summary: str = Field(..., description="AI-generated 60-word summary")
    category: str
    source: str
    url: str
    image_url: Optional[str] = None
    published_at: Optional[str] = None
    
    # AI-enhanced fields
    importance_score: int = Field(
        default=5, 
        ge=1,  # ge = greater than or equal to
        le=10, # le = less than or equal to
        description="AI-rated importance from 1-10"
    )
    sentiment: str = Field(
        default="Neutral",
        description="Positive, Negative, or Neutral"
    )
    why_it_matters: Optional[str] = Field(
        default=None,
        description="One-line context on why this news is significant"
    )


class UserPreferences(BaseModel):
    """
    Represents a user's news preferences.
    
    This mirrors what the frontend collects during registration.
    Your personalization engine uses this to filter/rank articles.
    """
    user_id: str
    name: str
    email: str
    phone: Optional[str] = None
    categories: List[str] = Field(
        default=["General"],
        description="List of preferred categories"
    )
    sources: List[str] = Field(
        default=[],
        description="List of preferred news sources"
    )
    frequency: str = Field(
        default="daily",
        description="daily, twice-daily, or weekly"
    )
    delivery: List[str] = Field(
        default=["email"],
        description="Delivery methods: email, sms, or both"
    )


class NewsletterRequest(BaseModel):
    """
    Request body for generating a personalized newsletter.
    
    The N8N workflow or frontend sends this to your API.
    """
    user_id: str
    

class BulkSummarizeRequest(BaseModel):
    """
    Request body for summarizing multiple articles at once.
    """
    articles: List[RawArticle]