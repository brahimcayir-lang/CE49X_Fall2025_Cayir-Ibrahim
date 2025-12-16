"""
Search URL generation utilities for CE x AI keyword pairs.
Supports site queries and NewsAPI templates.
"""

from urllib.parse import quote_plus
from typing import List, Dict


def _combine_terms(ce_terms: List[str], ai_terms: List[str]) -> List[str]:
    return [f"{ce} {ai}" for ce in ce_terms for ai in ai_terms]


def enr_search_urls(ce_terms: List[str], ai_terms: List[str], pages: int = 3) -> List[str]:
    """Build ENR site:search URLs across pages."""
    queries = _combine_terms(ce_terms, ai_terms)
    urls = []
    for q in queries:
        for page in range(1, pages + 1):
            encoded = quote_plus(q)
            urls.append(f"https://www.enr.com/search?query={encoded}&page={page}")
    return urls


def construction_dive_urls(ce_terms: List[str], ai_terms: List[str], pages: int = 3) -> List[str]:
    """Build Construction Dive site search URLs."""
    queries = _combine_terms(ce_terms, ai_terms)
    urls = []
    for q in queries:
        for page in range(1, pages + 1):
            encoded = quote_plus(q)
            urls.append(f"https://www.constructiondive.com/search/?q={encoded}&p={page}")
    return urls


def google_news_urls(ce_terms: List[str], ai_terms: List[str], pages: int = 2) -> List[str]:
    """Google News query URLs (non-API, HTML results)."""
    queries = _combine_terms(ce_terms, ai_terms)
    urls = []
    for q in queries:
        for page in range(pages):
            start = page * 10
            encoded = quote_plus(q)
            urls.append(f"https://news.google.com/search?q={encoded}&start={start}")
    return urls


def newsapi_requests(ce_terms: List[str], ai_terms: List[str], page_size: int = 50) -> List[Dict[str, str]]:
    """
    Build NewsAPI request params for each CE x AI query.
    Caller should supply NEWSAPI_KEY and use requests.get with the returned params.
    """
    queries = _combine_terms(ce_terms, ai_terms)
    return [
        {
            "url": "https://newsapi.org/v2/everything",
            "params": {
                "q": q,
                "pageSize": page_size,
                "language": "en",
                "sortBy": "relevancy",
            },
        }
        for q in queries
    ]


def aggregate_search_urls(ce_terms: List[str], ai_terms: List[str]) -> List[str]:
    """Collect all non-API search URLs."""
    return (
        enr_search_urls(ce_terms, ai_terms)
        + construction_dive_urls(ce_terms, ai_terms)
        + google_news_urls(ce_terms, ai_terms)
    )

