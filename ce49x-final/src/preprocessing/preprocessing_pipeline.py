"""
Preprocess scraped articles and save cleaned output.
"""

import os
import pandas as pd
from .clean_text import clean_text

RAW_PATH = os.path.join("data", "raw", "articles.csv")
PROC_PATH = os.path.join("data", "processed", "articles_clean.csv")


def preprocess_all_articles(path: str = RAW_PATH) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Raw data not found at {path}")

    df = pd.read_csv(path)
    if "full_text" not in df.columns:
        raise ValueError("Expected 'full_text' column in raw dataset.")

    df["clean_text"] = df["full_text"].fillna("").apply(lambda t: clean_text(str(t)))
    df["tokens"] = df["clean_text"].apply(lambda t: t.split())

    os.makedirs(os.path.dirname(PROC_PATH), exist_ok=True)
    df.to_csv(PROC_PATH, index=False)
    return df

