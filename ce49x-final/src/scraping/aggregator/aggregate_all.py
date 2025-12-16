"""
Aggregate all ingestion layers into a single DataFrame and CSV.
"""

import glob
import json
import os
from typing import List, Dict

import pandas as pd

from src.scraping.rss.rss_scraper import fetch_rss_articles
from src.scraping.apis.news_api import fetch_api_articles
from src.scraping.google_news.search_google_news import search_google_news
from src.scraping.aec_sites import aec_scrapers
from src.scraping.scraper import scrape_all_articles as legacy_scrape

RAW_MASTER = os.path.join("data", "raw", "articles_master.csv")


def _standardize(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["title", "date", "source", "url", "full_text", "source_type", "raw_source"]:
        if col not in df.columns:
            df[col] = ""
    return df[["title", "date", "source", "url", "full_text", "source_type", "raw_source"]]


def _load_scrapy_outputs(patterns: List[str] = None) -> List[Dict]:
    patterns = patterns or ["data/raw/*archive*.json", "data/raw/*archive*.csv"]
    records: List[Dict] = []
    for pattern in patterns:
        for path in glob.glob(pattern):
            if path.endswith(".json"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        records.extend(json.load(f))
                except Exception:
                    continue
            elif path.endswith(".csv"):
                try:
                    df = pd.read_csv(path)
                    records.extend(df.to_dict(orient="records"))
                except Exception:
                    continue
    # tag source_type if missing
    for r in records:
        r.setdefault("source_type", "scrapy")
        r.setdefault("raw_source", os.path.basename(path))
    return records


def collect_all_articles(
    ce_terms: List[str],
    ai_terms: List[str],
    max_api_results: int = 400,
    num_google_pages: int = 3,
    site_page_limit: int = 3,
    include_legacy_html: bool = True,
) -> pd.DataFrame:
    query_terms = [f"{ce} {ai}" for ce in ce_terms for ai in ai_terms]
    records: List[Dict] = []

    # RSS
    records.extend(fetch_rss_articles())

    # APIs (with env toggles handled inside)
    records.extend(fetch_api_articles(query_terms, max_results=max_api_results, use_mediastack=False, use_bing=False))

    # Google News
    records.extend(search_google_news(ce_terms, ai_terms, num_pages=num_google_pages))

    # AEC site scrapers (shallow)
    for kw in query_terms:
        records.extend(aec_scrapers.scrape_enr(kw, page_limit=site_page_limit))
        records.extend(aec_scrapers.scrape_construction_dive(kw, page_limit=site_page_limit))
        records.extend(aec_scrapers.scrape_civil_structural(kw, page_limit=site_page_limit))
        records.extend(aec_scrapers.scrape_engineering_com(kw, page_limit=site_page_limit))
        records.extend(aec_scrapers.scrape_bimplus(kw, page_limit=site_page_limit))
        records.extend(aec_scrapers.scrape_new_civil_engineer(kw, page_limit=site_page_limit))

    # Legacy HTML + NewsAPI scraper (for compatibility)
    if include_legacy_html:
        records.extend(legacy_scrape(ce_terms, ai_terms, limit=200).to_dict(orient="records"))

    # Scrapy outputs (if spiders have been run)
    records.extend(_load_scrapy_outputs())

    df = pd.DataFrame(records)
    if df.empty:
        return df

    df = _standardize(df)
    df = df.drop_duplicates(subset="url").reset_index(drop=True)

    os.makedirs(os.path.dirname(RAW_MASTER), exist_ok=True)
    df.to_csv(RAW_MASTER, index=False)
    return df





