#!/usr/bin/env python3
"""
Apply statistical outlier correction using ±3 standard deviations
Replace outliers with median values for better reliability
"""

import pandas as pd
import numpy as np
import shutil

def apply_outlier_correction():
    # Create backup first
    original_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED_ROUNDED_WITH_ANNUAL_AVG.csv"
    backup_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED_ROUNDED_WITH_ANNUAL_AVG_BACKUP.csv"
    
    print(f"Creating backup: {backup_file}")
    shutil.copy2(original_file, backup_file)
    
    # Read the CSV
    df = pd.read_csv(original_file)
    print(f"Loaded {len(df)} records")
    
    # Define numerical columns to check for outliers
    numerical_columns = [
        'catchment_area_km2', 'annual_avg_flow_m3s', 'annual_total_m3', 
        'mm_total', 'avg_ltsnkm2'
    ]
    
    # Add all monthly metric columns
    monthly_metrics = ['flow_max_m3', 'flow_min_m3', 'flow_avg_m3', 'ltsnkm2_m3', 'akim_mm_m3', 'milm3_m3']
    months = ['oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep']
    
    for metric in monthly_metrics:
        for month in months:
            numerical_columns.append(f"{month}_{metric}")
    
    # Add annual average columns
    for metric in monthly_metrics:
        numerical_columns.append(f"annual_average_{metric}")
    
    print(f"Checking {len(numerical_columns)} numerical columns for outliers")
    
    # Track corrections
    total_corrections = 0
    correction_log = []
    
    # Apply outlier correction to each numerical column
    for col in numerical_columns:
        if col in df.columns:
            # Get non-null values
            non_null_values = df[col].dropna()
            
            if len(non_null_values) > 3:  # Need at least 4 values for meaningful statistics
                # Calculate statistics
                mean_val = non_null_values.mean()
                std_val = non_null_values.std()
                median_val = non_null_values.median()
                
                # Define outlier boundaries (±3 standard deviations)
                lower_bound = mean_val - 3 * std_val
                upper_bound = mean_val + 3 * std_val
                
                # Find outliers
                outliers_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                outliers_count = outliers_mask.sum()
                
                if outliers_count > 0:
                    # Replace outliers with median value
                    df.loc[outliers_mask, col] = round(median_val, 2)
                    
                    correction_log.append({
                        'column': col,
                        'outliers_found': outliers_count,
                        'lower_bound': round(lower_bound, 2),
                        'upper_bound': round(upper_bound, 2),
                        'median_replacement': round(median_val, 2),
                        'mean': round(mean_val, 2),
                        'std': round(std_val, 2)
                    })
                    
                    total_corrections += outliers_count
                    print(f"Column {col}: {outliers_count} outliers corrected (bounds: {lower_bound:.2f} to {upper_bound:.2f})")
    
    print(f"\nTotal corrections made: {total_corrections}")
    
    # Save the corrected file
    corrected_file = "dsi_2000_2020_final_structured_STD_CORRECTED.csv"
    df.to_csv(corrected_file, index=False)
    print(f"Saved corrected file: {corrected_file}")
    
    # Create correction report
    create_correction_report(correction_log, corrected_file)
    
    # Verify the corrections
    print("\nVerification - Sample of corrected data:")
    print("First 5 rows of key columns:")
    key_cols = ['annual_avg_flow_m3s', 'annual_total_m3', 'annual_average_flow_avg_m3']
    print(df[key_cols].head().to_string())
    
    return corrected_file, correction_log

def create_correction_report(correction_log, corrected_file):
    """Create a detailed report of all corrections made"""
    
    if correction_log:
        report_file = "outlier_correction_report.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("OUTLIER CORRECTION REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Method: ±3 Standard Deviations\n")
            f.write(f"Replacement: Median values (rounded to 2 decimals)\n")
            f.write(f"Corrected file: {corrected_file}\n\n")
            
            f.write("CORRECTIONS BY COLUMN:\n")
            f.write("-" * 30 + "\n")
            
            for correction in correction_log:
                f.write(f"\nColumn: {correction['column']}\n")
                f.write(f"  Outliers found: {correction['outliers_found']}\n")
                f.write(f"  Lower bound: {correction['lower_bound']}\n")
                f.write(f"  Upper bound: {correction['upper_bound']}\n")
                f.write(f"  Mean: {correction['mean']}\n")
                f.write(f"  Std Dev: {correction['std']}\n")
                f.write(f"  Median replacement: {correction['median_replacement']}\n")
            
            f.write(f"\nSUMMARY:\n")
            f.write(f"Total columns corrected: {len(correction_log)}\n")
            f.write(f"Total outliers replaced: {sum(c['outliers_found'] for c in correction_log)}\n")
        
        print(f"Correction report saved to: {report_file}")
    else:
        print("No outliers found - no corrections needed!")

if __name__ == "__main__":
    corrected_file, correction_log = apply_outlier_correction()
    print(f"\n[SUCCESS] Outlier correction completed!")
    print(f"[CORRECTED] File: {corrected_file}")
    print(f"[BACKUP] Original file preserved")
