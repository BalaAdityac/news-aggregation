# database/supabase_client.py

from supabase import create_client, Client
from typing import List, Optional
import logging
from datetime import datetime

from config.settings import SUPABASE_URL, SUPABASE_KEY
from models.schemas import RawArticle, SummarizedArticle, UserPreferences

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── INITIALIZE SUPABASE CLIENT ─────────────────────────────
# create_client connects to your Supabase project
# It handles authentication, REST API calls, and error handling
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ═══════════════════════════════════════════════════════════════
# ARTICLE OPERATIONS
# ═══════════════════════════════════════════════════════════════

def save_articles(articles: List[RawArticle]) -> int:
    """
    Save raw articles to the database.
    
    Uses 'upsert' instead of 'insert':
    - insert: fails if a record with the same ID already exists
    - upsert: updates the record if it exists, inserts if it doesn't
    
    This prevents duplicate errors when running the scraper multiple times.
    
    Args:
        articles: List of RawArticle objects to save
    
    Returns:
        Number of articles saved
    """
    if not articles:
        return 0
    
    # Convert Pydantic models to dictionaries for Supabase
    # .model_dump() converts a Pydantic model to a plain Python dict
    records = []
    for article in articles:
        record = article.model_dump()
        # Supabase expects these specific fields
        record["is_summarized"] = False
        records.append(record)
    
    try:
        # Upsert into the articles table
        # on_conflict="id" means: if an article with this ID exists, update it
        result = supabase.table("articles").upsert(
            records, 
            on_conflict="id"
        ).execute()
        
        saved_count = len(result.data) if result.data else 0
        logger.info(f"Saved {saved_count} articles to database")
        return saved_count
        
    except Exception as e:
        logger.error(f"Error saving articles: {e}")
        return 0


def get_unsummarized_articles(limit: int = 50) -> List[dict]:
    """
    Get articles that haven't been summarized yet.
    
    This is useful for the pipeline:
    1. Scraper runs → saves raw articles
    2. Summarizer runs → fetches unsummarized articles → processes them
    
    Args:
        limit: Maximum number of articles to return
    
    Returns:
        List of article dictionaries
    """
    try:
        result = supabase.table("articles") \
            .select("*") \
            .eq("is_summarized", False) \
            .order("fetched_at", desc=True) \
            .limit(limit) \
            .execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        logger.error(f"Error fetching unsummarized articles: {e}")
        return []


def update_article_summary(article_id: str, summary_data: dict) -> bool:
    """
    Update an article with its AI-generated summary and analysis.
    
    Args:
        article_id: The article's ID
        summary_data: Dict with summary, importance_score, sentiment, etc.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase.table("articles").update({
            "summary": summary_data.get("summary"),
            "importance_score": summary_data.get("importance_score", 5),
            "sentiment": summary_data.get("sentiment", "Neutral"),
            "why_it_matters": summary_data.get("why_it_matters"),
            "is_summarized": True,
        }).eq("id", article_id).execute()
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating summary for {article_id}: {e}")
        return False


def get_summarized_articles(
    category: Optional[str] = None,
    limit: int = 50
) -> List[dict]:
    """
    Get articles that have been summarized.
    
    Optionally filter by category.
    Returns articles sorted by importance score (highest first).
    
    Args:
        category: Optional category filter
        limit: Maximum articles to return
    
    Returns:
        List of article dictionaries with summaries
    """
    try:
        query = supabase.table("articles") \
            .select("*") \
            .eq("is_summarized", True) \
            .order("importance_score", desc=True) \
            .limit(limit)
        
        if category:
            query = query.eq("category", category)
        
        result = query.execute()
        return result.data if result.data else []
        
    except Exception as e:
        logger.error(f"Error fetching summarized articles: {e}")
        return []


def get_todays_articles() -> List[dict]:
    """
    Get all summarized articles from today.
    Used for generating daily newsletters.
    """
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        result = supabase.table("articles") \
            .select("*") \
            .eq("is_summarized", True) \
            .gte("fetched_at", f"{today}T00:00:00") \
            .order("importance_score", desc=True) \
            .execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        logger.error(f"Error fetching today's articles: {e}")
        return []


# ═══════════════════════════════════════════════════════════════
# USER OPERATIONS
# ═══════════════════════════════════════════════════════════════

def get_all_active_users() -> List[dict]:
    """
    Get all active users for newsletter delivery.
    
    Returns:
        List of user dictionaries
    """
    try:
        result = supabase.table("users") \
            .select("*") \
            .eq("is_active", True) \
            .execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return []


def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get a single user by their ID."""
    try:
        result = supabase.table("users") \
            .select("*") \
            .eq("id", user_id) \
            .single() \
            .execute()
        
        return result.data
        
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        return None


def log_newsletter_delivery(user_id: str, method: str, article_count: int):
    """
    Log that a newsletter was sent to a user.
    Useful for tracking and debugging delivery issues.
    """
    try:
        supabase.table("newsletter_logs").insert({
            "user_id": user_id,
            "delivery_method": method,
            "article_count": article_count,
            "status": "sent"
        }).execute()
        
    except Exception as e:
        logger.error(f"Error logging delivery for {user_id}: {e}")


# ─── TEST ────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test database connection
    print("Testing Supabase connection...")
    
    # Test saving an article
    test_article = RawArticle(
        title="Test Article - Please Ignore",
        source="Test Source",
        category="Technology",
        url="https://test.com/article-1",
        content="This is a test article content for database testing."
    )
    
    saved = save_articles([test_article])
    print(f"Saved {saved} articles")
    
    # Test fetching
    unsummarized = get_unsummarized_articles(limit=5)
    print(f"Unsummarized articles: {len(unsummarized)}")
    
    users = get_all_active_users()
    print(f"Active users: {len(users)}")