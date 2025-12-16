"""
Article extraction helper.
"""

import re
from typing import Dict, Optional
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CE49X/1.0; +https://example.edu)"
}


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_article(url: str) -> Optional[Dict[str, str]]:
    """
    Returns title, date, source, url, full_text.
    Handles missing dates gracefully.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    title_tag = soup.find("title") or soup.find("h1")
    title = _clean_text(title_tag.get_text()) if title_tag else ""

    # common date patterns
    date_tag = soup.find("time") or soup.find("meta", {"property": "article:published_time"}) or soup.find(
        "meta", {"name": "pubdate"}
    )
    if date_tag and date_tag.has_attr("datetime"):
        date = date_tag["datetime"]
    elif date_tag and date_tag.has_attr("content"):
        date = date_tag["content"]
    elif date_tag:
        date = date_tag.get_text(strip=True)
    else:
        date = ""

    # article text aggregation
    paragraphs = soup.find_all("p")
    body = " ".join([p.get_text(" ", strip=True) for p in paragraphs])
    full_text = _clean_text(body)

    source = ""
    domain_match = re.search(r"https?://([^/]+)/", url)
    if domain_match:
        source = domain_match.group(1)

    return {
        "title": title,
        "date": date,
        "source": source,
        "url": url,
        "full_text": full_text,
    }

