# scrapers/rss_scraper.py

import feedparser
from datetime import datetime
from typing import List
import logging

# Import our settings and data models
from config.settings import RSS_FEEDS
from models.schemas import RawArticle

# Set up logging — this prints informative messages to the console
# so you can track what's happening when the scraper runs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# __name__ makes the logger show which file the message came from


def parse_single_feed(feed_name: str, feed_config: dict) -> List[RawArticle]:
    """
    Parse a single RSS feed and return a list of RawArticle objects.
    
    How RSS feeds work:
    - Each feed URL returns XML data
    - feedparser library converts this XML into Python objects
    - Each 'entry' in the feed is one article
    - We extract title, link, description, date from each entry
    
    Args:
        feed_name: Human-readable identifier like "BBC_Tech"
        feed_config: Dict with 'url', 'source', 'category' keys
    
    Returns:
        List of RawArticle objects
    """
    articles = []
    
    try:
        # feedparser.parse() fetches the URL and parses the XML
        # It returns a FeedParserDict object with feed metadata and entries
        feed = feedparser.parse(feed_config["url"])
        
        # Check if the feed was parsed successfully
        # feed.bozo is True if there was a parsing error
        if feed.bozo and not feed.entries:
            logger.warning(f"Failed to parse feed: {feed_name}")
            return articles
        
        logger.info(f"Parsing {feed_name}: found {len(feed.entries)} entries")
        
        # Loop through each article (entry) in the feed
        for entry in feed.entries:
            try:
                # ─── EXTRACT TITLE ───────────────────────────
                # .get() is safer than direct access — returns default if key missing
                title = entry.get("title", "").strip()
                if not title:
                    continue  # Skip articles without titles
                
                # ─── EXTRACT URL ─────────────────────────────
                url = entry.get("link", "").strip()
                if not url:
                    continue  # Skip articles without URLs
                
                # ─── EXTRACT CONTENT ─────────────────────────
                # RSS feeds usually have a 'summary' or 'description' field
                # This contains a short preview of the article
                # Some feeds put the full content in 'content'
                content = ""
                
                # Try 'content' first (some feeds put full text here)
                if "content" in entry and entry.content:
                    # entry.content is a list of dicts
                    content = entry.content[0].get("value", "")
                
                # Fall back to 'summary' or 'description'
                if not content:
                    content = entry.get("summary", entry.get("description", ""))
                
                # Clean HTML tags from content
                # RSS descriptions often contain HTML markup
                content = _strip_html(content)
                
                # ─── EXTRACT PUBLICATION DATE ────────────────
                published = entry.get("published", entry.get("updated", ""))
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    # Convert time.struct_time to ISO format string
                    try:
                        published = datetime(*entry.published_parsed[:6]).isoformat()
                    except (TypeError, ValueError):
                        published = datetime.utcnow().isoformat()
                
                # ─── EXTRACT IMAGE ───────────────────────────
                image_url = _extract_image(entry)
                
                # ─── CREATE ARTICLE OBJECT ───────────────────
                article = RawArticle(
                    title=title,
                    source=feed_config["source"],
                    category=feed_config["category"],
                    url=url,
                    content=content[:5000],  # Limit content length
                    image_url=image_url,
                    published_at=published
                )
                articles.append(article)
                
            except Exception as e:
                # If one article fails, log it and continue to the next
                # Don't let one bad entry kill the whole feed
                logger.error(f"Error parsing entry in {feed_name}: {e}")
                continue
        
        logger.info(f"Successfully parsed {len(articles)} articles from {feed_name}")
        
    except Exception as e:
        logger.error(f"Error fetching feed {feed_name}: {e}")
    
    return articles


def _strip_html(text: str) -> str:
    """
    Remove HTML tags from text.
    
    RSS descriptions often look like:
    '<p>The <b>Prime Minister</b> said...</p>'
    
    We want: 'The Prime Minister said...'
    
    BeautifulSoup parses HTML and .get_text() extracts just the text.
    """
    if not text:
        return ""
    
    from bs4 import BeautifulSoup
    # 'html.parser' is Python's built-in HTML parser
    soup = BeautifulSoup(text, "html.parser")
    # get_text() extracts all text, separator=" " adds space between elements
    clean_text = soup.get_text(separator=" ", strip=True)
    return clean_text


def _extract_image(entry) -> str:
    """
    Try to extract an image URL from an RSS entry.
    
    Images can be in several places in RSS:
    1. media_content — standard media RSS extension
    2. media_thumbnail — smaller preview image
    3. enclosures — attachments to the entry
    4. Inside the HTML content itself
    
    We try each in order and return the first one found.
    """
    # Method 1: media:content tag
    if hasattr(entry, "media_content") and entry.media_content:
        for media in entry.media_content:
            if "url" in media:
                return media["url"]
    
    # Method 2: media:thumbnail tag
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        for thumb in entry.media_thumbnail:
            if "url" in thumb:
                return thumb["url"]
    
    # Method 3: enclosures (like email attachments)
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image"):
                return enc.get("href", enc.get("url", ""))
    
    # Method 4: Look for <img> tags inside the summary/content HTML
    summary_html = entry.get("summary", "")
    if "<img" in summary_html:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(summary_html, "html.parser")
        img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            return img_tag["src"]
    
    return None


def fetch_all_rss_feeds() -> List[RawArticle]:
    """
    Fetch articles from ALL configured RSS feeds.
    
    This is the main function you'll call from your API.
    It loops through every feed defined in settings.py,
    parses each one, and combines all articles into one list.
    
    Returns:
        Combined list of RawArticle objects from all feeds
    """
    all_articles = []
    
    logger.info(f"Starting RSS fetch from {len(RSS_FEEDS)} feeds...")
    
    for feed_name, feed_config in RSS_FEEDS.items():
        articles = parse_single_feed(feed_name, feed_config)
        all_articles.extend(articles)  # .extend() adds all items from one list to another
    
    logger.info(f"Total articles fetched from RSS: {len(all_articles)}")
    return all_articles


def fetch_feeds_by_category(category: str) -> List[RawArticle]:
    """
    Fetch articles only from feeds matching a specific category.
    
    Useful when a user only wants Tech news — no need to fetch
    Politics feeds.
    
    Args:
        category: Category to filter by (e.g., "Technology")
    
    Returns:
        List of RawArticle objects matching that category
    """
    articles = []
    
    for feed_name, feed_config in RSS_FEEDS.items():
        if feed_config["category"].lower() == category.lower():
            feed_articles = parse_single_feed(feed_name, feed_config)
            articles.extend(feed_articles)
    
    return articles


# ─── TEST THE RSS SCRAPER ────────────────────────────────────
# This block only runs if you execute this file directly:
#   python scrapers/rss_scraper.py
# It does NOT run when another file imports from this module
if __name__ == "__main__":
    articles = fetch_all_rss_feeds()
    
    print(f"\n{'='*60}")
    print(f"Fetched {len(articles)} total articles")
    print(f"{'='*60}\n")
    
    # Show first 5 articles as preview
    for i, article in enumerate(articles[:5]):
        print(f"Article {i+1}:")
        print(f"  Title:    {article.title}")
        print(f"  Source:   {article.source}")
        print(f"  Category: {article.category}")
        print(f"  URL:      {article.url[:80]}...")
        print(f"  Content:  {article.content[:150]}...")
        print()