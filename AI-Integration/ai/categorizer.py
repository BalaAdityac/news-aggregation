# ai/categorizer.py

from openai import OpenAI
from typing import List
import logging
import json

from config.settings import OPENAI_API_KEY, LLM_MODEL, VALID_CATEGORIES
from models.schemas import RawArticle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

CATEGORIZE_PROMPT = """Classify this news article into exactly ONE of these categories:
{categories}

Article Title: {title}
Article Content: {content}

Respond with ONLY the category name, nothing else. 
Example response: Technology"""


def categorize_article(article: RawArticle) -> str:
    """
    Use AI to determine the category of an article.
    
    This is useful when:
    - RSS feed doesn't specify a category
    - NewsAPI assigns "general" but it's really about technology
    - Web-scraped articles have no metadata
    
    Args:
        article: The article to categorize
    
    Returns:
        Category string (e.g., "Technology", "Sports")
    """
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": CATEGORIZE_PROMPT.format(
                        categories=", ".join(VALID_CATEGORIES),
                        title=article.title,
                        content=article.content[:500]  # Only need beginning for classification
                    )
                }
            ],
            max_tokens=20,       # Category name is at most 2-3 words
            temperature=0.1,     # Very low — we want consistent categorization
        )
        
        category = response.choices[0].message.content.strip()
        
        # Validate: make sure the AI returned one of our valid categories
        if category in VALID_CATEGORIES:
            return category
        
        # If not exact match, try case-insensitive match
        for valid_cat in VALID_CATEGORIES:
            if valid_cat.lower() == category.lower():
                return valid_cat
        
        # If AI returned something weird, default to "General"
        logger.warning(f"AI returned invalid category '{category}' for '{article.title[:50]}'. Defaulting to General.")
        return "General"
        
    except Exception as e:
        logger.error(f"Categorization error for '{article.title[:50]}': {e}")
        return "General"


def categorize_batch(articles: List[RawArticle]) -> List[RawArticle]:
    """
    Categorize multiple articles that have 'General' or empty categories.
    
    Only processes articles that need categorization — if an article
    already has a specific category from RSS, we keep it.
    
    Args:
        articles: List of articles to potentially categorize
    
    Returns:
        Same list with updated categories
    """
    recategorized = 0
    
    for article in articles:
        # Only re-categorize if the category is generic
        if article.category in ["General", "", None]:
            new_category = categorize_article(article)
            if new_category != article.category:
                article.category = new_category
                recategorized += 1
    
    logger.info(f"Re-categorized {recategorized} articles")
    return articles


# For efficiency, categorize multiple articles in one API call
def batch_categorize_efficient(articles: List[RawArticle]) -> List[RawArticle]:
    """
    Categorize up to 10 articles in a single API call to save money.
    
    Instead of one API call per article, we send multiple titles
    at once and ask the AI to categorize all of them.
    """
    # Only process articles needing categorization
    needs_categorization = [
        (i, a) for i, a in enumerate(articles) 
        if a.category in ["General", "", None]
    ]
    
    if not needs_categorization:
        return articles
    
    # Process in batches of 10
    batch_size = 10
    for batch_start in range(0, len(needs_categorization), batch_size):
        batch = needs_categorization[batch_start:batch_start + batch_size]
        
        # Build prompt with multiple articles
        articles_text = ""
        for idx, (original_idx, article) in enumerate(batch):
            articles_text += f"{idx+1}. {article.title}\n"
        
        prompt = f"""Classify each article into one category from: {', '.join(VALID_CATEGORIES)}

Articles:
{articles_text}

Respond as a JSON list of categories in order. Example: ["Technology", "Sports", "Politics"]
Only return the JSON list, nothing else."""
        
        try:
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1,
            )
            
            result_text = response.choices[0].message.content.strip()
            categories = json.loads(result_text)
            
            # Apply categories back to articles
            for (original_idx, article), category in zip(batch, categories):
                if category in VALID_CATEGORIES:
                    articles[original_idx].category = category
                    
        except Exception as e:
            logger.error(f"Batch categorization error: {e}")
            # Fall back to individual categorization
            for original_idx, article in batch:
                articles[original_idx].category = categorize_article(article)
    
    return articles