#!/usr/bin/env python3
"""
Simple script to fill year column from filename
"""

import pandas as pd
import re
import os

def fill_year_column():
    """Fill year column from filename."""
    
    input_file = "dsi_2000_2020_final.csv"
    output_file = "dsi_2000_2020_final_with_years.csv"
    
    print(f"Reading {input_file}...")
    
    # Read CSV with proper encoding
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    
    print(f"Data shape: {df.shape}")
    
    # Extract year from filename
    def extract_year(filename):
        if pd.isna(filename):
            return None
        match = re.search(r'dsi_(\d{4})\.pdf', filename, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    # Fill year column
    df['year'] = df['file'].apply(extract_year)
    
    # Results
    years_found = df['year'].notna().sum()
    print(f"Years extracted: {years_found}/{len(df)}")
    print(f"Unique years: {sorted(df['year'].dropna().unique())}")
    
    # Save result
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Saved to: {output_file}")
    
    return df

if __name__ == "__main__":
    fill_year_column()
