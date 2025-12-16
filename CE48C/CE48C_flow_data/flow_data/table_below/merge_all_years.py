# -*- coding: utf-8 -*-
"""
Merge all year-specific parsed files into a single combined CSV with a year column.
"""

import pandas as pd
from pathlib import Path

def merge_all_years():
    """Merge all year files into one common CSV."""
    
    base_dir = Path(__file__).parent
    
    # Find all parsed files
    parsed_files = sorted(base_dir.glob("dsi_*_full_flow_tables_parsed.csv"))
    
    print(f"Found {len(parsed_files)} parsed files to merge:")
    
    all_dfs = []
    
    for file_path in parsed_files:
        # Extract year from filename (e.g., "dsi_2005_full_flow_tables_parsed.csv" -> 2005)
        year = file_path.stem.replace("dsi_", "").replace("_full_flow_tables_parsed", "")
        
        print(f"  Reading {file_path.name} (year: {year})...")
        
        df = pd.read_csv(file_path)
        df.insert(1, 'year', int(year))  # Insert year column after station_code
        
        all_dfs.append(df)
    
    # Combine all dataframes
    print("\nMerging all years...")
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # Reorder columns to put year after station_code and before page
    cols = list(combined_df.columns)
    cols.remove('year')
    new_cols = ['station_code', 'year'] + [col for col in cols if col != 'station_code']
    combined_df = combined_df[new_cols]
    
    # Save combined file
    output_file = base_dir / "dsi_all_years_combined.csv"
    combined_df.to_csv(output_file, index=False, encoding="utf-8")
    
    print(f"\n✓ SUCCESS!")
    print(f"  Total stations: {len(combined_df)}")
    print(f"  Total columns: {len(combined_df.columns)}")
    print(f"  Years covered: {combined_df['year'].min()} - {combined_df['year'].max()}")
    print(f"  Output: {output_file.name}")
    
    # Print summary by year
    print("\nSummary by year:")
    print("-" * 60)
    year_counts = combined_df.groupby('year').size().sort_index()
    for year, count in year_counts.items():
        print(f"  {year}: {count:3} stations")
    
    return combined_df


if __name__ == "__main__":
    merge_all_years()

