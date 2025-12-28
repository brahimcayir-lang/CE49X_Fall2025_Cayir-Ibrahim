import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from wordcloud import WordCloud
import os
from collections import Counter

# --- 1. CONFIGURATION ---
BASE_PATH = r"C:\Users\Hakan\Desktop\CE49X Final Project\Data"
DB_PATH = os.path.join(BASE_PATH, 'corpus_LLM_Improved.db')

# Output Directory for Deliverables
OUTPUT_DIR = r"C:\Users\Hakan\Desktop\CE49X Final Project\Outputs\AfterLLM"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_task4_synthesis():
    print(f"⚙️ Loading and merging data from {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        # We need the labels (CE_topic) and the processed text for word clouds
        df_labels = pd.read_sql_query("SELECT * FROM articles_labeled", conn)
        df_text = pd.read_sql_query("SELECT id, clean_text FROM articles_labeled_clean", conn)
        conn.close()
        
        # Merge on ID
        df = pd.merge(df_labels, df_text, on='id')
    except Exception as e:
        print(f"❌ Error merging data: {e}")
        return

    # Normalize column names for safety
    df.columns = [c.lower() for c in df.columns]
    ce_col = 'ce_topic'
    ai_col = 'ai_topic'

    # --- 2. BAR CHART: ARTICLES PER CE AREA ---
    print("📊 Generating Category Bar Charts...")
    plt.figure(figsize=(10, 6))
    order = df[ce_col].value_counts().index
    sns.countplot(data=df, y=ce_col, order=order, palette='viridis')
    plt.title('Volume of AI Research by Civil Engineering Area', fontsize=14)
    plt.xlabel('Number of Articles')
    plt.ylabel('CE Discipline')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "BarChart_CE_Distribution.png"), dpi=300)
    plt.close()

    # --- 3. WORD CLOUDS PER SUB-DISCIPLINE ---
    print("☁️ Generating Word Clouds for each CE Area...")
    disciplines = df[ce_col].unique()
    
    for disc in disciplines:
        text = " ".join(df[df[ce_col] == disc]['clean_text'].astype(str))
        if len(text) < 10: continue # Skip if no text
        
        wc = WordCloud(width=800, height=400, background_color='white', 
                       colormap='tab10', max_words=100).generate(text)
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wc, interpolation='bilinear')
        plt.title(f'Word Cloud: AI in {disc}', fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        safe_name = disc.replace("/", "_").replace(" ", "_")
        plt.savefig(os.path.join(OUTPUT_DIR, f"WordCloud_{safe_name}.png"))
        plt.close()

    # --- 4. NETWORK GRAPH: TERM RELATIONSHIPS ---
    print("🕸️ Building Semantic Network Graph...")
    G = nx.Graph()
    
    # We will link CE Topics to their most frequent 5 keywords
    for disc in disciplines:
        # skip missing values (None/empty strings/NaN)
        if disc is None or (isinstance(disc, str) and disc.strip() == ""):
            print("Skipping empty node:", repr(disc))
            continue

        # optional: coerce other types to string
        disc_key = str(disc)

        G.add_node(disc_key, color='orange', size=2000)
        # Get top words for this discipline
        words = " ".join(df[df[ce_col] == disc]['clean_text'].astype(str)).split()
        top_words = [word for word, count in Counter(words).most_common(6) if len(word) > 3]
        
        for word in top_words:
            G.add_node(word, color='skyblue', size=1000)
            G.add_edge(disc, word)

    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    # Draw nodes
    nodes = G.nodes(data=True)
    colors = [data['color'] for n, data in nodes]
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=[data['size'] for n, data in nodes], alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.3)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

    plt.title("Network Graph: CE Areas and Associated AI Keywords", fontsize=15)
    plt.axis('off')
    plt.savefig(os.path.join(OUTPUT_DIR, "NetworkGraph_Terms.png"), dpi=300)
    plt.close()

    # --- 5. FINAL CONCLUSION: AI MATURITY RANKING ---
    print("📜 Synthesizing AI Maturity Ranking...")
    ranking = df[ce_col].value_counts().reset_index()
    ranking.columns = ['CE Discipline', 'Article Count']
    ranking['Percentage'] = (ranking['Article Count'] / len(df) * 100).round(2)
    
    # Maturity Logic: High count + Diversity of AI Tech
    diversity = df.groupby(ce_col)[ai_col].nunique().sort_values(ascending=False)
    
    with open(os.path.join(OUTPUT_DIR, "Final_Conclusion_Insights.txt"), "w") as f:
        f.write("=== FINAL PROJECT CONCLUSION: AI MATURITY IN CIVIL ENGINEERING ===\n\n")
        f.write("AI INTEREST RANKING (Based on Article Volume):\n")
        f.write(ranking.to_string(index=False) + "\n\n")
        
        f.write("AI MATURITY INSIGHTS:\n")
        f.write(f"1. Most Mature Discipline: {ranking.iloc[0]['CE Discipline']} (Highest research volume).\n")
        f.write(f"2. Most Tech-Diverse Discipline: {diversity.index[0]} (Uses the widest variety of AI tools).\n\n")
        f.write("INTERPRETATION:\n")
        f.write(f"The data suggests that {ranking.iloc[0]['CE Discipline']} is the leading area for AI integration, ")
        f.write("likely due to the abundance of image/sensor data available for Computer Vision and Predictive Analytics.")

    print(f"\n✅ Task 4 Complete!")
    print(f"📂 Visuals saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    run_task4_synthesis()