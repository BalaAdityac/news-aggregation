# ai/personalizer.py

from typing import List, Dict
import logging

from models.schemas import SummarizedArticle, UserPreferences
from config.settings import MAX_ARTICLES_PER_NEWSLETTER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def personalize_for_user(
    articles: List[SummarizedArticle],
    user_prefs: UserPreferences
) -> List[SummarizedArticle]:
    """
    Filter and rank articles based on a user's preferences.
    
    How personalization works:
    1. FILTER: Remove articles that don't match user's preferred categories/sources
    2. SCORE: Assign a relevance score to each remaining article
    3. RANK: Sort by score (highest first)
    4. LIMIT: Return top N articles
    
    Scoring logic:
    - Base score = article's importance_score (from AI, 1-10)
    - +3 if article category is in user's preferred categories
    - +2 if article source is in user's preferred sources
    - +1 if article is recent (published today)
    
    This ensures users get articles that match their interests,
    with the most important ones at the top.
    
    Args:
        articles: All available summarized articles
        user_prefs: The user's preferences
    
    Returns:
        Personalized, ranked, limited list of articles
    """
    if not articles:
        return []
    
    scored_articles = []
    
    for article in articles:
        score = article.importance_score  # Base: AI importance score (1-10)
        
        # ─── CATEGORY MATCH BONUS ────────────────────────
        # If user prefers "Technology" and this article is "Technology"
        if user_prefs.categories:
            if article.category in user_prefs.categories:
                score += 3  # Strong boost for matching category
        
        # ─── SOURCE MATCH BONUS ──────────────────────────
        # If user prefers "BBC News" and this article is from "BBC News"
        if user_prefs.sources:
            if article.source in user_prefs.sources:
                score += 2  # Moderate boost for preferred source
        
        # ─── RECENCY BONUS ──────────────────────────────
        # More recent articles get a small boost
        from datetime import datetime, timedelta
        if article.published_at:
            try:
                # Parse the publication date
                pub_date = datetime.fromisoformat(
                    article.published_at.replace("Z", "+00:00")
                )
                hours_old = (datetime.utcnow() - pub_date.replace(tzinfo=None)).total_seconds() / 3600
                
                if hours_old < 6:      # Less than 6 hours old
                    score += 2
                elif hours_old < 12:   # Less than 12 hours old
                    score += 1
            except (ValueError, TypeError):
                pass  # If date parsing fails, just skip the bonus
        
        scored_articles.append((score, article))
    
    # ─── FILTER: Must match at least category OR source ──
    if user_prefs.categories or user_prefs.sources:
        filtered = []
        for score, article in scored_articles:
            category_match = (
                not user_prefs.categories or 
                article.category in user_prefs.categories
            )
            source_match = (
                not user_prefs.sources or 
                article.source in user_prefs.sources
            )
            
            # Keep article if it matches category OR source
            if category_match or source_match:
                filtered.append((score, article))
        
        scored_articles = filtered
    
    # ─── SORT: Highest score first ───────────────────────
    scored_articles.sort(key=lambda x: x[0], reverse=True)
    
    # ─── LIMIT: Top N articles ───────────────────────────
    top_articles = [
        article for score, article in scored_articles[:MAX_ARTICLES_PER_NEWSLETTER]
    ]
    
    logger.info(
        f"Personalized for {user_prefs.name}: "
        f"{len(articles)} → {len(top_articles)} articles "
        f"(categories: {user_prefs.categories})"
    )
    
    return top_articles


