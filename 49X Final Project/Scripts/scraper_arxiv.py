import feedparser
import sqlite3
import urllib.parse
import os

# --- CONFIGURATION ---
# We use 'os' to find the database path automatically
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'corpus.db')

# API QUERY EXPLANATION:
# cat:cs.AI   -> Category: Computer Science / Artificial Intelligence
# AND         -> Logic operator
# all:construction -> Looks for "construction" in title or abstract
method_terms = [
    '"finite element"', '"topology optimization"', '"structural health monitoring"',
    '"crack detection"', '"damage detection"', '"predictive maintenance"',
    '"digital twin"', "BIM", '"computer vision"', '"reinforcement learning"',
    '"deep learning"', '"neural network"'
]

application_terms = [
    "bridge", "pavement", "tunnel", "geotechnical", "soil", "retaining wall",
    "highway", "railway", "airport", "building", "foundation", "slope",
    "structural", "load-bearing"
]

# Build a balanced OR-list that searches in title OR abstract (ti: OR abs:)
method_query = " OR ".join(f'(ti:{t} OR abs:{t})' for t in method_terms)
app_query = " OR ".join(f'(ti:{t} OR abs:{t})' for t in application_terms)

# Limit to categories likely to contain applied AI work
categories = "(cat:cs.AI OR cat:cs.CV OR cat:cs.LG)"

# Final query
SEARCH_QUERY = f'{categories} AND ({method_query} OR {app_query})'

def save_to_db(entry):
    """Saves a single API result to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # arXiv uses the ID link as a unique identifier
        url = entry.id
        title = entry.title.replace('\n', ' ')
        date = entry.published[:10]  # Format: YYYY-MM-DD
        abstract = entry.summary.replace('\n', ' ')
        
        # Insert into database
        # We assume 'Scientific' category for these
        cursor.execute("""
            INSERT OR IGNORE INTO articles 
            (title, publication_date, source_domain, url, full_text, category_tag)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            title,
            date,
            "arxiv.org",
            url,
            abstract, # The abstract serves as the "full text"
            "Scientific"
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving {entry.id}: {e}")
        return False

def run_arxiv_fetcher():
    print("🔬 Contacting arXiv API...")
    
    # URL Encode the query so it travels safely over the internet
    encoded_query = urllib.parse.quote(SEARCH_QUERY)
    
    # We ask for 200 results. 
    # API Rule: strict limit is usually higher, but 200 is safe.
    api_url = f'http://export.arxiv.org/api/query?search_query={encoded_query}&start=0&max_results=200'
    
    # Fetch data
    feed = feedparser.parse(api_url)
    
    print(f"   Received {len(feed.entries)} entries from arXiv.")
    
    new_count = 0
    for entry in feed.entries:
        if save_to_db(entry):
            new_count += 1
            print(f"   ✅ Saved: {entry.title[:50]}...")
            
    print(f"\n🎉 arXiv Module Complete. Added {new_count} scientific papers.")

if __name__ == "__main__":
    run_arxiv_fetcher()