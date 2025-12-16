"""
Google News scraping via SerpAPI (if key available) or HTML fallback.
"""

import os
import time
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CE49X/1.0)"}


def _standardize(item: Dict, source: str = "google_news") -> Dict:
    return {
        "title": item.get("title", ""),
        "date": item.get("date", ""),
        "source": item.get("source", "") or source,
        "url": item.get("url", ""),
        "full_text": item.get("snippet", "") or item.get("full_text", ""),
        "source_type": "google_news",
        "raw_source": source,
    }


def _serpapi_search(query: str, num_pages: int, api_key: str) -> List[Dict]:
    results: List[Dict] = []
    if not (SERPAPI_AVAILABLE and api_key):
        return results
    for page in range(num_pages):
        params = {"engine": "google_news", "q": query, "api_key": api_key, "start": page * 10}
        search = GoogleSearch(params)
        data = search.get_dict()
        for item in data.get("news_results", []) or []:
            results.append(
                _standardize(
                    {
                        "title": item.get("title", ""),
                        "date": item.get("date", ""),
                        "source": item.get("source", {}).get("name", "GoogleNewsSerpAPI") if isinstance(item.get("source"), dict) else "GoogleNewsSerpAPI",
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                    }
                )
            )
        time.sleep(0.5)
    return results


def _html_search(query: str, num_pages: int) -> List[Dict]:
    results: List[Dict] = []
    for page in range(num_pages):
        start = page * 10
        url = f"https://news.google.com/search?q={requests.utils.quote(query)}&start={start}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for article in soup.select("article"):
                title_tag = article.find("a")
                title = title_tag.get_text(strip=True) if title_tag else ""
                link = title_tag["href"] if title_tag and title_tag.has_attr("href") else ""
                if link.startswith("./"):
                    link = "https://news.google.com" + link[1:]
                snippet_tag = article.find("span")
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                results.append(_standardize({"title": title, "url": link, "snippet": snippet}, source="GoogleNewsHTML"))
            time.sleep(0.3)
        except requests.RequestException:
            continue
    return results


def search_google_news(ce_terms: List[str], ai_terms: List[str], num_pages: int = 5) -> List[Dict]:
    """
    Generate Google News queries using CE × AI keyword matrix and return standardized results.
    """
    api_key = os.getenv("SERPAPI_KEY")
    queries = [f"{ce} {ai}" for ce in ce_terms for ai in ai_terms]
    articles: List[Dict] = []
    for q in queries:
        if api_key:
            articles.extend(_serpapi_search(q, num_pages=num_pages, api_key=api_key))
        else:
            articles.extend(_html_search(q, num_pages=num_pages))
    return articles





