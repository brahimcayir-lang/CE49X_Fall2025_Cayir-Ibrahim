import sqlite3
import pandas as pd
import os

try:
    import plotly.graph_objects as go
except ImportError:
    print("❌ Error: plotly is not installed.")
    print("   Please install it using: pip install plotly")
    print("   For PNG export, also install: pip install kaleido")
    exit(1)

# --- 1. SETUP & PATHS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Logic to find the base directory (same pattern as task4_visuals.py)
if os.path.exists(os.path.join(SCRIPT_DIR, 'data')):
    BASE_DIR = SCRIPT_DIR
else:
    BASE_DIR = os.path.dirname(SCRIPT_DIR)

# Try multiple possible database paths
DB_PATHS = [
    os.path.join(BASE_DIR, 'Data', 'corpus_LLM_Improved.db'),
    os.path.join(BASE_DIR, 'data', 'corpus_LLM_Improved.db'),
    os.path.join(BASE_DIR, 'Data', 'corpus_LLM.db'),
]

# Output Directory
OUTPUT_DIR = os.path.join(BASE_DIR, 'Outputs', 'Extra_Visualizations')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def find_database():
    """Find the database file."""
    for db_path in DB_PATHS:
        if os.path.exists(db_path):
            return db_path
    return None

def create_sankey_diagram():
    """Create a Sankey diagram showing flow from CE disciplines to AI technologies."""
    print(f"📂 Searching for database...")
    
    DB_PATH = find_database()
    if not DB_PATH:
        print(f"❌ Error: Database not found. Checked paths: {DB_PATHS}")
        return
    
    print(f"✅ Found database at: {DB_PATH}")
    
    # Connect to database
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM articles_labeled", conn)
        conn.close()
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        return
    
    # Normalize column names
    df.columns = [c.lower() for c in df.columns]
    
    # Find the correct columns
    ce_col = next((c for c in df.columns if 'ce' in c and 'topic' in c), None)
    ai_col = next((c for c in df.columns if 'ai' in c and 'topic' in c), None)
    
    if not ce_col or not ai_col:
        print(f"❌ ERROR: Could not find topic columns. Available columns: {list(df.columns)}")
        return
    
    print(f"✅ Found CE column: '{ce_col}' and AI column: '{ai_col}'")
    
    # Fill empty values
    df[ce_col] = df[ce_col].fillna('Uncategorized')
    df[ai_col] = df[ai_col].fillna('Uncategorized')
    
    # Filter out uncategorized entries for cleaner visualization
    df_filtered = df[(df[ce_col] != 'Uncategorized') & (df[ai_col] != 'Uncategorized')].copy()
    
    if df_filtered.empty:
        print("⚠️ No valid CE-AI pairs found after filtering.")
        df_filtered = df.copy()
    
    # Calculate flow counts (co-occurrence)
    flow_data = df_filtered.groupby([ce_col, ai_col]).size().reset_index(name='count')
    
    # Create unique lists of source (CE) and target (AI) nodes
    ce_nodes = sorted(df_filtered[ce_col].unique().tolist())
    ai_nodes = sorted(df_filtered[ai_col].unique().tolist())
    
    # Combine all nodes (sources first, then targets)
    all_nodes = ce_nodes + ai_nodes
    
    # Create node indices
    node_indices = {node: idx for idx, node in enumerate(all_nodes)}
    
    # Prepare source, target, and value lists for Sankey diagram
    source_indices = []
    target_indices = []
    values = []
    labels = all_nodes.copy()
    
    # Map CE nodes to AI nodes with their counts
    for _, row in flow_data.iterrows():
        ce_topic = row[ce_col]
        ai_topic = row[ai_col]
        count = row['count']
        
        source_idx = node_indices[ce_topic]
        target_idx = node_indices[ai_topic]
        
        source_indices.append(source_idx)
        target_indices.append(target_idx)
        values.append(count)
    
    # Create color palette
    num_ce_nodes = len(ce_nodes)
    num_ai_nodes = len(ai_nodes)
    
    # Colors for CE nodes (blue tones)
    ce_colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c']
    # Colors for AI nodes (green/red tones)
    ai_colors = ['#2ca02c', '#98df8a', '#d62728', '#ff9896', '#9467bd']
    
    # Extend colors if needed
    while len(ce_colors) < num_ce_nodes:
        ce_colors.extend(ce_colors)
    while len(ai_colors) < num_ai_nodes:
        ai_colors.extend(ai_colors)
    
    node_colors = ce_colors[:num_ce_nodes] + ai_colors[:num_ai_nodes]
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color='rgba(128, 128, 128, 0.4)'  # Semi-transparent gray for links
        )
    )])
    
    fig.update_layout(
        title_text="Sankey Diagram: Flow from Civil Engineering Disciplines to AI Technologies",
        font_size=12,
        height=800,
        width=1400
    )
    
    # Save as HTML (interactive)
    output_html = os.path.join(OUTPUT_DIR, "Sankey_Diagram_CE_to_AI.html")
    fig.write_html(output_html)
    print(f"✅ Interactive Sankey diagram saved to: {output_html}")
    
    # Save as static PNG (requires kaleido)
    try:
        output_png = os.path.join(OUTPUT_DIR, "Sankey_Diagram_CE_to_AI.png")
        fig.write_image(output_png, width=1400, height=800, scale=2)
        print(f"✅ Static Sankey diagram saved to: {output_png}")
    except Exception as e:
        print(f"⚠️ Could not save PNG (kaleido not installed): {e}")
        print("   HTML version saved successfully. To save PNG, install: pip install kaleido")
    
    print(f"\n📊 Flow Statistics:")
    print(f"   Total flows: {len(flow_data)}")
    print(f"   CE Disciplines: {len(ce_nodes)}")
    print(f"   AI Technologies: {len(ai_nodes)}")
    print(f"\n✅ Sankey diagram complete! Results saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    create_sankey_diagram()

