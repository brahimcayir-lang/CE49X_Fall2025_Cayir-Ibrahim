#!/usr/bin/env python3
"""
Debug and fix the monthly data shift issue
"""

import pandas as pd
import numpy as np
import shutil

def debug_and_fix():
    # Create backup first
    original_file = "dsi_2000_2020_final_structured_UPDATED.csv"
    backup_file = "dsi_2000_2020_final_structured_UPDATED_BACKUP.csv"
    
    print(f"Creating backup: {backup_file}")
    shutil.copy2(original_file, backup_file)
    
    # Read the CSV
    df = pd.read_csv(original_file)
    print(f"Loaded {len(df)} records")
    
    # Let's focus on one specific case first - row 0, flow_max_m3
    print("\n=== DEBUGGING ROW 0, flow_max_m3 ===")
    row_idx = 0
    metric = 'flow_max_m3'
    months = ['oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep']
    
    # Get current values
    current_values = []
    for month in months:
        col = f"{month}_{metric}"
        val = df.iloc[row_idx][col]
        current_values.append(val)
        print(f"{col}: {val}")
    
    print(f"\nCurrent values: {current_values}")
    
    # Check if October is empty
    oct_val = current_values[0]
    print(f"October value: {oct_val}, Is NaN: {pd.isna(oct_val)}")
    
    if pd.isna(oct_val):
        print("October is empty - shifting data...")
        
        # Shift right: [oct, nov, dec, ...] -> [NaN, oct, nov, dec, ...]
        shifted_values = [np.nan] + current_values[:-1]
        print(f"Shifted values: {shifted_values}")
        
        # Fill September with average of October and December
        oct_val_shifted = shifted_values[0]  # November data
        dec_val_shifted = shifted_values[2]   # January data
        print(f"October (has November data): {oct_val_shifted}")
        print(f"December (has January data): {dec_val_shifted}")
        
        if not pd.isna(oct_val_shifted) and not pd.isna(dec_val_shifted):
            avg_val = (oct_val_shifted + dec_val_shifted) / 2
            shifted_values[-1] = avg_val
            print(f"September filled with average: {avg_val}")
        else:
            print("Cannot calculate average - one or both values are NaN")
        
        print(f"Final shifted values: {shifted_values}")
        
        # Apply the fix to the DataFrame
        for i, month in enumerate(months):
            col = f"{month}_{metric}"
            df.at[row_idx, col] = shifted_values[i]
        
        print("Applied fix to DataFrame")
    
    # Verify the fix
    print(f"\nAfter fix - Row 0, flow_max_m3:")
    for month in months:
        col = f"{month}_{metric}"
        val = df.iloc[row_idx][col]
        print(f"{col}: {val}")
    
    # Save the corrected file
    corrected_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED.csv"
    df.to_csv(corrected_file, index=False)
    print(f"\nSaved corrected file: {corrected_file}")

if __name__ == "__main__":
    debug_and_fix()
