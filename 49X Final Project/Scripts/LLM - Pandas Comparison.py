import sqlite3
import pandas as pd
import os

def compare_llm_effectiveness(pandas_db_path, llm_db_path, output_db_path=None):
    """
    Subtracts LLM results from Pandas results to see exactly what the LLM removed.
    Output: title, url, text.
    """
    if output_db_path is None:
        data_dir = r"C:\Users\Hakan\Desktop\CE49X Final Project\Data"
        output_db_path = os.path.join(data_dir, 'Pandas-LLM Comparison.db')

    # 1. Load the Pandas-Cleaned Data (The 'Before' set)
    print(f"📖 Loading Pandas-cleaned data (Source of truth)...")
    conn1 = sqlite3.connect(pandas_db_path)
    # Target table 'articles'
    df_pandas = pd.read_sql_query("SELECT title, url, full_text FROM articles", conn1)
    conn1.close()

    # 2. Load the LLM-Cleaned Data (The 'After' set)
    print(f"📖 Loading LLM-cleaned data (The filtered set)...")
    conn2 = sqlite3.connect(llm_db_path)
    # Target table 'articles_labeled'
    df_llm = pd.read_sql_query("SELECT title, url, full_text FROM articles_labeled", conn2)
    conn2.close()

    # 3. Normalize Column Names for both
    # We rename 'full_text' to 'text' as requested
    for df in [df_pandas, df_llm]:
        df.rename(columns={'full_text': 'text'}, inplace=True)
        # Clean URLs and text to ensure matching works perfectly
        df['url'] = df['url'].astype(str).str.strip().str.lower()
        df['title'] = df['title'].astype(str).str.strip()

    # 4. PERFORM SUBTRACTION (The "Cleanup" analysis)
    # We want rows in df_pandas whose URL is NOT in df_llm
    print("🔍 Calculating subtractions (Finding removed rows)...")
    removed_df = df_pandas[~df_pandas['url'].isin(df_llm['url'])].copy()

    # 5. SAVE TO DIFF DATABASE
    if os.path.exists(output_db_path):
        os.remove(output_db_path)
    
    diff_conn = sqlite3.connect(output_db_path)
    
    # Save the removed rows
    removed_df.to_sql('removed_articles', diff_conn, index=False, if_exists='replace')
    
    # Create a small summary table for your report
    summary_data = {
        'Description': ['Pandas Initial', 'LLM Kept', 'LLM Removed (Trash)'],
        'Count': [len(df_pandas), len(df_llm), len(removed_df)]
    }
    pd.DataFrame(summary_data).to_sql('comparison_summary', diff_conn, index=False, if_exists='replace')
    
    diff_conn.close()

    print("\n" + "="*30)
    print(f"✅ ANALYSIS COMPLETE")
    print(f"📊 Total Rows Processed: {len(df_pandas)}")
    print(f"📉 Rows Removed by LLM:  {len(removed_df)}")
    print(f"📂 Results saved to: {output_db_path}")
    print("="*30)

if __name__ == "__main__":
    # Corrected Paths
    db_pandas = r"C:\Users\Hakan\Desktop\CE49X Final Project\Data\corpus_pandas_cleaned.db"
    db_llm = r"C:\Users\Hakan\Desktop\CE49X Final Project\Data\corpus_LLM_Improved.db"
    
    compare_llm_effectiveness(db_pandas, db_llm)