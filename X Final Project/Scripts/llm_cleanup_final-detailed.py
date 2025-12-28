import os
import json
import sqlite3
import asyncio
import pandas as pd
from google import genai
from google.genai import types

# --- CONFIGURATION ---
API_KEY = "AIzaSyBZqNlxSVmim2yfZUXqksSZN1MeGLq4e2s"
client = genai.Client(api_key=API_KEY)

BASE_PATH = r"C:\Users\Hakan\Desktop\CE49X Final Project\Data"
SOURCE_DB = os.path.join(BASE_PATH, "corpus_pandas_cleaned.db")
DEST_DB = os.path.join(BASE_PATH, "corpus_LLM_Improved.db")

BATCH_SIZE = 25  
MAX_CONCURRENT_REQUESTS = 25 

SYSTEM_PROMPT = """
You are a peer-reviewer of a Civil Engineering + AI article database. This database collects news articles / scientific articles / magazine entries / yearly sector & company outlook reports related to both Civil Engineering and Artificial Intelligence.
Your task is to audit each article based on the following rules.
DATA AUDIT RULES:

1. VALIDITY: Remove irrelevant data (not Civil Engineering or AI related). (It needs to be related with both, pure CE or AI articles will not cut it). 
However, you needn't be very strict if the scripts seems relevant or is just a snippet of article, you can still consider it 'valid'.

2. SEMANTIC DEDUPLICATION: Identify if this article is the same as another in this batch (even with different titles/URLs). Mark status 'duplicate'.

3. TOPIC ASSIGNMENT:
   CE_Topic: [Structural, Geotechnical, Transportation, Construction Management, Environmental Engineering]
   AI_Topic: [Computer Vision, Predictive Analytics, Generative Design, Robotics/Automation, Machine Learning (General)]

Be a little more lenient on duplicates - if two articles are very similar but have different angles or focus, consider them both valid.
Be a little more lenient than you normally would be on validity - if an article seems somewhat relevant - meaning it mildly relates to both fields, consider it valid

Output ONLY a JSON list of objects: [{"id": 1, "status": "valid", "CE_topic": "...", "AI_topic": "..."}]
"""

async def process_batch(semaphore, batch_df):
    async with semaphore:
        batch_data = ""
        for _, row in batch_df.iterrows():
            text_snippet = str(row['full_text'])[:1200]
            batch_data += f"ID: {row['id']} | Title: {row['title']} | Snippet: {text_snippet}\n---\n"

        try:
            # Using gemini-3-flash-preview for speed & accuracy
            response = await client.aio.models.generate_content(
                model='gemini-3-flash-preview', 
                contents=f"{SYSTEM_PROMPT}\n\nArticles:\n{batch_data}",
                config=types.GenerateContentConfig(response_mime_type='application/json')
            )
            
            # Defensive Parsing
            data = json.loads(response.text)
            if isinstance(data, dict) and "results" in data: # Handle if LLM wraps list in a dict
                data = data["results"]
            
            # Force all keys in the response to lowercase to avoid 'ID' vs 'id' errors
            cleaned_data = []
            for item in data:
                cleaned_item = {str(k).lower(): v for k, v in item.items()}
                cleaned_data.append(cleaned_item)
            return cleaned_data

        except Exception as e:
            print(f"Batch failed or JSON invalid: {e}")
            return []

async def main():
    if not os.path.exists(SOURCE_DB):
        print("Source file not found. Run the Pandas preclean script first.")
        return

    conn = sqlite3.connect(SOURCE_DB)
    df = pd.read_sql_query("SELECT * FROM articles", conn)
    conn.close()

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    tasks = [process_batch(semaphore, df.iloc[i : i + BATCH_SIZE]) 
             for i in range(0, len(df), BATCH_SIZE)]

    print(f"Auditing {len(df)} rows with Gemini 3 Flash...")
    batch_results = await asyncio.gather(*tasks)
    
    # Flatten the list
    results_list = [item for sublist in batch_results for item in sublist]
    
    if not results_list:
        print("CRITICAL ERROR: No results were returned from the LLM. Check your API key and safety settings.")
        return

    results_df = pd.DataFrame(results_list)

    # CHECK: Ensure 'id' exists after normalization
    if 'id' not in results_df.columns:
        print(f"ERROR: LLM failed to return 'id' column. Columns found: {results_df.columns.tolist()}")
        return

    # Ensure ID types match for the merge
    results_df['id'] = pd.to_numeric(results_df['id'], errors='coerce')
    df['id'] = pd.to_numeric(df['id'], errors='coerce')

    print("Merging results and applying final cleanup...")
    final_df = df.merge(results_df, on='id', how='left')
    
    # Filter valid rows and remove helper columns
    # We use .get() to avoid errors if some rows weren't labeled
    final_df = final_df[final_df['status'] == 'valid'].copy()
    
    # Drop columns to reach the 10-column goal
    # (id, title, publication_date, source_domain, url, full_text, search_keywords, category_tab, CE_topic, AI_topic)
    cols_to_drop = [c for c in ['status', 'title_slug', 'is_likely_relevant'] if c in final_df.columns]
    final_df.drop(columns=cols_to_drop, inplace=True)

    print(f"Final Count: {len(final_df)} entries with 10 columns.")

    # Save final database
    conn_dest = sqlite3.connect(DEST_DB)
    final_df.to_sql('articles_labeled', conn_dest, if_exists='replace', index=False)
    conn_dest.close()
    print(f"Process complete! Saved to: {DEST_DB}")

if __name__ == "__main__":
    asyncio.run(main())