def generate_newsletter_content(
    articles: List[SummarizedArticle],
    user_prefs: UserPreferences
) -> Dict:
    """
    Generate the final newsletter content structure.
    
    This organizes articles by category and creates the data structure
    that the frontend/email template will render.
    
    Returns a dictionary like:
    {
        "greeting": "Good morning, Rahul!",
        "sections": {
            "Technology": [article1, article2],
            "Sports": [article3],
            ...
        },
        "total_articles": 10,
        "generated_at": "2025-01-15T08:00:00"
    }
    
    Args:
        articles: Personalized list of summarized articles
        user_prefs: User's preferences
    
    Returns:
        Newsletter content dictionary
    """
    from datetime import datetime
    
    # ─── DETERMINE GREETING ──────────────────────────────
    current_hour = datetime.utcnow().hour + 5  # UTC to IST (rough)
    if current_hour % 24 < 12:
        time_greeting = "Good morning"
    elif current_hour % 24 < 17:
        time_greeting = "Good afternoon"
    else:
        time_greeting = "Good evening"
    
    greeting = f"{time_greeting}, {user_prefs.name}!"
    subtitle = (
        f"Here are your top stories in "
        f"{', '.join(user_prefs.categories[:3])}, "
        f"curated just for you."
    )
    
    # ─── GROUP ARTICLES BY CATEGORY ──────────────────────
    sections = {}
    for article in articles:
        category = article.category
        if category not in sections:
            sections[category] = []
        
        sections[category].append({
            "title": article.title,
            "summary": article.summary,
            "source": article.source,
            "url": article.url,
            "image_url": article.image_url,
            "importance": article.importance_score,
            "sentiment": article.sentiment,
            "why_it_matters": article.why_it_matters,
        })
    
    # ─── BUILD NEWSLETTER STRUCTURE ──────────────────────
    newsletter = {
        "user_id": user_prefs.user_id,
        "user_name": user_prefs.name,
        "user_email": user_prefs.email,
        "greeting": greeting,
        "subtitle": subtitle,
        "sections": sections,
        "total_articles": len(articles),
        "generated_at": datetime.utcnow().isoformat(),
    }
    
    return newsletter


def generate_sms_content(articles: List[SummarizedArticle], user_name: str) -> str:
    """
    Generate a condensed SMS version of the newsletter.
    
    SMS has a 160-character limit per message, but we can send longer ones.
    Keep it under 500 characters for cost efficiency.
    
    Args:
        articles: Top articles (already personalized)
        user_name: User's first name
    
    Returns:
        SMS text string
    """
    sms = f"📰 Hi {user_name}! Your news digest:\n\n"
    
    # Include top 3 articles
    for i, article in enumerate(articles[:3], 1):
        # Truncate title to 60 chars
        title = article.title[:60]
        if len(article.title) > 60:
            title += "..."
        
        # Emoji for sentiment
        sentiment_emoji = {"Positive": "🟢", "Negative": "🔴", "Neutral": "🟡"}
        emoji = sentiment_emoji.get(article.sentiment, "🟡")
        
        sms += f"{i}. {emoji} {title}\n"
    
    sms += "\nReply STOP to unsubscribe."
    
    return sms


# ─── TEST ────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test with sample data
    test_articles = [
        SummarizedArticle(
            original_id="1", title="New AI Chip Released",
            summary="A major tech company released...",
            category="Technology", source="BBC News", url="https://bbc.com/1",
            importance_score=8, sentiment="Positive"
        ),
        SummarizedArticle(
            original_id="2", title="India Wins Cricket Match",
            summary="India defeated Australia...",
            category="Sports", source="Times of India", url="https://toi.com/1",
            importance_score=7, sentiment="Positive"
        ),
        SummarizedArticle(
            original_id="3", title="Stock Market Crashes",
            summary="The Sensex fell by...",
            category="Business", source="NDTV", url="https://ndtv.com/1",
            importance_score=9, sentiment="Negative"
        ),
    ]
    
    test_user = UserPreferences(
        user_id="test-123",
        name="Rahul",
        email="rahul@test.com",
        categories=["Technology", "Sports"],
        sources=["BBC News"]
    )
    
    personalized = personalize_for_user(test_articles, test_user)
    print(f"\nPersonalized articles for {test_user.name}:")
    for a in personalized:
        print(f"  [{a.category}] {a.title} (score: {a.importance_score})")
    
    newsletter = generate_newsletter_content(personalized, test_user)
    print(f"\nNewsletter greeting: {newsletter['greeting']}")
    print(f"Sections: {list(newsletter['sections'].keys())}")
    
    sms = generate_sms_content(personalized, test_user.name)
    print(f"\nSMS content:\n{sms}")