#!/usr/bin/env python3
"""
Round only the filled values (changes made) to two decimal places
Keep original extracted data unchanged
"""

import pandas as pd
import numpy as np
import os

def round_only_filled_values():
    """Round only the values that were filled to 2 decimal places"""
    
    # Read the original and filled datasets
    original_file = "dsi_2000_2020_final_structured_STD_CORRECTED.csv"
    filled_file = "dsi_2000_2020_final_structured_STD_CORRECTED_FILLED_BY_STATION.csv"
    
    try:
        df_original = pd.read_csv(original_file)
        df_filled = pd.read_csv(filled_file)
        print(f"Loaded original: {len(df_original)} records")
        print(f"Loaded filled: {len(df_filled)} records")
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return
    
    # Create backup of filled file
    backup_path = filled_file.replace('.csv', '_BACKUP_BEFORE_ROUNDING.csv')
    df_filled.to_csv(backup_path, index=False)
    print(f"Backup created: {backup_path}")
    
    # Identify numerical columns
    exclude_cols = ['file', 'station_code', 'station_name', 'coordinates']
    numerical_cols = [col for col in df_filled.columns if col not in exclude_cols]
    
    print(f"Processing {len(numerical_cols)} numerical columns")
    
    # Create a copy for rounding
    df_rounded = df_filled.copy()
    
    # Track changes
    total_rounded = 0
    changes_by_station = {}
    
    # Process each station separately
    stations = df_filled['station_code'].unique()
    
    for station in stations:
        print(f"\nProcessing station: {station}")
        
        # Get masks for this station
        station_mask_orig = df_original['station_code'] == station
        station_mask_filled = df_filled['station_code'] == station
        
        station_rounded = 0
        
        # Compare original vs filled for each column
        for col in numerical_cols:
            if col in df_original.columns and col in df_filled.columns:
                # Get original and filled values for this station
                orig_values = df_original.loc[station_mask_orig, col]
                filled_values = df_filled.loc[station_mask_filled, col]
                
                # Find where values were filled (NaN in original, not NaN in filled)
                if len(orig_values) > 0 and len(filled_values) > 0:
                    # Create comparison mask
                    orig_isna = orig_values.isna()
                    filled_notna = filled_values.notna()
                    
                    # Values that were filled
                    filled_mask = orig_isna & filled_notna
                    
                    if filled_mask.any():
                        # Round only the filled values
                        filled_indices = filled_values[filled_mask].index
                        rounded_values = filled_values[filled_mask].round(2)
                        
                        # Update the dataframe
                        df_rounded.loc[filled_indices, col] = rounded_values
                        
                        num_rounded = len(filled_indices)
                        station_rounded += num_rounded
                        
                        if num_rounded > 0:
                            print(f"  {col}: Rounded {num_rounded} filled values")
        
        changes_by_station[station] = station_rounded
        total_rounded += station_rounded
        print(f"  Total rounded for {station}: {station_rounded} values")
    
    # Save the rounded dataset
    output_path = filled_file.replace('.csv', '_ROUNDED_FILLED_VALUES.csv')
    df_rounded.to_csv(output_path, index=False)
    print(f"\nRounded dataset saved to: {output_path}")
    
    # Create summary report
    create_rounding_report(changes_by_station, total_rounded, original_file, filled_file, output_path)
    
    # Verify the results
    verify_rounding_results(df_original, df_filled, df_rounded, numerical_cols)
    
    return output_path

def create_rounding_report(changes_by_station, total_rounded, original_file, filled_file, output_file):
    """Create a detailed report of the rounding process"""
    
    report_path = "filled_values_rounding_report.txt"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("Filled Values Rounding Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Original file: {original_file}\n")
        f.write(f"Filled file: {filled_file}\n")
        f.write(f"Output file: {output_file}\n")
        f.write(f"Method: Round only filled values to 2 decimal places\n\n")
        
        f.write("Rounding Summary:\n")
        f.write("- Only values that were filled (missing in original) were rounded\n")
        f.write("- Original extracted data remains unchanged\n")
        f.write("- Filled values rounded to 2 decimal places\n\n")
        
        f.write(f"Total filled values rounded: {total_rounded}\n\n")
        
        f.write("Rounding Summary by Station:\n")
        f.write("-" * 30 + "\n")
        for station, count in sorted(changes_by_station.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{station}: {count} filled values rounded\n")
        
        f.write(f"\nStations with no filled values: {sum(1 for count in changes_by_station.values() if count == 0)}\n")
        f.write(f"Stations with filled values rounded: {sum(1 for count in changes_by_station.values() if count > 0)}\n")
    
    print(f"Rounding report saved to: {report_path}")

def verify_rounding_results(df_original, df_filled, df_rounded, numerical_cols):
    """Verify the rounding results"""
    
    print("\n" + "=" * 60)
    print("VERIFICATION RESULTS")
    print("=" * 60)
    
    # Check that original data is unchanged
    print("Checking that original data is unchanged...")
    original_unchanged = True
    
    for col in numerical_cols[:5]:  # Check first 5 columns
        if col in df_original.columns and col in df_rounded.columns:
            # Compare non-NaN values
            orig_notna = df_original[col].notna()
            rounded_notna = df_rounded[col].notna()
            
            # Values that exist in both
            common_mask = orig_notna & rounded_notna
            
            if common_mask.any():
                orig_values = df_original.loc[common_mask, col]
                rounded_values = df_rounded.loc[common_mask, col]
                
                # Check if they're equal (allowing for small floating point differences)
                if not np.allclose(orig_values, rounded_values, rtol=1e-10):
                    print(f"  WARNING: Original values changed in {col}")
                    original_unchanged = False
    
    if original_unchanged:
        print("[SUCCESS] Original data unchanged")
    else:
        print("[ERROR] Some original data was modified")
    
    # Check that filled values are rounded
    print("\nChecking that filled values are rounded...")
    
    # Sample check for a few columns
    sample_cols = ['annual_avg_flow_m3s', 'annual_total_m3', 'oct_flow_max_m3']
    
    for col in sample_cols:
        if col in df_filled.columns and col in df_rounded.columns:
            # Find filled values (NaN in original, not NaN in filled)
            orig_isna = df_original[col].isna()
            filled_notna = df_filled[col].notna()
            filled_mask = orig_isna & filled_notna
            
            if filled_mask.any():
                filled_values = df_filled.loc[filled_mask, col]
                rounded_values = df_rounded.loc[filled_mask, col]
                
                # Check if rounded values have max 2 decimal places
                decimal_places = rounded_values.apply(lambda x: len(str(x).split('.')[-1]) if '.' in str(x) else 0)
                max_decimals = decimal_places.max()
                
                print(f"  {col}: Max decimal places in filled values = {max_decimals}")
    
    # Sample of rounded data
    print(f"\nSample of rounded filled data:")
    sample_station = df_rounded['station_code'].iloc[0]
    station_data = df_rounded[df_rounded['station_code'] == sample_station]
    sample_cols = ['station_code', 'year', 'annual_avg_flow_m3s', 'annual_total_m3']
    print(station_data[sample_cols].head(3).to_string())

if __name__ == "__main__":
    print("Rounding only filled values to 2 decimal places...")
    print("Original extracted data will remain unchanged")
    
    # Round filled values
    output_file = round_only_filled_values()
    
    print(f"\n[SUCCESS] Filled values rounding completed!")
    print(f"Output file: {output_file}")
    print("Only filled values were rounded, original data preserved")
