# main.py

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
from datetime import datetime

# Import all our modules
from scrapers.rss_scraper import fetch_all_rss_feeds
from scrapers.newsapi_scraper import fetch_all_categories as fetch_newsapi
from scrapers.web_scraper import enrich_articles_with_full_content
from ai.summarizer import summarize_batch, summarize_single_article
from ai.categorizer import batch_categorize_efficient
from ai.personalizer import (
    personalize_for_user, 
    generate_newsletter_content,
    generate_sms_content
)
from utils.deduplication import deduplicate_articles, deduplicate_by_url
from database.supabase_client import (
    save_articles, get_unsummarized_articles, update_article_summary,
    get_summarized_articles, get_todays_articles, get_all_active_users,
    get_user_by_id, log_newsletter_delivery
)
from models.schemas import (
    RawArticle, SummarizedArticle, UserPreferences,
    NewsletterRequest, BulkSummarizeRequest
)

# ─── SETUP LOGGING ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ─── CREATE FASTAPI APP ─────────────────────────────────────
app = FastAPI(
    title="AI News Aggregation Agent",
    description="Scrapes news, summarizes with AI, personalizes per user",
    version="1.0.0"
)

# ─── CORS MIDDLEWARE ─────────────────────────────────────────
# CORS (Cross-Origin Resource Sharing) controls which websites
# can call your API. Without this, the frontend (running on 
# localhost:3000) can't call the backend (running on localhost:8000).
# The browser blocks it as a security measure.
# allow_origins=["*"] means "allow any website" — fine for hackathon.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # In production, list specific domains
    allow_credentials=True,
    allow_methods=["*"],        # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],        # Allow all headers
)


# ═══════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def root():
    """
    Health check endpoint.
    
    When someone visits the base URL, this confirms the API is running.
    N8N and monitoring tools use this to verify the service is up.
    """
    return {
        "status": "running",
        "service": "AI News Aggregation Agent",
        "timestamp": datetime.utcnow().isoformat()
    }


# ═══════════════════════════════════════════════════════════════
# NEWS AGGREGATION ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/fetch-news")
async def fetch_news(background_tasks: BackgroundTasks):
    """
    Trigger the news fetching pipeline.
    
    This endpoint:
    1. Fetches articles from all RSS feeds
    2. Fetches articles from NewsAPI  
    3. Removes duplicate articles
    4. Enriches short articles with full content (web scraping)
    5. Auto-categorizes uncategorized articles
    6. Saves everything to the database
    
    N8N calls this endpoint on a schedule (e.g., every morning at 8 AM).
    
    We use BackgroundTasks because fetching + scraping can take 30+ seconds.
    The API responds immediately with "started", and the work happens
    in the background.
    """
    # Start the pipeline in the background
    background_tasks.add_task(run_fetch_pipeline)
    
    return {
        "status": "started",
        "message": "News fetching pipeline started in background"
    }


async def run_fetch_pipeline():
    """
    The actual news fetching pipeline.
    Runs as a background task.
    """
    try:
        logger.info("=" * 60)
        logger.info("STARTING NEWS FETCH PIPELINE")
        logger.info("=" * 60)
        
        # ─── STEP 1: FETCH FROM RSS FEEDS ────────────────
        logger.info("Step 1: Fetching RSS feeds...")
        rss_articles = fetch_all_rss_feeds()
        logger.info(f"  → Got {len(rss_articles)} articles from RSS")
        
        # ─── STEP 2: FETCH FROM NEWSAPI ──────────────────
        logger.info("Step 2: Fetching from NewsAPI...")
        try:
            newsapi_articles = fetch_newsapi()
            logger.info(f"  → Got {len(newsapi_articles)} articles from NewsAPI")
        except Exception as e:
            logger.warning(f"  → NewsAPI fetch failed: {e}")
            newsapi_articles = []
        
        # ─── STEP 3: COMBINE ALL ARTICLES ────────────────
        all_articles = rss_articles + newsapi_articles
        logger.info(f"Step 3: Combined total: {len(all_articles)} articles")
        
        # ─── STEP 4: DEDUPLICATE ─────────────────────────
        logger.info("Step 4: Deduplicating...")
        all_articles = deduplicate_by_url(all_articles)  # Quick URL-based dedup
        all_articles = deduplicate_articles(all_articles)  # Thorough title-based dedup
        logger.info(f"  → After dedup: {len(all_articles)} articles")
        
        # ─── STEP 5: ENRICH SHORT ARTICLES ───────────────
        logger.info("Step 5: Enriching articles with full content...")
        # Only enrich articles that have very short content
        short_articles = [a for a in all_articles if len(a.content) < 200]
        if short_articles:
            # Limit to 20 to avoid taking too long
            enrich_articles_with_full_content(short_articles[:20], delay=0.3)
        logger.info(f"  → Enriched {min(len(short_articles), 20)} articles")
        
        # ─── STEP 6: AUTO-CATEGORIZE ─────────────────────
        logger.info("Step 6: Auto-categorizing...")
        all_articles = batch_categorize_efficient(all_articles)
        
        # ─── STEP 7: SAVE TO DATABASE ────────────────────
        logger.info("Step 7: Saving to database...")
        saved = save_articles(all_articles)
        
        logger.info("=" * 60)
        logger.info(f"PIPELINE COMPLETE: {saved} articles saved")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise


