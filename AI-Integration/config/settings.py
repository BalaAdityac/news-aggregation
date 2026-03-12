# config/settings.py

import os
from dotenv import load_dotenv

# This reads your .env file and loads all key=value pairs
# into environment variables that os.getenv() can access
load_dotenv()

# ─── API KEYS ───────────────────────────────────────────────
# os.getenv() reads environment variables
# The second argument is a default value if the key isn't found
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# ─── RSS FEED SOURCES ───────────────────────────────────────
# Dictionary mapping a human-readable name to the RSS feed URL
# Each feed also has a default category and the source name
# This makes it easy to add/remove sources later
RSS_FEEDS = {
    "TOI_Top": {
        "url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        "source": "Times of India",
        "category": "General"
    },
    "TOI_Tech": {
        "url": "https://timesofindia.indiatimes.com/rssfeeds/66949542.cms",
        "source": "Times of India",
        "category": "Technology"
    },
    "TOI_Sports": {
        "url": "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
        "source": "Times of India",
        "category": "Sports"
    },
    "TOI_India": {
        "url": "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
        "source": "Times of India",
        "category": "Politics"
    },
    "BBC_World": {
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "source": "BBC News",
        "category": "World"
    },
    "BBC_Tech": {
        "url": "http://feeds.bbci.co.uk/news/technology/rss.xml",
        "source": "BBC News",
        "category": "Technology"
    },
    "BBC_Sports": {
        "url": "http://feeds.bbci.co.uk/news/sport/rss.xml",
        "source": "BBC News",
        "category": "Sports"
    },
    "BBC_Business": {
        "url": "http://feeds.bbci.co.uk/news/business/rss.xml",
        "source": "BBC News",
        "category": "Business"
    },
    "NDTV_Top": {
        "url": "https://feeds.feedburner.com/ndtvnews-top-stories",
        "source": "NDTV",
        "category": "General"
    },
    "Hindu_National": {
        "url": "https://www.thehindu.com/news/national/feeder/default.rss",
        "source": "The Hindu",
        "category": "Politics"
    },
    "Hindu_International": {
        "url": "https://www.thehindu.com/news/international/feeder/default.rss",
        "source": "The Hindu",
        "category": "World"
    },
    "Hindu_Science": {
        "url": "https://www.thehindu.com/sci-tech/science/feeder/default.rss",
        "source": "The Hindu",
        "category": "Science"
    },
}

# ─── NEWS CATEGORIES ────────────────────────────────────────
# All valid categories in our system
# This is used for validation and AI categorization
VALID_CATEGORIES = [
    "Politics",
    "Technology", 
    "Sports",
    "Entertainment",
    "Business",
    "World",
    "Science",
    "Health",
    "General"
]

# ─── AI CONFIGURATION ───────────────────────────────────────
# Which OpenAI model to use
# gpt-4o-mini is cheap (~$0.15 per million input tokens) and fast
# Perfect for hackathons where you need volume at low cost
LLM_MODEL = "gpt-4o-mini"

# Temperature controls randomness: 
# 0.0 = deterministic (same input → same output)
# 1.0 = very creative/random
# 0.3 = slightly creative but mostly factual (good for news)
LLM_TEMPERATURE = 0.3

# Maximum tokens the AI can generate in its response
# 60 words ≈ 80-100 tokens, we give buffer
LLM_MAX_TOKENS = 200

# How many articles to include per newsletter
MAX_ARTICLES_PER_NEWSLETTER = 15

# Summary word limit
SUMMARY_WORD_LIMIT = 60