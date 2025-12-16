"""
RSS feed ingestion for AEC/AI sources.
"""

from typing import List, Dict
import feedparser

DEFAULT_FEEDS = [
    "https://www.enr.com/rss/articles",
    "https://www.constructiondive.com/feeds/news/",
    "https://www.engineering.com/rss",  # Engineering.com
    "https://www.techcrunch.com/tag/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/",
]


def fetch_rss_articles(feed_urls: List[str] = None) -> List[Dict]:
    """
    Parse RSS feeds and return standardized article records.

    Each record fields:
        - title
        - date
        - source
        - url
        - full_text (summary/description if full not available)
        - source_type
    """
    urls = feed_urls or DEFAULT_FEEDS
    articles: List[Dict] = []

    for feed_url in urls:
        parsed = feedparser.parse(feed_url)
        source = parsed.feed.get("title", feed_url)
        for entry in parsed.entries:
            articles.append(
                {
                    "title": entry.get("title", ""),
                    "date": entry.get("published", "") or entry.get("updated", ""),
                    "source": source,
                    "url": entry.get("link", ""),
                    "full_text": entry.get("summary", "") or entry.get("description", ""),
                    "source_type": "rss",
                    "raw_source": feed_url,
                }
            )
    return articles





