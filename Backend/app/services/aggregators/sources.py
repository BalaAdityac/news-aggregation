from __future__ import annotations

from ...schemas.article import Category


RSS_SOURCES = [
    {
        "name": "NDTV",
        "url": "https://feeds.feedburner.com/ndtvnews-top-stories",
        "language": "en",
        "country": "IN",
        "default_category": Category.INTERNATIONAL,
    },
    {
        "name": "The Hindu",
        "url": "https://www.thehindu.com/feeder/default.rss",
        "language": "en",
        "country": "IN",
        "default_category": Category.INTERNATIONAL,
    },
    {
        "name": "Times of India",
        "url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        "language": "en",
        "country": "IN",
        "default_category": Category.INTERNATIONAL,
    },
    {
        "name": "Times of India - Tech",
        "url": "https://timesofindia.indiatimes.com/rssfeeds/66949542.cms",
        "language": "en",
        "country": "IN",
        "default_category": Category.TECHNOLOGY,
    },
    {
        "name": "Times of India - Sports",
        "url": "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
        "language": "en",
        "country": "IN",
        "default_category": Category.SPORTS,
    },
    {
        "name": "BBC News",
        "url": "http://feeds.bbci.co.uk/news/rss.xml",
        "language": "en",
        "country": "GB",
        "default_category": Category.INTERNATIONAL,
    },
    {
        "name": "BBC Technology",
        "url": "http://feeds.bbci.co.uk/news/technology/rss.xml",
        "language": "en",
        "country": "GB",
        "default_category": Category.TECHNOLOGY,
    },
    {
        "name": "Reuters",
        "url": "https://feeds.reuters.com/reuters/topNews",
        "language": "en",
        "country": "US",
        "default_category": Category.INTERNATIONAL,
    },
]
