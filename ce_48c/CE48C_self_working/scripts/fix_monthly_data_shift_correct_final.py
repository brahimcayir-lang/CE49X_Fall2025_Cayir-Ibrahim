#!/usr/bin/env python3
"""
Final correct fix for monthly data shift issue
"""

import pandas as pd
import numpy as np
import shutil

def fix_monthly_data_shift_correct():
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
                
                # Find the first non-NaN value
                first_data_idx = None
                for i, val in enumerate(current_values):
                    if not pd.isna(val):
                        first_data_idx = i
                        break
                
                if first_data_idx is not None and first_data_idx > 0:
                    # Shift data: move everything from first_data_idx to the left
                    # Example: [NaN, 0.54, 1.32, ...] -> [0.54, 1.32, ..., avg]
                    
                    # Extract the data part (from first_data_idx onwards)
                    data_part = current_values[first_data_idx:]
                    
                    # Create shifted values: data_part fills from the beginning
                    shifted_values = data_part + [np.nan] * (12 - len(data_part))
                    
                    # Fill the last empty position with average of first two data values
                    if len(data_part) >= 2:
                        avg_val = (data_part[0] + data_part[1]) / 2
                        shifted_values[-1] = avg_val
                    elif len(data_part) == 1:
                        shifted_values[-1] = data_part[0]
                    
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
    
    print("October columns (should now have November data):")
    print(df[oct_cols].head(3).to_string())
    
    print("\nNovember columns (should have December data):")
    print(df[nov_cols].head(3).to_string())
    
    print("\nSeptember columns (should have averaged data):")
    print(df[sep_cols].head(3).to_string())
    
    # Test specific values
    print(f"\nSpecific test - Row 0:")
    print(f"oct_flow_max_m3: {df.iloc[0]['oct_flow_max_m3']} (should have 0.54)")
    print(f"nov_flow_max_m3: {df.iloc[0]['nov_flow_max_m3']} (should have 1.32)")
    print(f"dec_flow_max_m3: {df.iloc[0]['dec_flow_max_m3']} (should have 0.62)")
    print(f"sep_flow_max_m3: {df.iloc[0]['sep_flow_max_m3']} (should have average of 0.54 and 1.32)")
    
    return corrected_file

if __name__ == "__main__":
    corrected_file = fix_monthly_data_shift_correct()
    print(f"\n[SUCCESS] Fix completed! Corrected file: {corrected_file}")
    print(f"[BACKUP] Backup created: dsi_2000_2020_final_structured_UPDATED_BACKUP.csv")
