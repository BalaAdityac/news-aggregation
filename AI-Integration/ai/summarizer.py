# ai/summarizer.py

from openai import OpenAI
from typing import List
import logging
import time

from config.settings import (
    OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE, 
    LLM_MAX_TOKENS, SUMMARY_WORD_LIMIT
)
from models.schemas import RawArticle, SummarizedArticle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the OpenAI client
# This object handles all communication with OpenAI's API
client = OpenAI(api_key=OPENAI_API_KEY)

# ─── PROMPT TEMPLATES ────────────────────────────────────────

# System prompt: tells the AI WHO it is and HOW to behave
# This stays the same for every article
SYSTEM_PROMPT = """You are a professional news summarizer, similar to Inshorts.

Your rules:
1. Summarize the given news article in EXACTLY 60 words or fewer
2. Keep it factual and neutral — no opinions
3. Include the key details: WHO, WHAT, WHEN, WHERE, WHY
4. Make it engaging and easy to read
5. Do NOT start with "The article discusses..." or "This article is about..."
6. Start directly with the news content
7. Use active voice whenever possible
8. If the article content is too short or unclear, summarize based on the title"""

# User prompt: the actual article to summarize
# {title}, {source}, {content} will be replaced with real values
SUMMARIZE_PROMPT = """Summarize this news article in {word_limit} words or fewer:

Title: {title}
Source: {source}
Content: {content}

Provide ONLY the summary, nothing else."""

# Combined prompt for getting summary + importance + sentiment in one call
# This saves API calls (and money) by getting everything at once
ENHANCED_PROMPT = """Analyze this news article and provide:

1. SUMMARY: A {word_limit}-word summary (factual, engaging, Inshorts-style)
2. IMPORTANCE: Rate 1-10 (10 = critical breaking news, 1 = trivial)
3. SENTIMENT: Positive, Negative, or Neutral
4. WHY_IT_MATTERS: One sentence explaining significance

Title: {title}
Source: {source}
Content: {content}

Respond in EXACTLY this JSON format (no markdown, no code blocks):
{{"summary": "your summary here", "importance": 7, "sentiment": "Neutral", "why_it_matters": "one sentence here"}}"""


