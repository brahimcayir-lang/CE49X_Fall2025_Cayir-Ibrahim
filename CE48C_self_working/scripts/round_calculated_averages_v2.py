#!/usr/bin/env python3
"""
Round only the calculated average values to 2 decimal places
Leave all original extracted data unchanged
"""

import pandas as pd
import numpy as np
import shutil

def round_calculated_averages():
    # Use the original backup that contains the data before shifting
    original_backup = "dsi_2000_2020_final_structured_UPDATED_BACKUP.csv"
    current_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED.csv"
    final_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED_ROUNDED.csv"
    
    # Create backup of current file
    backup_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED_BACKUP.csv"
    print(f"Creating backup: {backup_file}")
    shutil.copy2(current_file, backup_file)
    
    # Read both files
    df_current = pd.read_csv(current_file)
    df_original = pd.read_csv(original_backup)
    print(f"Loaded {len(df_current)} records")
    
    # Define all monthly metric columns (6 metrics x 12 months)
    monthly_metrics = [
        'flow_max_m3', 'flow_min_m3', 'flow_avg_m3', 
        'ltsnkm2_m3', 'akim_mm_m3', 'milm3_m3'
    ]
    
    months = ['oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep']
    
    # Process each row to identify and round only calculated averages
    rows_processed = 0
    for idx, row in df_current.iterrows():
        row_processed = False
        
        # Check each metric
        for metric in monthly_metrics:
            # Check if October was originally empty (NaN) for this metric
            oct_col = f"oct_{metric}"
            sep_col = f"sep_{metric}"
            
            # Check original October value from the original backup
            original_oct_val = df_original.iloc[idx][oct_col]
            
            if pd.isna(original_oct_val):
                # October was originally empty, so September was calculated
                # Round the September value to 2 decimal places
                sep_val = df_current.iloc[idx][sep_col]
                if not pd.isna(sep_val):
                    rounded_sep_val = round(sep_val, 2)
                    df_current.at[idx, sep_col] = rounded_sep_val
                    row_processed = True
        
        if row_processed:
            rows_processed += 1
    
    print(f"Processed {rows_processed} rows")
    
    # Save the corrected file
    df_current.to_csv(final_file, index=False)
    print(f"Saved final file: {final_file}")
    
    # Verify the rounding
    print("\nVerification - September columns (calculated averages, should be rounded to 2 decimals):")
    sep_cols = [col for col in df_current.columns if col.startswith('sep_')]
    print(df_current[sep_cols].head(5).to_string())
    
    # Test specific values
    print(f"\nSpecific test - Row 0 September values:")
    for metric in monthly_metrics:
        sep_col = f"sep_{metric}"
        val = df_current.iloc[0][sep_col]
        print(f"{sep_col}: {val}")
    
    return final_file

if __name__ == "__main__":
    final_file = round_calculated_averages()
    print(f"\n[SUCCESS] Rounding completed! Final file: {final_file}")
    print(f"[BACKUP] Backup created: dsi_2000_2020_final_structured_UPDATED_CORRECTED_BACKUP.csv")
