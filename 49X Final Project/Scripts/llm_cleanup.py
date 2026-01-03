import os
import json
import sqlite3
import asyncio
import pandas as pd
from google import genai
from google.genai import types

# --- CONFIGURATION ---
API_KEY = "AIzaSyBZqNlxSVmim2yfZUXqksSZN1MeGLq4e2s"
# 2025 Standard: Initialize the client directly with the key
client = genai.Client(api_key=API_KEY)

# Use raw strings for Windows paths to avoid errors
BASE_PATH = r"C:\Users\Hakan\Desktop\CE49X Final Project\Data"
SOURCE_DB = os.path.join(BASE_PATH, "corpus.db")
DEST_DB = os.path.join(BASE_PATH, "corpus_LLM_Trial.db")

BATCH_SIZE = 25  # Increased for speed
MAX_CONCURRENT_REQUESTS = 8  # Parallel API calls

SYSTEM_PROMPT = """
Return ONLY a JSON list of objects.
Tasks:
1. Remove irrelevant data (not Civil Engineering or AI related). (It needs to be related with both, pure CE or AI articles will not cut it)
2. Remove semantic duplicates.
3. For valid entries, assign:
   CE_Topic: [Structural, Geotechnical, Transportation, Construction Management, Environmental Engineering]
   AI_Topic: [Computer Vision, Predictive Analytics, Generative Design, Robotics/Automation, Machine Learning (General)]

Output format: [{"id": 1, "status": "valid", "CE_topic": "...", "AI_topic": "..."}]
Status must be "valid", "irrelevant", or "duplicate".
"""

async def process_batch(semaphore, batch_df):
    async with semaphore:
        batch_data = ""
        for _, row in batch_df.iterrows():
            # Send Title + snippet of Full Text to identify topics swiftly
            text_snippet = str(row['full_text'])[:1000]
            batch_data += f"ID: {row['id']} | Title: {row['title']} | Text: {text_snippet}\n---\n"

        try:
            # Using Gemini 2.0 Flash - the fastest model available in late 2025
            response = await client.aio.models.generate_content(
                model='gemini-2.0-flash', 
                contents=f"{SYSTEM_PROMPT}\n\nArticles:\n{batch_data}",
                config=types.GenerateContentConfig(response_mime_type='application/json')
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error in batch: {e}")
            return []

async def main():
    if not os.path.exists(SOURCE_DB):
        print(f"File not found: {SOURCE_DB}")
        return

    print("Loading data from corpus.db...")
    conn_src = sqlite3.connect(SOURCE_DB)
    # This reads all 8 columns: id, title, publication_date, source_domain, url, full_text, search_keywords, category_tab
    df = pd.read_sql_query("SELECT * FROM articles", conn_src)
    conn_src.close()

    # Create parallel tasks
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    tasks = [process_batch(semaphore, df.iloc[i : i + BATCH_SIZE]) 
             for i in range(0, len(df), BATCH_SIZE)]

    print(f"Processing {len(df)} rows with Gemini 2.0 Flash...")
    batch_results = await asyncio.gather(*tasks)
    
    # Flatten and Merge
    results_list = [item for sublist in batch_results for item in sublist]
    results_df = pd.DataFrame(results_list)

    # Merge original 8 columns with new labels
    # results_df contains: id, status, CE_topic, AI_topic
    final_df = df.merge(results_df, on='id', how='left')
    
    # CLEANING: Filter rows based on AI judgment
    initial_count = len(final_df)
    final_df = final_df[final_df['status'] == 'valid'].copy()
    
    # Drop 'status' column -> Final result is exactly 10 columns
    final_df.drop(columns=['status'], inplace=True)
    
    print(f"Cleaning complete. Removed {initial_count - len(final_df)} entries.")
    print(f"Final dataset: {len(final_df)} entries with 10 columns.")

    # SAVE: Write to the new database file
    conn_dest = sqlite3.connect(DEST_DB)
    final_df.to_sql('articles_labeled', conn_dest, if_exists='replace', index=False)
    conn_dest.close()
    
    print(f"Successfully saved to: {DEST_DB}")

if __name__ == "__main__":
    asyncio.run(main())