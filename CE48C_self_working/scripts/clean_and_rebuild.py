#!/usr/bin/env python3
"""
COMPLETELY CLEAN AND REBUILD CSV with correct 2020 data
"""

import pandas as pd
import os

def clean_and_rebuild_csv():
    """Completely clean the CSV and rebuild with correct 2020 data"""
    csv_path = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_final_structured.csv"
    
    # Read the current CSV
    df = pd.read_csv(csv_path)
    print(f"Original CSV has {len(df)} records")
    
    # Remove ALL 2020 data completely
    df_clean = df[df['year'] != 2020]
    print(f"After removing 2020 data: {len(df_clean)} records")
    
    # Save the cleaned CSV
    df_clean.to_csv(csv_path, index=False)
    print(f"Saved cleaned CSV with {len(df_clean)} records")
    
    # Now run the extraction to add only correct 2020 data
    print("\nNow extracting correct 2020 data...")
    os.system("py extract_2020_final.py")

if __name__ == "__main__":
    clean_and_rebuild_csv()
