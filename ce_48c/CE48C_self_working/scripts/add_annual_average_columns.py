#!/usr/bin/env python3
"""
Add 6 new annual average columns for each metric
Calculate average of 12 months for each metric without changing existing data
"""

import pandas as pd
import numpy as np
import shutil

def add_annual_average_columns():
    # Create backup first
    original_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED_ROUNDED.csv"
    backup_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED_ROUNDED_BACKUP.csv"
    
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
    
    # Create new annual average columns
    new_columns = []
    for metric in monthly_metrics:
        annual_col = f"annual_average_{metric}"
        new_columns.append(annual_col)
        
        # Calculate annual average for each row
        annual_averages = []
        for idx, row in df.iterrows():
            # Get all 12 monthly values for this metric
            monthly_values = []
            for month in months:
                col = f"{month}_{metric}"
                val = row[col]
                if not pd.isna(val):
                    monthly_values.append(val)
            
            # Calculate average of available monthly values
            if len(monthly_values) > 0:
                avg_val = np.mean(monthly_values)
                annual_averages.append(round(avg_val, 2))  # Round to 2 decimal places
            else:
                annual_averages.append(np.nan)
        
        # Add the new column to the dataframe
        df[annual_col] = annual_averages
        print(f"Added column: {annual_col}")
    
    print(f"\nAdded {len(new_columns)} new annual average columns")
    
    # Save the updated file
    updated_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED_ROUNDED_WITH_ANNUAL_AVG.csv"
    df.to_csv(updated_file, index=False)
    print(f"Saved updated file: {updated_file}")
    
    # Verify the new columns
    print("\nVerification - New annual average columns:")
    print(df[new_columns].head(5).to_string())
    
    # Test specific values for first row
    print(f"\nSpecific test - Row 0 annual averages:")
    for metric in monthly_metrics:
        annual_col = f"annual_average_{metric}"
        val = df.iloc[0][annual_col]
        print(f"{annual_col}: {val}")
    
    # Show column count
    print(f"\nTotal columns in file: {len(df.columns)}")
    print(f"Original columns: {len(df.columns) - len(new_columns)}")
    print(f"New columns added: {len(new_columns)}")
    
    return updated_file

if __name__ == "__main__":
    updated_file = add_annual_average_columns()
    print(f"\n[SUCCESS] Annual average columns added! Updated file: {updated_file}")
    print(f"[BACKUP] Backup created: dsi_2000_2020_final_structured_UPDATED_CORRECTED_ROUNDED_BACKUP.csv")
