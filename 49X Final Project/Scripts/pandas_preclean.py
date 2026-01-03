import sqlite3
import pandas as pd
import os
import re

# --- CONFIGURATION ---
BASE_PATH = r"C:\Users\Hakan\Desktop\CE49X Final Project\Data"
SOURCE_DB = os.path.join(BASE_PATH, "corpus.db")
INTERMEDIATE_DB = os.path.join(BASE_PATH, "corpus_pandas_cleaned.db")

# Keywords for Superficial Filtering
CE_KEYWORDS = ['apartment', 'structural', 'geotechnical', 'soil', 'foundation', 'concrete', 'seismic', 'traffic', 'transportation', 'construction', 'sustainability', 'waste management']
AI_KEYWORDS = ['neural network', 'deep learning', 'machine learning', 'algorithm', 'computer vision', 'predictive', 'optimization', 'robotics', 'automation', 'generative', 'ai', 'ml']
NOISE_KEYWORDS = ['buy now', 'limited offer', 'subscribe', 'sponsored content', 'cookie', 'privacy settings']

def create_slug(text):
    """Removes all non-alphanumeric characters and lowercases for perfect sorting."""
    if not text: return ""
    # This turns "AI in Bridges!" into "aiinbridges"
    return re.sub(r'[^a-z0-9]', '', str(text).lower())

def pandas_superficial_cleanup():
    if not os.path.exists(SOURCE_DB):
        print("Source file not found.")
        return

    conn = sqlite3.connect(SOURCE_DB)
    df = pd.read_sql_query("SELECT * FROM articles", conn)
    conn.close()

    print(f"Original Count: {len(df)}")

    # 1. HARD CLEAN: Remove rows with empty critical fields
    df = df.dropna(subset=['title', 'url', 'full_text'])
    df = df[df['full_text'].str.strip() != ""]

    # 2. EXACT DEDUPLICATION: URL and Title
    df = df.drop_duplicates(subset=['url'], keep='first')
    df = df.drop_duplicates(subset=['title'], keep='first')

    # 3. NOISE/RELEVANCE SCORING
    def calculate_relevance(text):
        text = str(text).lower()
        score = sum(1 for word in CE_KEYWORDS + AI_KEYWORDS if word in text)
        noise_score = sum(1 for word in NOISE_KEYWORDS if word in text)
        if len(text) < 500 or (noise_score > 2 and score < 1):
            return False
        return score >= 1

    df['is_likely_relevant'] = df['full_text'].apply(calculate_relevance)
    cleaned_df = df[df['is_likely_relevant'] == True].copy()
    cleaned_df.drop(columns=['is_likely_relevant'], inplace=True)

    # --- NEW: SLUG CREATION & SORTING ---
    print("Creating slugs and sorting for LLM batching...")
    # This creates a hidden 'grouping' key
    cleaned_df['title_slug'] = cleaned_df['title'].apply(create_slug)
    
    # Sort by the slug so semantic duplicates sit next to each other
    cleaned_df = cleaned_df.sort_values(by='title_slug').reset_index(drop=True)
    # ------------------------------------

    print(f"Pandas Cleaned Count: {len(cleaned_df)} (Removed {len(df) - len(cleaned_df)} rows)")

    # Save to intermediate database
    conn_dest = sqlite3.connect(INTERMEDIATE_DB)
    # We keep 'title_slug' in the DB so the next script can maintain the order easily
    cleaned_df.to_sql('articles', conn_dest, if_exists='replace', index=False)
    conn_dest.close()
    print(f"Intermediate file saved: {INTERMEDIATE_DB}")

if __name__ == "__main__":
    pandas_superficial_cleanup()