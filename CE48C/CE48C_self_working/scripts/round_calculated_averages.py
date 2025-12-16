#!/usr/bin/env python3
"""
Round only the calculated average values to 2 decimal places
Leave all original extracted data unchanged
"""

import pandas as pd
import numpy as np
import shutil

def round_calculated_averages():
    # Create backup first
    original_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED.csv"
    backup_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED_BACKUP.csv"
    
    print(f"Creating backup: {backup_file}")
    shutil.copy2(original_file, backup_file)
    
    # Read the CSV
    df = pd.read_csv(original_file)
    print(f"Loaded {len(df)} records")
    
    # Define all monthly metric columns (6 metrics x 12 months)
    monthly_metrics = [
        'flow_max_m3', 'flow_min_m3', 'flow_avg_m3', 
        'ltsnkm2_m3', 'akim_mm_m3', 'milm3_m3'
    ]
    
    months = ['oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep']
    
    # Process each row to identify and round only calculated averages
    rows_processed = 0
    for idx, row in df.iterrows():
        row_processed = False
        
        # Check each metric
        for metric in monthly_metrics:
            # Get all columns for this metric
            metric_cols = [f"{month}_{metric}" for month in months]
            
            # Check if October was originally empty (NaN) for this metric
            # This means September was calculated as an average
            oct_col = f"oct_{metric}"
            sep_col = f"sep_{metric}"
            
            # Read the backup to check original October value
            backup_df = pd.read_csv(backup_file)
            original_oct_val = backup_df.iloc[idx][oct_col]
            
            if pd.isna(original_oct_val):
                # October was originally empty, so September was calculated
                # Round the September value to 2 decimal places
                sep_val = df.iloc[idx][sep_col]
                if not pd.isna(sep_val):
                    rounded_sep_val = round(sep_val, 2)
                    df.at[idx, sep_col] = rounded_sep_val
                    row_processed = True
        
        if row_processed:
            rows_processed += 1
    
    print(f"Processed {rows_processed} rows")
    
    # Save the corrected file
    final_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED_ROUNDED.csv"
    df.to_csv(final_file, index=False)
    print(f"Saved final file: {final_file}")
    
    # Verify the rounding
    print("\nVerification - September columns (calculated averages, should be rounded to 2 decimals):")
    sep_cols = [col for col in df.columns if col.startswith('sep_')]
    print(df[sep_cols].head(5).to_string())
    
    # Test specific values
    print(f"\nSpecific test - Row 0 September values:")
    for metric in monthly_metrics:
        sep_col = f"sep_{metric}"
        val = df.iloc[0][sep_col]
        print(f"{sep_col}: {val}")
    
    return final_file

if __name__ == "__main__":
    final_file = round_calculated_averages()
    print(f"\n[SUCCESS] Rounding completed! Final file: {final_file}")
    print(f"[BACKUP] Backup created: dsi_2000_2020_final_structured_UPDATED_CORRECTED_BACKUP.csv")
