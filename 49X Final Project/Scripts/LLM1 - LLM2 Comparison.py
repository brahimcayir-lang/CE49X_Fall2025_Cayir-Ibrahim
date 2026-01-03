import sqlite3
import pandas as pd
import os

def compare_llm_versions(db1_path, db2_path, diff_db_path=None):
    """
    Compares two LLM-processed databases.
    Identifies rows present in LLM1 but removed in LLM2.
    Output: title, url, text (3 columns).
    """
    if diff_db_path is None:
        data_dir = r"C:\Users\Hakan\Desktop\CE49X Final Project\Data"
        diff_db_path = os.path.join(data_dir, 'LLM1 - LLM2 comparison.db')

    # Ensure we start with a fresh diff database
    if os.path.exists(diff_db_path):
        os.remove(diff_db_path)

    print(f"📖 Loading LLM Run 1 (Source): {os.path.basename(db1_path)}")
    conn1 = sqlite3.connect(db1_path)
    # Using a TRY block in case the table name varies
    try:
        df1 = pd.read_sql_query("SELECT title, url, full_text FROM articles_labeled", conn1)
    except:
        df1 = pd.read_sql_query("SELECT title, url, full_text FROM articles", conn1)
    conn1.close()

    print(f"📖 Loading LLM Run 2 (Improved): {os.path.basename(db2_path)}")
    conn2 = sqlite3.connect(db2_path)
    try:
        df2 = pd.read_sql_query("SELECT title, url, full_text FROM articles_labeled", conn2)
    except:
        df2 = pd.read_sql_query("SELECT title, url, full_text FROM articles", conn2)
    conn2.close()

    # --- NORMALIZATION ---
    # Convert both to 3 columns: title, url, text
    for df in [df1, df2]:
        df.rename(columns={'full_text': 'text'}, inplace=True)
        # Clean URLs for perfect matching (lowercase and strip spaces)
        df['url'] = df['url'].astype(str).str.strip().str.lower()
        df['title'] = df['title'].astype(str).str.strip()

    # --- SUBTRACTION ---
    # Find rows that exist in LLM1 but are GONE in LLM2
    print("🔍 Calculating delta (Rows removed in the Improved run)...")
    removed_df = df1[~df1['url'].isin(df2['url'])].copy()

    # --- SAVE RESULTS ---
    diff_conn = sqlite3.connect(diff_db_path)
    
    # Save the 3-column 'Removed' data
    removed_df.to_sql('removed_articles', diff_conn, index=False, if_exists='replace')
    
    # Create a summary for your report
    summary_data = {
        'Run': ['LLM Run 1', 'LLM Run 2 (Improved)', 'Difference (Removed)'],
        'Article_Count': [len(df1), len(df2), len(removed_df)]
    }
    pd.DataFrame(summary_data).to_sql('comparison_summary', diff_conn, index=False, if_exists='replace')
    
    diff_conn.close()

    print("\n" + "="*40)
    print(f"📊 COMPARISON SUMMARY")
    print(f"LLM 1 Count: {len(df1)}")
    print(f"LLM 2 Count: {len(df2)}")
    print(f"Rows 'Cleaned' in v2: {len(removed_df)}")
    print(f"📂 Results saved to: {diff_db_path}")
    print("="*40)

if __name__ == "__main__":
    # The two LLM versions you want to compare
    llm_v1 = r"C:\Users\Hakan\Desktop\CE49X Final Project\Data\corpus_LLM.db"
    llm_v2 = r"C:\Users\Hakan\Desktop\CE49X Final Project\Data\corpus_LLM_Improved.db"
    
    compare_llm_versions(llm_v1, llm_v2)