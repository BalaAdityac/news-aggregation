# scrapers/newsapi_scraper.py

import requests
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from config.settings import NEWSAPI_KEY, VALID_CATEGORIES
from models.schemas import RawArticle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NewsAPI base URL — all requests go through this
NEWSAPI_BASE_URL = "https://newsapi.org/v2"

# Map our categories to NewsAPI's category names
# NewsAPI uses slightly different category names
CATEGORY_MAP = {
    "Politics": "general",      # NewsAPI doesn't have "politics" specifically
    "Technology": "technology",
    "Sports": "sports",
    "Entertainment": "entertainment",
    "Business": "business",
    "Health": "health",
    "Science": "science",
    "General": "general",
    "World": "general",
}


def fetch_top_headlines(
    category: str = "general",
    country: str = "in",  # "in" = India
    page_size: int = 20
) -> List[RawArticle]:
    """
    Fetch top headlines from NewsAPI.
    
    NewsAPI provides two main endpoints:
    1. /top-headlines — today's top stories by country/category
    2. /everything — search through millions of articles
    
    We use /top-headlines because we want TODAY's news.
    
    Free tier limits:
    - 100 requests per day
    - Only first 100 results per request
    - Results are delayed (not real-time)
    
    Args:
        category: News category (technology, sports, etc.)
        country: Two-letter country code (in, us, gb, etc.)
        page_size: How many articles to fetch (max 100)
    
    Returns:
        List of RawArticle objects
    """
    articles = []
    
    if not NEWSAPI_KEY:
        logger.warning("NewsAPI key not configured. Skipping NewsAPI fetch.")
        return articles
    
    # Map our category name to NewsAPI's expected value
    newsapi_category = CATEGORY_MAP.get(category, "general")
    
    # Build the API request URL and parameters
    url = f"{NEWSAPI_BASE_URL}/top-headlines"
    params = {
        "apiKey": NEWSAPI_KEY,
        "country": country,
        "category": newsapi_category,
        "pageSize": page_size,
    }
    
    try:
        # Make the HTTP GET request
        # requests.get() sends the request and waits for the response
        response = requests.get(url, params=params, timeout=10)
        
        # Raise an exception if the status code indicates an error
        # 200 = success, 401 = bad API key, 429 = rate limited, etc.
        response.raise_for_status()
        
        # Parse the JSON response body into a Python dictionary
        data = response.json()
        
        if data.get("status") != "ok":
            logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
            return articles
        
        logger.info(
            f"NewsAPI: fetched {data.get('totalResults', 0)} results "
            f"for category '{category}' in country '{country}'"
        )
        
        # Process each article from the response
        for item in data.get("articles", []):
            try:
                title = item.get("title", "").strip()
                
                # NewsAPI sometimes returns "[Removed]" for deleted articles
                if not title or title == "[Removed]":
                    continue
                
                url_str = item.get("url", "").strip()
                if not url_str:
                    continue
                
                # Build the content from description + full content
                # NewsAPI gives 'description' (short) and 'content' (truncated)
                description = item.get("description", "") or ""
                content = item.get("content", "") or ""
                full_content = f"{description} {content}".strip()
                
                # Clean the "[+N chars]" suffix that NewsAPI adds
                # e.g., "Article text here... [+2500 chars]"
                if "[+" in full_content:
                    full_content = full_content[:full_content.rfind("[+")].strip()
                
                # Extract source name
                source_name = "Unknown"
                if item.get("source") and item["source"].get("name"):
                    source_name = item["source"]["name"]
                
                article = RawArticle(
                    title=title,
                    source=source_name,
                    category=category,  # Use OUR category name, not NewsAPI's
                    url=url_str,
                    content=full_content,
                    image_url=item.get("urlToImage"),
                    published_at=item.get("publishedAt", datetime.utcnow().isoformat())
                )
                articles.append(article)
                
            except Exception as e:
                logger.error(f"Error processing NewsAPI article: {e}")
                continue
        
    except requests.exceptions.Timeout:
        logger.error("NewsAPI request timed out")
    except requests.exceptions.HTTPError as e:
        logger.error(f"NewsAPI HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"NewsAPI request failed: {e}")
    
    return articles


def fetch_all_categories(country: str = "in") -> List[RawArticle]:
    """
    Fetch headlines from ALL categories.
    
    Loops through each category and calls fetch_top_headlines().
    
    ⚠️ WARNING: Each category = 1 API call.
    Free tier = 100 calls/day.
    7 categories = 7 calls per run.
    So you can run this ~14 times per day on free tier.
    
    Returns:
        Combined list of articles from all categories
    """
    all_articles = []
    
    # Only fetch categories that NewsAPI supports
    categories_to_fetch = ["general", "technology", "sports", 
                          "business", "entertainment", "health", "science"]
    
    # Reverse map to get our category name from NewsAPI's
    reverse_map = {v: k for k, v in CATEGORY_MAP.items()}
    
    for newsapi_cat in categories_to_fetch:
        our_category = reverse_map.get(newsapi_cat, "General")
        articles = fetch_top_headlines(
            category=our_category,
            country=country,
            page_size=10  # Fetch 10 per category to conserve API calls
        )
        all_articles.extend(articles)
    
    logger.info(f"Total articles from NewsAPI (all categories): {len(all_articles)}")
    return all_articles


def search_news(query: str, page_size: int = 10) -> List[RawArticle]:
    """
    Search for specific news topics using NewsAPI's /everything endpoint.
    
    This is useful for finding articles about specific topics
    that might not appear in top headlines.
    
    Example: search_news("artificial intelligence India")
    
    Args:
        query: Search string
        page_size: Number of results
    
    Returns:
        List of matching articles
    """
    articles = []
    
    if not NEWSAPI_KEY:
        return articles
    
    url = f"{NEWSAPI_BASE_URL}/everything"
    params = {
        "apiKey": NEWSAPI_KEY,
        "q": query,
        "pageSize": page_size,
        "sortBy": "publishedAt",  # Most recent first
        "language": "en",
        # Only get articles from the last 24 hours
        "from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        for item in data.get("articles", []):
            title = item.get("title", "").strip()
            if not title or title == "[Removed]":
                continue
                
            article = RawArticle(
                title=title,
                source=item.get("source", {}).get("name", "Unknown"),
                category="General",  # Search results don't have categories
                url=item.get("url", ""),
                content=f"{item.get('description', '')} {item.get('content', '')}".strip(),
                image_url=item.get("urlToImage"),
                published_at=item.get("publishedAt")
            )
            articles.append(article)
            
    except Exception as e:
        logger.error(f"NewsAPI search error: {e}")
    
    return articles


# ─── TEST ────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test fetching top headlines
    articles = fetch_top_headlines(category="Technology", country="in")
    
    print(f"\nFetched {len(articles)} tech articles from NewsAPI:\n")
    for i, article in enumerate(articles[:5]):
        print(f"{i+1}. [{article.source}] {article.title}")
        print(f"   {article.content[:100]}...")
        print()