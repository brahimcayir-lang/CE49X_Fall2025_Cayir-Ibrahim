import sqlite3
import time
import os
import pandas as pd
from GoogleNews import GoogleNews
from newspaper import Article, Config
from datetime import datetime

# --- CONFIGURATION ---
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'corpus.db')

# Project Requirements: Combinations of CE terms and AI terms
# We create search queries by mixing these lists
SEARCH_QUERIES = [
    "Artificial Intelligence Construction",
    "Artificial Intelligence Civil Engineering",
    "Artificial Intelligence Structural Engineering",
    "Machine Learning Civil Engineering",
    "Machine Learning Structural Engineering",
    "Artificial Intelligence AR Construction Industry",
    "Artificial Intelligence VR Construction Industry",
    "Generative AI Construction Industry",
    "Computer Vision Infrastructure",
    "Generative AI Structural Engineering",
    "Robotics Construction Site",
    "Automation Geotechnical Engineering",
    "AI Concrete Strength",
    "Smart City Transportation AI",
    "Predictive Maintenance Bridge"
    "Predictive Maintenance Commercial",
    # --- CORE GENERAL TERMS ---
    "Artificial Intelligence Construction Industry",
    "Machine Learning Civil Engineering",
    "Deep Learning Structural Health Monitoring",
    
    # --- CONSTRUCTION MANAGEMENT & COST (Relevant to your Internship) ---
    "AI Construction Cost Estimation",
    "Natural Language Processing Construction Contracts",
    "Machine Learning Construction Scheduling",
    "AI Tender Risk Analysis Construction",
    "Predictive Analytics Construction Supply Chain",
    "NLP Automated Compliance Checking Construction",

    # --- SITE SAFETY & COMPUTER VISION ---
    "Computer Vision PPE Detection Construction",
    "AI Construction Site Safety Monitoring",
    "Computer Vision Pavement Distress Detection",
    "Drone Data Analysis AI Construction",
    "Autonomous Cranes Construction Site",
    "AI Accident Prediction Construction",

    # --- BIM & DIGITAL TWINS ---
    "AI Scan to BIM Automation",
    "Digital Twin Construction Management",
    "Generative Design BIM Integration",
    "IoT Digital Twin Civil Infrastructure",
    "AI 4D Construction Simulation",

    # --- STRUCTURAL & MATERIALS ---
    "Machine Learning Concrete Mix Design",
    "AI Self-Healing Concrete",
    "Generative AI Structural Topology Optimization",
    "Deep Learning Crack Detection Bridges",
    "Robotics 3D Printing Construction",

    # --- TRANSPORTATION & GEOTECHNICAL (Your Interest Area) ---
    "AI Traffic Flow Optimization",
    "Machine Learning Geometric Road Design",
    "AI Pavement Management Systems",
    "Machine Learning Soil Stabilization",
    "AI Tunnel Boring Machine Optimization",
    "Smart Highways AI Infrastructure",

    # --- SUSTAINABILITY & ENERGY ---
    "AI Energy Efficient Building Design",
    "Machine Learning Carbon Footprint Construction",
    "AI HVAC Optimization Commercial Buildings",
    "Net Zero Construction AI",

    # --- DIGITAL TWINS & IOT (New Focus) ---
    "Digital Twin Construction Site AI",
    "AI Digital Twin Infrastructure Monitoring",
    "Digital Twin Smart City Integration",
    "IoT Digital Twin Predictive Maintenance",
    "Real-time Digital Twin Construction Progress",
    "Digital Twin Bridge Structural Health",
    "AI Airport Digital Twin Operations",  # Relevant to your Istanbul Airport project
    "Digital Twin Energy Optimization AI",

    # --- BIM & AUTOMATION (New Focus) ---
    "AI Scan to BIM Automation",
    "Machine Learning BIM Clash Detection",
    "Generative Design BIM Integration",
    "AI Automated BIM Compliance Checking",
    "BIM 5D Cost Estimation AI",
    "Machine Learning COBie Data",
    "AI Revit Plugin Automation",
    "Natural Language Processing BIM Models",

    # --- CORE CONSTRUCTION AI ---
    "Artificial Intelligence Construction Industry",
    "Machine Learning Civil Engineering",
    "Robotics Construction Site Automation",
    "Computer Vision Construction Safety",
    "AI Construction Risk Management",
    
    # --- STRUCTURAL & GEOTECHNICAL ---
    "Generative AI Structural Topology Optimization",
    "Machine Learning Concrete Strength Prediction",
    "AI Geotechnical Soil Analysis",
    "Computer Vision Pavement Distress",
    "Deep Learning Structural Health Monitoring",

    # --- TRANSPORTATION & INFRASTRUCTURE ---
    "AI Traffic Flow Optimization",
    "Machine Learning Road Design",
    "Smart Highway Infrastructure AI",
    "Predictive Maintenance Railway Infrastructure",

    # --- GENERAL STUFF ---
    "Predictive Maintenance Infrastructure",
    "AI Infrastructure Safety",
    "AI Construction Safety",
    "Construction Site Safety AI",
    "Construction Site Monitoring AI",
    "Health and Safety Construction AI",
    "AI Construction Monitoring",  
    "AI Predictive Maintenance",
    
    # --- DIGITAL TWINS & IOT (New Focus) ---
    "Digital Twin Construction Site AI",
    "AI Digital Twin Infrastructure Monitoring",
    "Digital Twin Smart City Integration",
    "IoT Digital Twin Predictive Maintenance",
    "Real-time Digital Twin Construction Progress",
    "Digital Twin Bridge Structural Health",
    "AI Airport Digital Twin Operations",  # Relevant to your Istanbul Airport project
    "Digital Twin Energy Optimization AI",

    # --- BIM & AUTOMATION (New Focus) ---
    "AI Scan to BIM Automation",
    "Machine Learning BIM Clash Detection",
    "Generative Design BIM Integration",
    "AI Automated BIM Compliance Checking",
    "BIM 5D Cost Estimation AI",
    "Machine Learning COBie Data",
    "AI Revit Plugin Automation",
    "Natural Language Processing BIM Models",

    # --- CORE CONSTRUCTION AI ---
    "Artificial Intelligence Construction Industry",
    "Machine Learning Civil Engineering",
    "Robotics Construction Site Automation",
    "Computer Vision Construction Safety",
    "AI Construction Risk Management",
    
    # --- STRUCTURAL & GEOTECHNICAL ---
    "Generative AI Structural Topology Optimization",
    "Machine Learning Concrete Strength Prediction",
    "AI Geotechnical Soil Analysis",
    "Computer Vision Pavement Distress",
    "Deep Learning Structural Health Monitoring",

    # --- TRANSPORTATION & INFRASTRUCTURE ---
    "AI Traffic Flow Optimization",
    "Machine Learning Road Design",
    "Smart Highway Infrastructure AI",
    "Predictive Maintenance Railway Infrastructure"
    
]

