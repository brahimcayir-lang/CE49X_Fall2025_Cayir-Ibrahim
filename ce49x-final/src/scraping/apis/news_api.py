"""
API-based news ingestion with optional providers.
"""

import os
import time
from typing import List, Dict, Optional
import requests


def _standardize_article(item: Dict, source: str, url_field: str = "url") -> Dict:
    return {
        "title": item.get("title", ""),
        "date": item.get("publishedAt", "") or item.get("date", "") or item.get("published", ""),
        "source": item.get("source", "") or source,
        "url": item.get(url_field, "") or item.get("link", ""),
        "full_text": item.get("content", "") or item.get("description", ""),
        "source_type": "api",
        "raw_source": source,
    }


def _newsapi_fetch(query: str, key: str, page_size: int = 100, pages: int = 3) -> List[Dict]:
    if not key:
        return []
    results = []
    for page in range(1, pages + 1):
        params = {
            "q": query,
            "language": "en",
            "pageSize": page_size,
            "page": page,
            "sortBy": "relevancy",
        }
        try:
            resp = requests.get("https://newsapi.org/v2/everything", params=params, headers={"X-Api-Key": key}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            for art in data.get("articles", []):
                art["source"] = art.get("source", {}).get("name", "NewsAPI")
                results.append(_standardize_article(art, "NewsAPI"))
            time.sleep(0.5)
        except requests.RequestException:
            continue
    return results


def _gdelt_fetch(query: str, max_records: int = 250) -> List[Dict]:
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {"query": query, "maxrecords": max_records, "format": "json"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        arts = data.get("articles", [])
        return [
            {
                "title": a.get("title", ""),
                "date": a.get("seendate", ""),
                "source": a.get("sourceCommonName", "GDELT"),
                "url": a.get("url", ""),
                "full_text": a.get("sourceArticleText", "") or a.get("excerpt", ""),
                "source_type": "api",
                "raw_source": "GDELT",
            }
            for a in arts
        ]
    except requests.RequestException:
        return []


def _mediastack_fetch(query: str, key: str, limit: int = 100) -> List[Dict]:
    if not key:
        return []
    params = {"access_key": key, "languages": "en", "keywords": query, "limit": limit}
    try:
        resp = requests.get("http://api.mediastack.com/v1/news", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return [
            _standardize_article(
                {
                    "title": a.get("title", ""),
                    "publishedAt": a.get("published_at", ""),
                    "source": a.get("source", "mediastack"),
                    "url": a.get("url", ""),
                    "description": a.get("description", ""),
                },
                "mediastack",
            )
            for a in data.get("data", [])
        ]
    except requests.RequestException:
        return []


def _bing_fetch(query: str, key: str, count: int = 50, pages: int = 2) -> List[Dict]:
    if not key:
        return []
    headers = {"Ocp-Apim-Subscription-Key": key}
    results = []
    for offset in range(0, count * pages, count):
        params = {"q": query, "count": count, "offset": offset, "mkt": "en-US", "sortBy": "Date"}
        try:
            resp = requests.get("https://api.bing.microsoft.com/v7.0/news/search", headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            for a in data.get("value", []):
                results.append(
                    _standardize_article(
                        {
                            "title": a.get("name", ""),
                            "publishedAt": a.get("datePublished", ""),
                            "source": a.get("provider", [{}])[0].get("name", "Bing"),
                            "url": a.get("url", ""),
                            "description": a.get("description", ""),
                        },
                        "Bing",
                    )
                )
            time.sleep(0.5)
        except requests.RequestException:
            continue
    return results


def fetch_api_articles(
    query_terms: List[str],
    max_results: int = 500,
    use_newsapi: bool = True,
    use_gdelt: bool = True,
    use_mediastack: bool = False,
    use_bing: bool = False,
    api_keys: Optional[Dict[str, str]] = None,
) -> List[Dict]:
    """
    Query news APIs for civil engineering + AI keywords.
    query_terms: list of query strings (e.g., CE x AI combinations)
    Returns standardized list of records.
    """
    keys = api_keys or {}
    newsapi_key = keys.get("NEWSAPI_KEY") or os.getenv("NEWSAPI_KEY")
    mediastack_key = keys.get("MEDIASTACK_KEY") or os.getenv("MEDIASTACK_KEY")
    bing_key = keys.get("BING_API_KEY") or os.getenv("BING_API_KEY")

    articles: List[Dict] = []
    per_query_limit = max_results // max(1, len(query_terms))

    for q in query_terms:
        if use_newsapi:
            articles.extend(_newsapi_fetch(q, newsapi_key, page_size=min(100, per_query_limit), pages=2))
        if use_gdelt:
            articles.extend(_gdelt_fetch(q, max_records=min(250, per_query_limit)))
        if use_mediastack:
            articles.extend(_mediastack_fetch(q, mediastack_key, limit=min(100, per_query_limit)))
        if use_bing:
            articles.extend(_bing_fetch(q, bing_key, count=min(50, per_query_limit), pages=1))
    return articles