def summarize_single_article(article: RawArticle) -> SummarizedArticle:
    """
    Summarize a single article using GPT.
    
    How OpenAI's API works:
    - You send a list of 'messages' (conversation history)
    - Each message has a 'role': 'system', 'user', or 'assistant'
    - 'system' = instructions for how the AI should behave
    - 'user' = what you're asking it to do
    - 'assistant' = AI's previous responses (for multi-turn conversations)
    - The AI generates a response based on all messages
    
    Args:
        article: A RawArticle object to summarize
    
    Returns:
        A SummarizedArticle object with summary and AI analysis
    """
    try:
        # Prepare the content — use article content, fall back to title
        content = article.content if article.content else article.title
        
        # Truncate content to save tokens (and money)
        # GPT doesn't need 10,000 words to write a 60-word summary
        # First 3000 characters usually contain all the key information
        content = content[:3000]
        
        # Format the prompt with actual article data
        user_message = ENHANCED_PROMPT.format(
            word_limit=SUMMARY_WORD_LIMIT,
            title=article.title,
            source=article.source,
            content=content
        )
        
        # ─── MAKE THE API CALL ───────────────────────────
        response = client.chat.completions.create(
            model=LLM_MODEL,           # e.g., "gpt-4o-mini"
            messages=[
                {
                    "role": "system", 
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            max_tokens=LLM_MAX_TOKENS,   # Limit response length
            temperature=LLM_TEMPERATURE,  # 0.3 = mostly factual
        )
        
        # Extract the AI's response text
        result_text = response.choices[0].message.content.strip()
        
        # ─── PARSE THE JSON RESPONSE ────────────────────
        # The AI should return a JSON object
        import json
        
        # Sometimes the AI wraps it in ```json ... ```
        # Clean that up
        if result_text.startswith("```"):
            result_text = result_text.strip("`").strip()
            if result_text.startswith("json"):
                result_text = result_text[4:].strip()
        
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            # If JSON parsing fails, use the raw text as summary
            logger.warning(f"Failed to parse AI response as JSON for: {article.title[:50]}")
            result = {
                "summary": result_text[:300],  # Use raw text as summary
                "importance": 5,
                "sentiment": "Neutral",
                "why_it_matters": None
            }
        
        # ─── CREATE SUMMARIZED ARTICLE ───────────────────
        summarized = SummarizedArticle(
            original_id=article.id,
            title=article.title,
            summary=result.get("summary", "Summary unavailable."),
            category=article.category,
            source=article.source,
            url=article.url,
            image_url=article.image_url,
            published_at=article.published_at,
            importance_score=min(max(int(result.get("importance", 5)), 1), 10),
            sentiment=result.get("sentiment", "Neutral"),
            why_it_matters=result.get("why_it_matters")
        )
        
        logger.info(
            f"Summarized: {article.title[:50]}... "
            f"[Score: {summarized.importance_score}, {summarized.sentiment}]"
        )
        
        return summarized
        
    except Exception as e:
        logger.error(f"Error summarizing article '{article.title[:50]}': {e}")
        
        # Return a fallback summary so the pipeline doesn't break
        return SummarizedArticle(
            original_id=article.id,
            title=article.title,
            summary=f"{article.title}. {article.content[:200] if article.content else ''}",
            category=article.category,
            source=article.source,
            url=article.url,
            image_url=article.image_url,
            published_at=article.published_at,
            importance_score=5,
            sentiment="Neutral",
            why_it_matters=None
        )


def summarize_batch(
    articles: List[RawArticle], 
    delay: float = 0.2
) -> List[SummarizedArticle]:
    """
    Summarize multiple articles.
    
    Processes articles one by one with a small delay between calls.
    
    Why the delay?
    - OpenAI has rate limits (requests per minute)
    - gpt-4o-mini allows ~500 RPM on most tiers
    - 0.2 second delay = max 300 requests/minute = safely under limit
    
    For a hackathon, this sequential approach is fine.
    In production, you'd use async/parallel processing.
    
    Args:
        articles: List of raw articles to summarize
        delay: Seconds between API calls
    
    Returns:
        List of summarized articles
    """
    summaries = []
    total = len(articles)
    
    logger.info(f"Starting batch summarization of {total} articles...")
    
    for i, article in enumerate(articles):
        logger.info(f"Summarizing [{i+1}/{total}]: {article.title[:60]}...")
        
        summary = summarize_single_article(article)
        summaries.append(summary)
        
        # Don't delay after the last article
        if i < total - 1:
            time.sleep(delay)
    
    logger.info(f"Batch summarization complete: {len(summaries)} summaries generated")
    return summaries


def simple_summarize(title: str, content: str) -> str:
    """
    Quick and simple summarization — returns just the summary text.
    
    Use this for one-off summarizations where you don't need
    importance scores, sentiment, etc.
    
    Args:
        title: Article title
        content: Article content
    
    Returns:
        Summary string
    """
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user", 
                    "content": SUMMARIZE_PROMPT.format(
                        word_limit=SUMMARY_WORD_LIMIT,
                        title=title,
                        source="Unknown",
                        content=content[:3000]
                    )
                }
            ],
            max_tokens=150,
            temperature=LLM_TEMPERATURE,
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Simple summarization error: {e}")
        return f"{title}. {content[:150]}..."


# ─── TEST ────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test with a sample article
    test_article = RawArticle(
        title="India Successfully Launches Chandrayaan-4 Moon Mission",
        source="NDTV",
        category="Science",
        url="https://ndtv.com/test",
        content="""
        The Indian Space Research Organisation (ISRO) successfully launched 
        Chandrayaan-4, India's fourth lunar mission, from the Satish Dhawan 
        Space Centre in Sriharikota on Monday morning. The mission aims to 
        bring back lunar soil samples to Earth, making India only the fourth 
        country to achieve this feat after the US, Russia, and China. 
        ISRO Chairman Dr. S. Somanath said the spacecraft will reach the 
        Moon's orbit in approximately 25 days. The mission carries five 
        scientific instruments to study the lunar surface composition. 
        Prime Minister Narendra Modi congratulated the ISRO team and called 
        it a "historic moment for Indian science." The total cost of the 
        mission is estimated at Rs 2,104 crore.
        """
    )
    
    print("Testing summarization...\n")
    result = summarize_single_article(test_article)
    
    print(f"Title: {result.title}")
    print(f"Summary: {result.summary}")
    print(f"Importance: {result.importance_score}/10")
    print(f"Sentiment: {result.sentiment}")
    print(f"Why it matters: {result.why_it_matters}")