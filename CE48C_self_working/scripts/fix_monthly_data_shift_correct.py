#!/usr/bin/env python3
"""
Fix monthly data shift issue - shift all monthly metrics one column right when October is empty
and fill September with average of October and December data
"""

import pandas as pd
import numpy as np
import shutil
import os

def fix_monthly_data_shift():
    # Create backup first
    original_file = "dsi_2000_2020_final_structured_UPDATED.csv"
    backup_file = "dsi_2000_2020_final_structured_UPDATED_BACKUP.csv"
    
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
    
    # Process each row
    rows_fixed = 0
    for idx, row in df.iterrows():
        row_fixed = False
        
        # Check each metric
        for metric in monthly_metrics:
            # Get all columns for this metric
            metric_cols = [f"{month}_{metric}" for month in months]
            
            # Check if October is empty (NaN) for this metric
            oct_col = f"oct_{metric}"
            if pd.isna(row[oct_col]):
                # Get current values for this metric
                current_values = [row[col] for col in metric_cols]
                
                # Shift data one column to the right
                # October gets November data, November gets December data, etc.
                shifted_values = [np.nan] + current_values[:-1]
                
                # Fill September (last column) with average of October and December
                # After shift: October has November data, December has January data
                oct_val = shifted_values[0]  # This is November data (was in November column)
                dec_val = shifted_values[2]  # This is January data (was in December column)
                
                if not pd.isna(oct_val) and not pd.isna(dec_val):
                    shifted_values[-1] = (oct_val + dec_val) / 2
                elif not pd.isna(oct_val):
                    shifted_values[-1] = oct_val
                elif not pd.isna(dec_val):
                    shifted_values[-1] = dec_val
                # If both are NaN, leave September as NaN
                
                # Update the row with shifted values
                for i, col in enumerate(metric_cols):
                    df.at[idx, col] = shifted_values[i]
                
                row_fixed = True
        
        if row_fixed:
            rows_fixed += 1
    
    print(f"Fixed {rows_fixed} rows")
    
    # Save the corrected file
    corrected_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED.csv"
    df.to_csv(corrected_file, index=False)
    print(f"Saved corrected file: {corrected_file}")
    
    # Verify the fix
    print("\nVerification - First few rows after fix:")
    oct_cols = [col for col in df.columns if col.startswith('oct_')]
    nov_cols = [col for col in df.columns if col.startswith('nov_')]
    sep_cols = [col for col in df.columns if col.startswith('sep_')]
    
    print("October columns (should now have November data where it was empty):")
    print(df[oct_cols].head(3).to_string())
    
    print("\nNovember columns (should have December data where October was empty):")
    print(df[nov_cols].head(3).to_string())
    
    print("\nSeptember columns (should have averaged data where October was empty):")
    print(df[sep_cols].head(3).to_string())
    
    # Test specific values
    print(f"\nSpecific test - Row 0:")
    print(f"oct_flow_max_m3: {df.iloc[0]['oct_flow_max_m3']} (was empty, should have 0.54)")
    print(f"nov_flow_max_m3: {df.iloc[0]['nov_flow_max_m3']} (should have 1.32)")
    print(f"dec_flow_max_m3: {df.iloc[0]['dec_flow_max_m3']} (should have 0.62)")
    print(f"sep_flow_max_m3: {df.iloc[0]['sep_flow_max_m3']} (should have average)")
    
    return corrected_file

if __name__ == "__main__":
    corrected_file = fix_monthly_data_shift()
    print(f"\n[SUCCESS] Fix completed! Corrected file: {corrected_file}")
    print(f"[BACKUP] Backup created: dsi_2000_2020_final_structured_UPDATED_BACKUP.csv")
