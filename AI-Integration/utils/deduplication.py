# utils/deduplication.py

from fuzzywuzzy import fuzz
from typing import List
import logging

from models.schemas import RawArticle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Similarity threshold (0-100)
# If two titles are > 75% similar, we consider them duplicates
# Too low = keeps duplicates; Too high = removes unique articles
SIMILARITY_THRESHOLD = 75


def deduplicate_articles(articles: List[RawArticle]) -> List[RawArticle]:
    """
    Remove duplicate articles from a list.
    
    How it works:
    1. Go through articles one by one
    2. For each article, compare its title with all previously 'accepted' articles
    3. If the title is too similar to any accepted article, skip it (it's a duplicate)
    4. If it's unique enough, add it to the accepted list
    
    We use 'fuzzy matching' because duplicates rarely have identical titles:
    - BBC: "India launches new space mission to study the Sun"
    - TOI: "India's new space mission launched to study Sun"
    These are clearly the same story but the titles differ slightly.
    
    fuzz.token_sort_ratio:
    - Splits both strings into words (tokens)
    - Sorts the words alphabetically
    - Compares the sorted strings
    - Returns a score from 0 (completely different) to 100 (identical)
    
    Why token_sort_ratio instead of simple ratio?
    - "India launches mission" vs "Mission launched by India"
    - simple ratio: might score low because word order differs
    - token_sort_ratio: sorts words first, so order doesn't matter → high score
    
    Args:
        articles: List of articles (may contain duplicates)
    
    Returns:
        List of unique articles
    """
    if not articles:
        return []
    
    unique_articles = []
    
    # Track titles we've seen (stored in lowercase for case-insensitive comparison)
    seen_titles = []
    
    for article in articles:
        title_lower = article.title.lower().strip()
        
        # Check if this title is too similar to any title we've already accepted
        is_duplicate = False
        
        for seen_title in seen_titles:
            # Calculate similarity score
            similarity = fuzz.token_sort_ratio(title_lower, seen_title)
            
            if similarity >= SIMILARITY_THRESHOLD:
                is_duplicate = True
                logger.debug(
                    f"Duplicate found (similarity={similarity}%):\n"
                    f"  Original: {seen_title[:80]}\n"
                    f"  Duplicate: {title_lower[:80]}"
                )
                break  # No need to check more — one match is enough
        
        if not is_duplicate:
            unique_articles.append(article)
            seen_titles.append(title_lower)
    
    removed_count = len(articles) - len(unique_articles)
    logger.info(
        f"Deduplication: {len(articles)} → {len(unique_articles)} "
        f"({removed_count} duplicates removed)"
    )
    
    return unique_articles


def deduplicate_by_url(articles: List[RawArticle]) -> List[RawArticle]:
    """
    Simpler deduplication — just check if URLs are the same.
    
    This catches exact duplicates (same URL appearing twice)
    but misses different URLs covering the same story.
    
    Use this as a quick first pass, then use deduplicate_articles()
    for the thorough check.
    """
    seen_urls = set()  # Sets have O(1) lookup — very fast
    unique = []
    
    for article in articles:
        # Normalize URL: remove trailing slash, lowercase
        normalized_url = article.url.lower().rstrip("/")
        
        if normalized_url not in seen_urls:
            seen_urls.add(normalized_url)
            unique.append(article)
    
    return unique


# ─── TEST ────────────────────────────────────────────────────
if __name__ == "__main__":
    # Create test articles with intentional duplicates
    test_articles = [
        RawArticle(title="India launches new space mission to study the Sun", 
                   source="BBC", url="https://bbc.com/1", content="test"),
        RawArticle(title="India's new space mission launched to study Sun", 
                   source="TOI", url="https://toi.com/1", content="test"),
        RawArticle(title="PM Modi meets US President Biden at G20 Summit", 
                   source="NDTV", url="https://ndtv.com/1", content="test"),
        RawArticle(title="Modi-Biden meeting at G20 Summit", 
                   source="Hindu", url="https://hindu.com/1", content="test"),
        RawArticle(title="New iPhone 16 features leaked online", 
                   source="BBC", url="https://bbc.com/2", content="test"),
    ]
    
    print(f"Before dedup: {len(test_articles)} articles")
    unique = deduplicate_articles(test_articles)
    print(f"After dedup: {len(unique)} articles")
    
    for a in unique:
        print(f"  - [{a.source}] {a.title}")