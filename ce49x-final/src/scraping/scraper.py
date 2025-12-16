"""
Scrape CE x AI articles from multiple sources.
"""

import os
import time
from typing import List
import requests
import pandas as pd

from .search_articles import aggregate_search_urls, newsapi_requests
from .extract_article import extract_article

RAW_PATH = os.path.join("data", "raw", "articles.csv")


def _fetch_newsapi_articles(ce_terms: List[str], ai_terms: List[str]) -> List[dict]:
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        return []

    results = []
    for req in newsapi_requests(ce_terms, ai_terms):
        try:
            resp = requests.get(req["url"], headers={"X-Api-Key": api_key}, params=req["params"], timeout=10)
            resp.raise_for_status()
            data = resp.json()
            for art in data.get("articles", []):
                results.append(
                    {
                        "title": art.get("title", ""),
                        "date": art.get("publishedAt", ""),
                        "source": art.get("source", {}).get("name", ""),
                        "url": art.get("url", ""),
                        "full_text": art.get("content", "") or art.get("description", ""),
                    }
                )
            time.sleep(1)  # be kind to API
        except requests.RequestException:
            continue
    return results


def _fetch_html_articles(urls: List[str]) -> List[dict]:
    articles = []
    for url in urls:
        article = extract_article(url)
        if article and article.get("full_text"):
            articles.append(article)
        time.sleep(0.5)
    return articles


def scrape_all_articles(ce_terms: List[str], ai_terms: List[str], limit: int = 200) -> pd.DataFrame:
    """
    Loop over CE x AI pairs, collect URLs, extract metadata + text, drop duplicate URLs, save to CSV.
    """
    search_urls = aggregate_search_urls(ce_terms, ai_terms)
    articles = _fetch_html_articles(search_urls)
    articles += _fetch_newsapi_articles(ce_terms, ai_terms)

    df = pd.DataFrame(articles)
    if not df.empty:
        df = df.drop_duplicates(subset=["url"]).head(limit)
        os.makedirs(os.path.dirname(RAW_PATH), exist_ok=True)
        df.to_csv(RAW_PATH, index=False)
    return df