@app.get("/api/articles")
def get_articles(
    category: Optional[str] = None,
    summarized_only: bool = False,
    limit: int = 50
):
    """
    Get articles from the database.
    
    Query parameters:
    - category: Filter by category (e.g., "Technology")
    - summarized_only: If true, only return articles that have summaries
    - limit: Max number of articles to return
    
    This endpoint is used by:
    - Frontend: to display articles on the website
    - N8N: to get articles for the newsletter
    """
    if summarized_only:
        articles = get_summarized_articles(category=category, limit=limit)
    else:
        articles = get_unsummarized_articles(limit=limit)
    
    return {
        "count": len(articles),
        "articles": articles
    }


@app.get("/api/articles/today")
def get_today():
    """Get all of today's summarized articles."""
    articles = get_todays_articles()
    return {
        "count": len(articles),
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "articles": articles
    }


# ═══════════════════════════════════════════════════════════════
# AI SUMMARIZATION ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/summarize")
async def summarize_articles_endpoint(background_tasks: BackgroundTasks):
    """
    Trigger AI summarization of all unsummarized articles.
    
    This fetches unsummarized articles from the database,
    runs them through the AI summarizer, and updates the database.
    """
    background_tasks.add_task(run_summarization_pipeline)
    
    return {
        "status": "started",
        "message": "Summarization pipeline started in background"
    }


async def run_summarization_pipeline():
    """
    Summarize all unsummarized articles in the database.
    """
    try:
        # Get unsummarized articles from DB
        unsummarized = get_unsummarized_articles(limit=30)
        
        if not unsummarized:
            logger.info("No unsummarized articles found")
            return
        
        logger.info(f"Summarizing {len(unsummarized)} articles...")
        
        # Convert DB records to RawArticle objects
        articles = [RawArticle(**record) for record in unsummarized]
        
        # Run through AI summarizer
        summaries = summarize_batch(articles)
        
        # Update database with summaries
        for summary in summaries:
            update_article_summary(
                article_id=summary.original_id,
                summary_data={
                    "summary": summary.summary,
                    "importance_score": summary.importance_score,
                    "sentiment": summary.sentiment,
                    "why_it_matters": summary.why_it_matters,
                }
            )
        
        logger.info(f"Summarization complete: {len(summaries)} articles processed")
        
    except Exception as e:
        logger.error(f"Summarization pipeline error: {e}")


@app.post("/api/summarize-articles")
def summarize_provided_articles(request: BulkSummarizeRequest):
    """
    Summarize a list of articles provided in the request body.
    
    Unlike /api/summarize which works from the database,
    this endpoint accepts articles directly in the request.
    
    Used by N8N when it wants to summarize specific articles.
    """
    if not request.articles:
        raise HTTPException(status_code=400, detail="No articles provided")
    
    summaries = summarize_batch(request.articles)
    
    return {
        "count": len(summaries),
        "summaries": [s.model_dump() for s in summaries]
    }


