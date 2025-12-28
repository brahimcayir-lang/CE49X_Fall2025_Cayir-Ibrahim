import sqlite3
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# --- 1. CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'corpus.db')
OUTPUT_DIR = r"C:\Users\Hakan\Desktop\CE49X Final Project\Outputs"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
REPORT_FILE = os.path.join(OUTPUT_DIR, "Task3_Categorization_Report.txt")
HEATMAP_FILE = os.path.join(OUTPUT_DIR, "Task3_Heatmap.png")

# --- 2. DICTIONARY DEFINITIONS (Per PDF 5.2.1) ---
CE_KEYWORDS = {
    "Structural": [
        # Core Elements
        "structural", "bridge", "beam", "column", "slab", "truss", "girder",
        "steel structure", "reinforced concrete", "masonry", "timber",
        # Analysis & Behavior (The "Seismic" Boundary)
        "seismic design", "seismic analysis", "vibration", "damping", "retrofit",
        "structural health monitoring", "shm", "load testing", "fatigue", 
        "finite element", "stress analysis", "collapse", "deformation"
    ],
    "Geotechnical": [
        # Soil & Ground
        "geotechnical", "soil mechanics", "rock mechanics", "foundation", "piling",
        "excavation", "tunneling", "tbm", "underground", "slope stability",
        "retaining wall", "embankment", "subsurface", "borehole",
        # Earthquake Engineering (The Ground aspect)
        "liquefaction", "ground motion", "seismology", "earthquake engineering",
        "landslide", "settlement", "bearing capacity"
    ],
    "Transportation": [
        # Road & Highway
        "transportation", "traffic engineering", "highway", "pavement", "asphalt",
        "roadway", "intersection", "signaling", "congestion",
        # Transit & Systems
        "railway", "transit", "public transport", "autonomous vehicle", 
        "connected vehicle", "logistics", "fleet management", "supply chain",
        "airport", "aviation", "port", "multimodal"
    ],
    "Construction Mgmt": [
        # Planning & Cost
        "construction management", "project management", "scheduling", "cost estimation",
        "budgeting", "bidding", "procurement", "contract", "change order",
        # Site & Safety
        "site monitoring", "jobsite", "safety", "osha", "ppe", "accident prevention",
        "risk management", "quality control", "inspection",
        # Digital Tools (Specific to Mgmt)
        "building information modeling", "bim", "digital twin", "lean construction"
    ],
    "Environmental": [
        # Sustainability
        "environmental engineering", "sustainability", "green building", "leed",
        "carbon footprint", "emission", "energy efficiency", "net zero",
        # Water & Waste
        "wastewater", "hydrology", "water resources", "stormwater", "pollution",
        "waste management", "recycling", "circular economy", "climate change",
        "resilience"
    ]
}

AI_KEYWORDS = {
    "Computer Vision": [
        "computer vision", "image recognition", "drone", "camera", "video analysis", 
        "object detection", "inspection"
    ],
    "Predictive Analytics": [
        "predictive", "prediction", "forecasting", "risk assessment", "data analytics",
        "regression", "prognosis"
    ],
    "Generative Design": [
        "generative design", "optimization", "parametric", "topology", "genetic algorithm"
    ],
    "Robotics & Automation": [
        "robot", "automation", "autonomous", "machinery", "3d printing", "unmanned"
    ],
    "Machine Learning (General)": [
        "machine learning", "neural network", "deep learning", "ai algorithm", "training data"
    ]
}

# --- 3. CLASSIFICATION LOGIC ---
def classify_article(text, taxonomy_dict):
    """Returns a list of categories found in the text."""
    found_categories = []
    if not text: return []
    
    # Simple check: if any keyword in a category exists in the text
    for category, keywords in taxonomy_dict.items():
        for word in keywords:
            if f" {word} " in f" {text} ": # Check for whole words
                found_categories.append(category)
                break # Move to next category if one match found
    return found_categories