unique_querries = []
for i in SEARCH_QUERIES:
    if i not in unique_querries :
        unique_querries .append(i)

SEARCH_QUERIES = unique_querries


def get_existing_urls():
    """Returns a set of URLs already in the database to avoid duplicates."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT url FROM articles")
        urls = set(row[0] for row in cursor.fetchall())
        conn.close()
        return urls
    except Exception:
        return set()


# --- UPDATE YOUR SAVE_ARTICLE FUNCTION ---
def save_article(article_data):
    
    # !!! ADD THIS CHECK !!!
    if not validate_relevance(article_data['text']):
        print(f"      ❌ Skipped (Irrelevant Content): {article_data['title'][:30]}...")
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO articles 
            (title, publication_date, source_domain, url, full_text, search_keywords, category_tag)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            article_data['title'],
            str(article_data['publish_date']),
            article_data['source_domain'],
            article_data['url'],
            article_data['text'],
            article_data['query'],
            "Aggregated_News"
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Database Error: {e}")
        return False


def download_and_parse(url, query_used):
    """Uses newspaper3k to extract text from a URL."""
    # User-Agent is vital to not look like a bot
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    config.request_timeout = 10

    try:
        article = Article(url, config=config)
        article.download()
        article.parse()

        # Validation: Ignore very short articles (likely errors or paywalls)
        if len(article.text) < 200:
            return None

        return {
            'title': article.title,
            'publish_date': article.publish_date if article.publish_date else datetime.now().strftime('%Y-%m-%d'),
            'source_domain': article.source_url,
            'url': url,
            'text': article.text,
            'query': query_used
        }
    except Exception as e:
        # Many sites will block us. This is normal. Just skip them.
        return None

# --- ADD THIS NEW FUNCTION ---
def validate_relevance(text):
    """
    Returns True ONLY if the text contains at least one word from 
    both the Civil Engineering list and the AI list.
    """
    if not text: return False
    
    # Convert text to lowercase for case-insensitive matching
    content_blob = text.lower()
    
    # 1. Define your validation terms (simplified lists)
    ce_keywords = [
        "construction", "structural", "geotechnical", "transportation", 
        "infrastructure", "civil engineer"
    ]
    
    ai_keywords = [
        "artificial intelligence", "machine learning", "computer vision", 
        "generative ai", "neural network", "robotics", "automation", 
        "predictive", "deep learning", "digital twin"
    ]
    
    # 2. Check for intersection
    has_ce = any(term in content_blob for term in ce_keywords)
    has_ai = any(term in content_blob for term in ai_keywords)
    
    # 3. Pass only if BOTH are present
    return has_ce and has_ai

def run_aggregator():
    existing_urls = get_existing_urls()
    print(f"📚 Starting with {len(existing_urls)} articles in database.")

    googlenews = GoogleNews(lang='en', region='US')

    total_saved = 0

    for query in SEARCH_QUERIES:
        print(f"\n🔍 Searching Google News for: '{query}'...")

        # Get search results (Page 1)
        googlenews.clear()
        googlenews.search(query)
        results = googlenews.results()

        # Optional: Get Page 2 and 3 for more volume
        # googlenews.get_page(2)
        # results.extend(googlenews.results())

        print(f"   Found {len(results)} links. Processing...")

        for item in results:
            url = item.get('link')

            # Skip if we already have it
            if url in existing_urls:
                continue

            # Attempt to download
            # We add a tiny sleep to be polite to servers
            time.sleep(1)
            print(f"   Downloading: {item.get('title')[:30]}...", end="\r")

            article_data = download_and_parse(url, query)

            if article_data:
                saved = save_article(article_data)
                if saved:
                    total_saved += 1
                    existing_urls.add(url)
                    print(f"   ✅ Saved: {article_data['title'][:40]}...")

    print(f"\n🎉 Session Complete. Added {total_saved} new articles.")


if __name__ == "__main__":
    run_aggregator()