# ═══════════════════════════════════════════════════════════════
# PERSONALIZATION & NEWSLETTER ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/newsletter/generate")
def generate_newsletter(request: NewsletterRequest):
    """
    Generate a personalized newsletter for a specific user.
    
    This endpoint:
    1. Fetches the user's preferences
    2. Gets today's summarized articles
    3. Personalizes/filters articles for this user
    4. Generates the newsletter content structure
    
    The returned data can be injected into an HTML email template.
    """
    # Get user preferences
    user_data = get_user_by_id(request.user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert to UserPreferences object
    user_prefs = UserPreferences(
        user_id=user_data["id"],
        name=user_data["name"],
        email=user_data["email"],
        phone=user_data.get("phone"),
        categories=user_data.get("categories", ["General"]),
        sources=user_data.get("sources", []),
        frequency=user_data.get("frequency", "daily"),
        delivery=user_data.get("delivery", ["email"]),
    )
    
    # Get today's summarized articles
    articles_data = get_todays_articles()
    
    if not articles_data:
        # Fallback: get any recent summarized articles
        articles_data = get_summarized_articles(limit=30)
    
    # Convert to SummarizedArticle objects
    articles = []
    for a in articles_data:
        try:
            articles.append(SummarizedArticle(
                original_id=a["id"],
                title=a["title"],
                summary=a.get("summary", "Summary unavailable"),
                category=a.get("category", "General"),
                source=a.get("source", "Unknown"),
                url=a.get("url", ""),
                image_url=a.get("image_url"),
                published_at=a.get("published_at"),
                importance_score=a.get("importance_score", 5),
                sentiment=a.get("sentiment", "Neutral"),
                why_it_matters=a.get("why_it_matters"),
            ))
        except Exception:
            continue
    
    # Personalize
    personalized = personalize_for_user(articles, user_prefs)
    
    # Generate newsletter content
    newsletter = generate_newsletter_content(personalized, user_prefs)
    
    # Also generate SMS content
    sms = generate_sms_content(personalized, user_prefs.name)
    newsletter["sms_content"] = sms
    
    return newsletter


@app.post("/api/newsletter/generate-all")
async def generate_all_newsletters(background_tasks: BackgroundTasks):
    """
    Generate newsletters for ALL active users.
    
    N8N calls this endpoint when it's time to send the daily newsletter.
    It generates personalized content for each user.
    """
    users = get_all_active_users()
    
    if not users:
        return {"status": "no users", "newsletters": []}
    
    newsletters = []
    
    # Get today's articles once (shared across all users)
    articles_data = get_todays_articles()
    if not articles_data:
        articles_data = get_summarized_articles(limit=30)
    
    articles = []
    for a in articles_data:
        try:
            articles.append(SummarizedArticle(
                original_id=a["id"],
                title=a["title"],
                summary=a.get("summary", "Summary unavailable"),
                category=a.get("category", "General"),
                source=a.get("source", "Unknown"),
                url=a.get("url", ""),
                image_url=a.get("image_url"),
                published_at=a.get("published_at"),
                importance_score=a.get("importance_score", 5),
                sentiment=a.get("sentiment", "Neutral"),
                why_it_matters=a.get("why_it_matters"),
            ))
        except Exception:
            continue
    
    for user_data in users:
        try:
            user_prefs = UserPreferences(
                user_id=user_data["id"],
                name=user_data["name"],
                email=user_data["email"],
                phone=user_data.get("phone"),
                categories=user_data.get("categories", ["General"]),
                sources=user_data.get("sources", []),
                frequency=user_data.get("frequency", "daily"),
                delivery=user_data.get("delivery", ["email"]),
            )
            
            personalized = personalize_for_user(articles, user_prefs)
            newsletter = generate_newsletter_content(personalized, user_prefs)
            newsletter["sms_content"] = generate_sms_content(personalized, user_prefs.name)
            newsletters.append(newsletter)
            
        except Exception as e:
            logger.error(f"Error generating newsletter for user {user_data.get('id')}: {e}")
            continue
    
    return {
        "status": "success",
        "total_users": len(users),
        "newsletters_generated": len(newsletters),
        "newsletters": newsletters
    }


# ═══════════════════════════════════════════════════════════════
# FULL PIPELINE ENDPOINT (Combines everything)
# ═══════════════════════════════════════════════════════════════

@app.post("/api/pipeline/run")
async def run_full_pipeline(background_tasks: BackgroundTasks):
    """
    Run the ENTIRE pipeline: fetch → summarize → generate newsletters.
    
    This is the master endpoint that N8N's cron job triggers.
    One click/call does everything.
    """
    background_tasks.add_task(execute_full_pipeline)
    
    return {
        "status": "started",
        "message": "Full pipeline started. Check logs for progress."
    }


async def execute_full_pipeline():
    """Execute the complete news pipeline."""
    try:
        logger.info("🚀 FULL PIPELINE STARTED")
        
        # Step 1: Fetch news
        logger.info("📡 Step 1/3: Fetching news...")
        await run_fetch_pipeline()
        
        # Step 2: Summarize
        logger.info("🤖 Step 2/3: Summarizing articles...")
        await run_summarization_pipeline()
        
        # Step 3: Log completion
        logger.info("✅ Step 3/3: Pipeline complete!")
        logger.info("📨 Newsletters can now be generated via /api/newsletter/generate-all")
        
    except Exception as e:
        logger.error(f"❌ Full pipeline failed: {e}")


# ═══════════════════════════════════════════════════════════════
# UTILITY ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/api/stats")
def get_stats():
    """
    Get current system statistics.
    Useful for dashboards and debugging.
    """
    unsummarized = get_unsummarized_articles(limit=1000)
    summarized = get_summarized_articles(limit=1000)
    users = get_all_active_users()
    
    return {
        "total_unsummarized": len(unsummarized),
        "total_summarized": len(summarized),
        "total_active_users": len(users),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/categories")
def get_categories():
    """Return the list of valid news categories."""
    from config.settings import VALID_CATEGORIES
    return {"categories": VALID_CATEGORIES}


# ═══════════════════════════════════════════════════════════════
# RUN THE SERVER
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    # uvicorn.run starts the web server
    # "main:app" means: in the file main.py, look for the variable 'app'
    # host="0.0.0.0" means: accept connections from any IP (not just localhost)
    # port=8000: run on port 8000 (access at http://localhost:8000)
    # reload=True: auto-restart when you change code (development only)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Remove this in production
    )