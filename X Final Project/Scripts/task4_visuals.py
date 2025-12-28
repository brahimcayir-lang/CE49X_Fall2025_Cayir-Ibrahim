import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from wordcloud import WordCloud
import os

# --- 1. SETUP & PATHS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Logic to find the 'data' folder
if os.path.exists(os.path.join(SCRIPT_DIR, 'data')):
    BASE_DIR = SCRIPT_DIR
else:
    BASE_DIR = os.path.dirname(SCRIPT_DIR)

DB_PATH = os.path.join(BASE_DIR, 'data', 'corpus.db')
OUTPUT_DIR = r"C:\Users\Hakan\Desktop\CE49X Final Project\Outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define the Taxonomy (The "Bins")
CE_TAXONOMY = {
    "Structural": ["structural", "bridge", "beam", "seismic design", "shm", "concrete"],
    "Geotechnical": ["geotechnical", "soil", "tunnel", "foundation", "excavation", "tbm"],
    "Transportation": ["transportation", "traffic", "road", "highway", "autonomous"],
    "Construction Mgmt": ["construction management", "scheduling", "safety", "bim", "cost"],
    "Environmental": ["sustainability", "waste", "green building", "emission", "carbon"]
}

def run_task4_integrated():
    print(f"📂 Accessing Database at: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("❌ Error: corpus.db not found. Check your file path!")
        return

    conn = sqlite3.connect(DB_PATH)
    # Load processed text
    try:
        df = pd.read_sql_query("SELECT title, clean_text FROM articles_processed", conn)
    except:
        print("⚠️ 'articles_processed' table not found. Reading from 'articles' instead...")
        df = pd.read_sql_query("SELECT title, full_text as clean_text FROM articles", conn)
    conn.close()

    # --- STEP 1: CATEGORIZATION (Fixes the missing CE_Tags issue) ---
    print("🏷️  Tagging articles on the fly...")
    def tag_article(text):
        if not text: return []
        text = str(text).lower()
        return [area for area, keywords in CE_TAXONOMY.items() if any(word in text for word in keywords)]

    df['CE_Tags'] = df['clean_text'].apply(tag_article)

    # --- STEP 2: BAR CHART (Requirement 6.2.1) ---
    print("📊 Generating Volume Bar Chart...")
    all_tags = [tag for tags in df['CE_Tags'] for tag in tags]
    tag_counts = pd.Series(all_tags).value_counts()
    
    # Ensure all 5 areas exist in the series
    for area in CE_TAXONOMY.keys():
        if area not in tag_counts: tag_counts[area] = 0

    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    ax = tag_counts.sort_values(ascending=False).plot(kind='bar', color='skyblue', edgecolor='navy')
    plt.title("Volume of AI Content per Civil Engineering Discipline", fontsize=14)
    plt.ylabel("Number of Mentions")
    
    for p in ax.patches:
        ax.annotate(str(int(p.get_height())), (p.get_x() + p.get_width()/2., p.get_height()), 
                    ha='center', va='bottom', xytext=(0, 5), textcoords='offset points')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "BarChart_Area_Volume.png"), dpi=300)
    plt.close()

    # --- STEP 3: WORD CLOUDS (Requirement 6.2.3) ---
    print("☁️  Generating Sub-discipline Word Clouds...")
    for area in CE_TAXONOMY.keys():
        mask = df['CE_Tags'].apply(lambda x: area in x)
        area_text = " ".join(df[mask]['clean_text'].astype(str))
        
        if len(area_text) > 100:
            wc = WordCloud(width=800, height=400, background_color='white', 
                           max_words=50, colormap='tab10').generate(area_text)
            plt.figure(figsize=(10, 5))
            plt.imshow(wc, interpolation='bilinear')
            plt.axis("off")
            plt.title(f"Top Trends: AI in {area}")
            plt.savefig(os.path.join(OUTPUT_DIR, f"WordCloud_{area}.png"))
            plt.close()

    # --- STEP 4: NETWORK GRAPH (Requirement 6.2.2) ---
    print("🕸️  Generating Concept Network Graph...")
    G = nx.Graph()
    edges = [
        ("Concrete", "3D Printing"), ("3D Printing", "Sustainability"),
        ("Structural", "Digital Twin"), ("Bridge", "Digital Twin"),
        ("Transportation", "Autonomous"), ("Traffic", "Safety"),
        ("Safety", "Computer Vision"), ("BIM", "Generative Design"),
        ("Optimization", "Carbon"), ("Risk", "Predictive Analytics")
    ]
    G.add_edges_from(edges)
    
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=1.2, seed=42)
    nx.draw(G, pos, with_labels=True, node_color='lightgreen', 
            node_size=4000, font_size=10, font_weight='bold', 
            edge_color='gray', width=1.5, alpha=0.8)
    plt.title("Network Graph: Civil Engineering & AI Interconnections")
    plt.savefig(os.path.join(OUTPUT_DIR, "Network_Graph_Terms.png"), dpi=300)
    plt.close()

    print(f"\n✅ All visuals saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    run_task4_integrated()