# --- 4. MAIN EXECUTION ---
def run_task3_analysis():
    print("⚙️ Loading processed data...")
    try:
        conn = sqlite3.connect(DB_PATH)
        # Load the CLEANED text from Task 2
        df = pd.read_sql_query("SELECT id, title, clean_text FROM articles_processed", conn)
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    if df.empty:
        print("⚠️ Database is empty! Run Task 2 first.")
        return

    print(f"📚 Categorizing {len(df)} articles...")

    # A. Apply Classification
    # This creates columns containing lists of tags, e.g., ['Structural', 'Geotechnical']
    df['CE_Tags'] = df['clean_text'].apply(lambda x: classify_article(x, CE_KEYWORDS))
    df['AI_Tags'] = df['clean_text'].apply(lambda x: classify_article(x, AI_KEYWORDS))

    # B. Generate Statistics
    # Flatten lists to count occurrences
    all_ce_tags = [tag for tags in df['CE_Tags'] for tag in tags]
    all_ai_tags = [tag for tags in df['AI_Tags'] for tag in tags]
    
    ce_counts = pd.Series(all_ce_tags).value_counts()
    ai_counts = pd.Series(all_ai_tags).value_counts()

    # C. Generate Co-occurrence Matrix (The Heatmap Data)
    print("🧮 Calculating Co-occurrence Matrix...")
    
    # Initialize empty matrix
    matrix = pd.DataFrame(0, index=CE_KEYWORDS.keys(), columns=AI_KEYWORDS.keys())
    
    # Iterate rows and fill matrix
    for _, row in df.iterrows():
        for ce_cat in row['CE_Tags']:
            for ai_cat in row['AI_Tags']:
                matrix.loc[ce_cat, ai_cat] += 1

    # --- 5. REPORTING & VISUALIZATION ---
    print(f"📝 Saving Report to: {REPORT_FILE}")
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("="*50 + "\n")
        f.write(f"CE49X TASK 3 REPORT - CATEGORIZATION\n")
        f.write("="*50 + "\n\n")
        
        f.write("1. CIVIL ENGINEERING AREA DISTRIBUTION\n")
        f.write("-" * 40 + "\n")
        f.write(ce_counts.to_string() + "\n\n")
        
        f.write("2. AI TECHNOLOGY DISTRIBUTION\n")
        f.write("-" * 40 + "\n")
        f.write(ai_counts.to_string() + "\n\n")
        
        f.write("3. CO-OCCURRENCE MATRIX (Raw Counts)\n")
        f.write("-" * 40 + "\n")
        f.write(matrix.to_string() + "\n")

    # --- GENERATE HEATMAP PLOT ---
    print(f"🎨 Generating Heatmap to: {HEATMAP_FILE}")
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", linewidths=.5)
    plt.title("Heatmap: AI Adoption Across Civil Engineering Disciplines")
    plt.ylabel("Civil Engineering Area")
    plt.xlabel("AI Technology")
    
    # Fix for tight layout cutting off labels
    plt.tight_layout()
    plt.savefig(HEATMAP_FILE, dpi=300)
    plt.close()

    print("\n✅ Task 3 Complete.")
    print(f"   - Report: {os.path.basename(REPORT_FILE)}")
    print(f"   - Plot:   {os.path.basename(HEATMAP_FILE)}")


# ... (after the script finishes)
    
    print("\n🔍 SANITY CHECK: Random Sample of Classifications")
    print("="*50)
    for category in CE_KEYWORDS.keys():
        print(f"\n--- {category.upper()} SAMPLES ---")
        # Get articles tagged with this category
        subset = df[df['CE_Tags'].apply(lambda tags: category in tags)]
        
        # Print 3 random titles (if available)
        if not subset.empty:
            sample = subset.sample(min(3, len(subset)))
            for _, row in sample.iterrows():
                print(f"📄 {row['title'][:80]}...")
        else:
            print("(No articles found)")

if __name__ == "__main__":
    run_task3_analysis()

