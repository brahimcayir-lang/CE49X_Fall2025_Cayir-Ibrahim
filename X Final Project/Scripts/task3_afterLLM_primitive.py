import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# --- 1. CONFIGURATION ---
BASE_PATH = r"C:\Users\Hakan\Desktop\CE49X Final Project\Data"
DB_PATH = os.path.join(BASE_PATH, 'corpus_LLM.db')

# Output Directory for Deliverables
OUTPUT_DIR = r"C:\Users\Hakan\Desktop\CE49X Final Project\Outputs\AfterLLM_Primitive"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_task3_analysis():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return

    print(f"⚙️ Loading data from {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM articles_labeled", conn)
        conn.close()
    except Exception as e:
        print(f"❌ Error reading DB: {e}")
        return

    # --- 2. COLUMN DETECTION & NORMALIZATION ---
    # Convert all column names to lowercase to avoid Casing issues
    df.columns = [c.lower() for c in df.columns]
    
    # Identify the correct columns
    ce_col = next((c for c in df.columns if 'ce' in c and 'topic' in c), None)
    ai_col = next((c for c in df.columns if 'ai' in c and 'topic' in c), None)

    if not ce_col or not ai_col:
        print(f"❌ ERROR: Could not find topic columns. Available columns: {list(df.columns)}")
        print("Double-check your LLM script to ensure 'CE_topic' and 'AI_topic' were saved.")
        return

    print(f"✅ Found CE column: '{ce_col}' and AI column: '{ai_col}'")

    # Fill empty labels to avoid NaNs
    df[ce_col] = df[ce_col].fillna('')
    df[ai_col] = df[ai_col].fillna('')

    # --- NORMALIZE TOPIC LABELS (merge variants like "Artificial Intelligence" vs "Artificial Intelligence (General)") ---
    def canonicalize_label(lbl: str, kind: str):
        s = (lbl or '').strip().lower()
        if s in ('', 'n/a', 'na', 'none', 'unknown'):
            return 'Uncategorized'
        if kind == 'ai':
            if 'machine' in s or 'ml' in s:
                return 'Machine Learning (General)'
            if 'robot' in s or 'automation' in s:
                return 'Robotics/Automation'
            if 'vision' in s or 'computer vision' in s:
                return 'Computer Vision'
            if 'generat' in s:
                return 'Generative Design'
            if 'predict' in s or 'analytics' in s:
                return 'Predictive Analytics'
            if 'digital' in s and 'twin' in s:
                return 'Digital Twins'
            if 'artificial' in s or s == 'ai' or 'artificial intelligence' in s:
                return 'Artificial Intelligence (General)'
            if s == 'general':
                return 'General'
            return lbl.strip()
        else:  # ce topics
            if 'construction' in s:
                return 'Construction Management'
            if 'struct' in s:
                return 'Structural'
            if 'transport' in s:
                return 'Transportation'
            if 'geo' in s:
                return 'Geotechnical'
            if 'environment' in s or 'env' in s:
                return 'Environmental Engineering'
            if 'robot' in s or 'automation' in s:
                return 'Robotics/Automation'
            if 'generat' in s:
                return 'Generative Design'
            if s == 'general':
                return 'General'
            return lbl.strip() or 'Uncategorized'

    df[ce_col] = df[ce_col].astype(str).apply(lambda v: canonicalize_label(v, 'ce'))
    df[ai_col] = df[ai_col].astype(str).apply(lambda v: canonicalize_label(v, 'ai'))

    # --- 3. TAGGING SUMMARY ---
    print("📊 Calculating Tag Statistics...")
    ce_counts = df[ce_col].value_counts().sort_values(ascending=False)
    ai_counts = df[ai_col].value_counts().sort_values(ascending=False)

    with open(os.path.join(OUTPUT_DIR, "Task3_Distribution_Report.txt"), "w", encoding="utf-8") as f:
        f.write("=== TASK 3: CATEGORY DISTRIBUTION ===\n\n")
        f.write(f"CIVIL ENGINEERING AREAS ({ce_col}):\n")
        f.write(ce_counts.to_string() + "\n\n")
        f.write(f"AI TECHNOLOGIES ({ai_col}):\n")
        f.write(ai_counts.to_string() + "\n")

    # --- 4. CO-OCCURRENCE MATRIX & HEATMAP ---
    print("🧩 Generating Co-occurrence Heatmap...")
    # ensure numeric counts, stable ordering, and no NaNs
    matrix = pd.crosstab(df[ce_col], df[ai_col]).fillna(0).astype(int)
    if matrix.empty:
        print("⚠️ Co-occurrence matrix is empty; skipping heatmap.")
    else:
        # sort rows/cols for consistent plotting
        matrix = matrix.sort_index().sort_index(axis=1)

        plt.figure(figsize=(12, 8), dpi=150)
        sns.heatmap(
            matrix,
            annot=True,
            fmt="d",
            cmap="YlGnBu",
            cbar=True,
            linewidths=0.5,
            linecolor="white",
            annot_kws={"size": 8}
        )
        plt.title('Heatmap: CE Areas vs. AI Technologies', fontsize=15)
        plt.ylabel('Civil Engineering Area')
        plt.xlabel('AI Technology')
        plt.xticks(rotation=45, ha='right', fontsize=8)
        plt.yticks(fontsize=8)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "Task3_Heatmap.png"), dpi=300)
        plt.close()

    # --- 5. TEMPORAL TRENDS ---
    if 'publication_date' in df.columns:
        print("📈 Analyzing Temporal Trends...")
        # robust parsing: try standard parsing (with UTC) then fall back to extracting a 4-digit year
        df['date'] = pd.to_datetime(df['publication_date'], errors='coerce', utc=True, infer_datetime_format=True)

        if df['date'].notna().any():
            # some rows parsed successfully -> get year from parsed datetimes
            df['year'] = df['date'].dt.year
        else:
            # no parsable datetimes: try extracting a YYYY pattern from the raw strings
            yrs = df['publication_date'].astype(str).str.extract(r'([12]\d{3})')
            df['year'] = pd.to_numeric(yrs[0], errors='coerce')

        # drop rows without a valid year
        df = df.dropna(subset=['year'])
        if df.empty:
            print("⚠️ No valid publication years found after parsing.")
        else:
            df['year'] = df['year'].astype(int)
            temporal = df.groupby(['year', ce_col]).size().unstack(fill_value=0)

            if not temporal.empty:
                plt.figure(figsize=(12, 6))
                temporal.plot(kind='line', marker='o', ax=plt.gca())
                plt.title('Trends: CE Topics Over Time', fontsize=14)
                plt.legend(title='CE Area', bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(os.path.join(OUTPUT_DIR, "Task3_Temporal_Trends.png"), dpi=300)
                plt.close()

    print(f"\n✅ Task 3 Complete! Results in: {OUTPUT_DIR}")

if __name__ == "__main__":
    run_task3_analysis()