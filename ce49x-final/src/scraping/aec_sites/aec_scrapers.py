"""
Dedicated scrapers for AEC news sites.
These are shallow search/pagination scrapers to stay light for laptop-scale runs.
"""

import time
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CE49X/1.0)"}


def _standardize(title: str, url: str, source: str, snippet: str = "", date: str = "") -> Dict:
    return {
        "title": title or "",
        "date": date or "",
        "source": source,
        "url": url or "",
        "full_text": snippet or "",
        "source_type": "site",
        "raw_source": source,
    }


def _fetch(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException:
        return None


def scrape_enr(keyword: str, page_limit: int = 5) -> List[Dict]:
    articles: List[Dict] = []
    for page in range(page_limit):
        url = f"https://www.enr.com/search?q={requests.utils.quote(keyword)}&page={page+1}"
        soup = _fetch(url)
        if not soup:
            continue
        for h2 in soup.select("h2 a"):
            title = h2.get_text(strip=True)
            link = h2.get("href", "")
            if link.startswith("/"):
                link = "https://www.enr.com" + link
            articles.append(_standardize(title, link, "ENR"))
        time.sleep(0.3)
    return articles


def scrape_construction_dive(keyword: str, page_limit: int = 5) -> List[Dict]:
    articles: List[Dict] = []
    for page in range(1, page_limit + 1):
        url = f"https://www.constructiondive.com/search/?q={requests.utils.quote(keyword)}&p={page}"
        soup = _fetch(url)
        if not soup:
            continue
        for item in soup.select("h3 a"):
            title = item.get_text(strip=True)
            link = item.get("href", "")
            if link.startswith("/"):
                link = "https://www.constructiondive.com" + link
            articles.append(_standardize(title, link, "ConstructionDive"))
        time.sleep(0.3)
    return articles


def scrape_civil_structural(keyword: str, page_limit: int = 5) -> List[Dict]:
    articles: List[Dict] = []
    for page in range(1, page_limit + 1):
        url = f"https://csengineermag.com/?s={requests.utils.quote(keyword)}&paged={page}"
        soup = _fetch(url)
        if not soup:
            continue
        for h2 in soup.select("h2.entry-title a"):
            title = h2.get_text(strip=True)
            link = h2.get("href", "")
            articles.append(_standardize(title, link, "CivilStructuralEngineer"))
        time.sleep(0.3)
    return articles


def scrape_engineering_com(keyword: str, page_limit: int = 5) -> List[Dict]:
    articles: List[Dict] = []
    for page in range(1, page_limit + 1):
        url = f"https://www.engineering.com/search?q={requests.utils.quote(keyword)}&page={page}"
        soup = _fetch(url)
        if not soup:
            continue
        for h2 in soup.select("h3 a, h2 a"):
            title = h2.get_text(strip=True)
            link = h2.get("href", "")
            if link.startswith("/"):
                link = "https://www.engineering.com" + link
            articles.append(_standardize(title, link, "Engineering.com"))
        time.sleep(0.3)
    return articles


def scrape_bimplus(keyword: str, page_limit: int = 5) -> List[Dict]:
    articles: List[Dict] = []
    for page in range(1, page_limit + 1):
        url = f"https://www.bimplus.co.uk/?s={requests.utils.quote(keyword)}&paged={page}"
        soup = _fetch(url)
        if not soup:
            continue
        for h2 in soup.select("h2.entry-title a"):
            title = h2.get_text(strip=True)
            link = h2.get("href", "")
            articles.append(_standardize(title, link, "BIMPlus"))
        time.sleep(0.3)
    return articles


def scrape_new_civil_engineer(keyword: str, page_limit: int = 5) -> List[Dict]:
    articles: List[Dict] = []
    for page in range(1, page_limit + 1):
        url = f"https://www.newcivilengineer.com/search/{requests.utils.quote(keyword)}/page/{page}"
        soup = _fetch(url)
        if not soup:
            continue
        for h2 in soup.select("h2 a"):
            title = h2.get_text(strip=True)
            link = h2.get("href", "")
            articles.append(_standardize(title, link, "NewCivilEngineer"))
        time.sleep(0.3)
    return articles





