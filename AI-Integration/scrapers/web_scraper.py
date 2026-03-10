# scrapers/web_scraper.py

import requests
from bs4 import BeautifulSoup
from typing import Optional
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pretend to be a web browser
# Without this, many websites block your request because they detect
# you're a script/bot. User-Agent makes your request look like
# it's coming from a real Chrome browser.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_article_content(url: str) -> Optional[str]:
    """
    Scrape the full text content from a news article URL.
    
    How web scraping works:
    1. Send an HTTP GET request to the URL (like a browser visiting the page)
    2. Receive the HTML response (the raw page code)
    3. Parse the HTML with BeautifulSoup
    4. Find the article content by looking for specific HTML tags
    5. Extract just the text, removing ads, menus, etc.
    
    This is a GENERIC scraper — it tries common patterns used by
    most news websites. It won't work perfectly for every site,
    but it works well enough for most.
    
    Args:
        url: The article's URL
    
    Returns:
        Extracted article text, or None if scraping failed
    """
    try:
        # Send the request with a 10-second timeout
        # If the website doesn't respond in 10 seconds, give up
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # Parse the HTML
        # 'html.parser' is Python's built-in parser — no extra dependencies
        soup = BeautifulSoup(response.text, "html.parser")
        
        # ─── REMOVE UNWANTED ELEMENTS ───────────────────
        # News pages have lots of junk: navigation bars, ads,
        # related articles, social media buttons, scripts, etc.
        # We remove these BEFORE extracting text.
        unwanted_tags = [
            "script",      # JavaScript code
            "style",       # CSS styling
            "nav",         # Navigation menus
            "header",      # Page header
            "footer",      # Page footer
            "aside",       # Sidebars
            "iframe",      # Embedded content (ads, videos)
            "form",        # Forms
            "button",      # Buttons
            "figure",      # Image captions (often noisy)
        ]
        
        # Also remove elements with these CSS classes/IDs
        # These are common patterns for non-article content
        unwanted_classes = [
            "advertisement", "ad-container", "sidebar",
            "related-articles", "social-share", "comments",
            "newsletter-signup", "popup", "modal",
            "breadcrumb", "navigation"
        ]
        
        # Remove unwanted tags
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()  # .decompose() removes the element entirely
        
        # Remove elements with unwanted classes
        for cls in unwanted_classes:
            for element in soup.find_all(class_=lambda c: c and cls in str(c).lower()):
                element.decompose()
        
        # ─── FIND THE ARTICLE CONTENT ───────────────────
        # News websites typically wrap article text in an <article> tag
        # or a <div> with a class like 'article-body', 'story-content', etc.
        # We try multiple strategies in order of reliability.
        
        content = None
        
        # Strategy 1: Look for <article> tag (most standard)
        article_tag = soup.find("article")
        if article_tag:
            content = article_tag.get_text(separator=" ", strip=True)
        
        # Strategy 2: Look for common article container class names
        if not content or len(content) < 100:
            content_selectors = [
                {"class_": "article-body"},
                {"class_": "story-body"},
                {"class_": "article-content"},
                {"class_": "story-content"},
                {"class_": "entry-content"},
                {"class_": "post-content"},
                {"class_": "article__body"},
                {"class_": "content-body"},
                {"itemprop": "articleBody"},  # Schema.org markup
            ]
            
            for selector in content_selectors:
                element = soup.find("div", selector)
                if element:
                    text = element.get_text(separator=" ", strip=True)
                    if len(text) > 100:  # Must have meaningful content
                        content = text
                        break
        
        # Strategy 3: Find the largest block of <p> tags
        # Most article text is in <p> (paragraph) tags
        # The cluster of <p> tags with the most total text is likely the article
        if not content or len(content) < 100:
            paragraphs = soup.find_all("p")
            if paragraphs:
                # Join all paragraph text
                content = " ".join(
                    p.get_text(strip=True) 
                    for p in paragraphs 
                    if len(p.get_text(strip=True)) > 30  # Skip tiny paragraphs
                )
        
        # ─── CLEAN UP THE TEXT ───────────────────────────
        if content:
            # Remove excessive whitespace
            # Multiple spaces, newlines, tabs → single space
            import re
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Limit to ~5000 characters (we don't need the entire article)
            # The AI summarizer only needs the first portion anyway
            content = content[:5000]
            
            # Only return if we got meaningful content
            if len(content) > 50:
                return content
        
        logger.warning(f"Could not extract meaningful content from {url}")
        return None
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout scraping {url}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error scraping {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return None


def enrich_articles_with_full_content(articles: list, delay: float = 0.5) -> list:
    """
    Take a list of articles and try to fetch full content for those
    that only have short descriptions.
    
    RSS feeds often only give you 1-2 sentence descriptions.
    This function visits each article URL and scrapes the full text.
    
    Args:
        articles: List of RawArticle objects
        delay: Seconds to wait between requests (be polite to servers!)
    
    Returns:
        Same list with content field enriched where possible
    """
    enriched_count = 0
    
    for article in articles:
        # Only scrape if the current content is too short to summarize well
        if len(article.content) < 200:
            logger.info(f"Enriching: {article.title[:60]}...")
            
            full_content = scrape_article_content(article.url)
            
            if full_content and len(full_content) > len(article.content):
                article.content = full_content
                enriched_count += 1
            
            # Be polite — don't hammer servers with rapid requests
            # This delay prevents your IP from being blocked
            time.sleep(delay)
    
    logger.info(f"Enriched {enriched_count}/{len(articles)} articles with full content")
    return articles


# ─── TEST ────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test with a known article URL
    test_url = "https://www.bbc.com/news/technology"
    
    print(f"Scraping: {test_url}\n")
    content = scrape_article_content(test_url)
    
    if content:
        print(f"Content length: {len(content)} characters")
        print(f"First 500 chars:\n{content[:500]}")
    else:
        print("Failed to extract content")