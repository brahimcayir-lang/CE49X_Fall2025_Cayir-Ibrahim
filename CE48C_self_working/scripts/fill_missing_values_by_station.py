#!/usr/bin/env python3
"""
Fill missing values using linear interpolation or forward/backward fill methods
Only using data from the same station (not mixing between stations)
"""

import pandas as pd
import numpy as np
import os

def fill_missing_values_by_station():
    """Fill missing values using station-specific data only"""
    
    # Use the exact file path provided by user
    csv_file = "dsi_2000_2020_final_structured_STD_CORRECTED.csv"
    
    try:
        df = pd.read_csv(csv_file)
        print(f"Successfully loaded {len(df)} records from {csv_file}")
    except FileNotFoundError:
        print(f"Error: File {csv_file} not found!")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Create backup
    backup_path = csv_file.replace('.csv', '_BACKUP_BEFORE_FILLING.csv')
    df.to_csv(backup_path, index=False)
    print(f"Backup created: {backup_path}")
    
    # Identify numerical columns for filling (exclude non-numerical columns)
    exclude_cols = ['file', 'station_code', 'station_name', 'coordinates']
    numerical_cols = [col for col in df.columns if col not in exclude_cols]
    
    print(f"\nProcessing {len(numerical_cols)} numerical columns")
    print(f"Excluded columns: {exclude_cols}")
    
    # Get unique stations
    stations = df['station_code'].unique()
    print(f"\nFound {len(stations)} unique stations")
    
    total_filled = 0
    station_summary = {}
    
    # Process each station separately
    for station in stations:
        print(f"\nProcessing station: {station}")
        
        # Get data for this station only
        station_mask = df['station_code'] == station
        station_data = df[station_mask].copy()
        
        if len(station_data) < 2:
            print(f"  Skipping {station} - insufficient data ({len(station_data)} records)")
            continue
        
        # Sort by year to ensure proper order for interpolation
        station_data = station_data.sort_values('year')
        
        station_filled = 0
        
        # Process each numerical column
        for col in numerical_cols:
            if col in station_data.columns:
                # Count missing values before filling
                missing_before = station_data[col].isna().sum()
                
                if missing_before > 0:
                    # Method 1: Try linear interpolation first (for time series data)
                    if col in ['year', 'annual_avg_flow_m3s', 'annual_total_m3', 'mm_total', 'avg_ltsnkm2']:
                        # For main flow metrics, use linear interpolation
                        station_data[col] = station_data[col].interpolate(method='linear')
                        
                        # If still missing values at edges, use forward/backward fill
                        station_data[col] = station_data[col].ffill().bfill()
                    
                    # Method 2: For monthly data, use forward/backward fill
                    elif any(month in col for month in ['oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep']):
                        # For monthly data, use forward fill first, then backward fill
                        station_data[col] = station_data[col].ffill().bfill()
                    
                    # Method 3: For other numerical columns, use median of the station
                    else:
                        station_median = station_data[col].median(skipna=True)
                        if pd.notna(station_median):
                            station_data[col] = station_data[col].fillna(station_median)
                    
                    # Count filled values
                    missing_after = station_data[col].isna().sum()
                    filled_count = missing_before - missing_after
                    
                    if filled_count > 0:
                        station_filled += filled_count
                        print(f"  {col}: Filled {filled_count} missing values")
        
        # Update the main dataframe with filled data
        df.loc[station_mask, numerical_cols] = station_data[numerical_cols]
        
        station_summary[station] = station_filled
        total_filled += station_filled
        
        print(f"  Total filled for {station}: {station_filled} values")
    
    # Save the filled dataset
    output_path = csv_file.replace('.csv', '_FILLED_BY_STATION.csv')
    df.to_csv(output_path, index=False)
    print(f"\nFilled dataset saved to: {output_path}")
    
    # Create summary report
    create_filling_report(station_summary, total_filled, csv_file, output_path)
    
    # Verify the results
    verify_filling_results(df, numerical_cols)
    
    return output_path

def create_filling_report(station_summary, total_filled, input_file, output_file):
    """Create a detailed report of the filling process"""
    
    report_path = "missing_values_filling_report.txt"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("Missing Values Filling Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Input file: {input_file}\n")
        f.write(f"Output file: {output_file}\n")
        f.write(f"Method: Station-specific filling (no mixing between stations)\n\n")
        
        f.write("Filling Methods Used:\n")
        f.write("- Linear interpolation + forward/backward fill for main flow metrics\n")
        f.write("- Forward/backward fill for monthly data\n")
        f.write("- Median fill for other numerical columns\n\n")
        
        f.write(f"Total values filled: {total_filled}\n\n")
        
        f.write("Filling Summary by Station:\n")
        f.write("-" * 30 + "\n")
        for station, count in sorted(station_summary.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{station}: {count} values filled\n")
        
        f.write(f"\nStations with no missing values: {sum(1 for count in station_summary.values() if count == 0)}\n")
        f.write(f"Stations with missing values filled: {sum(1 for count in station_summary.values() if count > 0)}\n")
    
    print(f"Filling report saved to: {report_path}")

def verify_filling_results(df, numerical_cols):
    """Verify the filling results"""
    
    print("\n" + "=" * 60)
    print("VERIFICATION RESULTS")
    print("=" * 60)
    
    # Check remaining missing values
    missing_after = df[numerical_cols].isna().sum()
    total_missing_after = missing_after.sum()
    
    print(f"Total missing values after filling: {total_missing_after}")
    
    if total_missing_after > 0:
        print("\nColumns with remaining missing values:")
        for col, count in missing_after[missing_after > 0].items():
            print(f"  {col}: {count} missing values")
    else:
        print("[SUCCESS] All missing values successfully filled!")
    
    # Check data types
    print(f"\nData types after filling:")
    for col in numerical_cols[:5]:  # Show first 5 columns
        print(f"  {col}: {df[col].dtype}")
    
    # Sample of filled data
    print(f"\nSample of filled data (first 3 rows):")
    sample_cols = ['station_code', 'year', 'annual_avg_flow_m3s', 'annual_total_m3']
    print(df[sample_cols].head(3).to_string())
    
    # Statistics by station
    print(f"\nData completeness by station:")
    station_completeness = df.groupby('station_code')[numerical_cols].apply(
        lambda x: (1 - x.isna().sum().sum() / (len(x) * len(numerical_cols))) * 100
    ).round(2)
    
    for station, completeness in station_completeness.items():
        print(f"  {station}: {completeness}% complete")

def create_comparison_chart():
    """Create a chart comparing before and after filling"""
    
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Read both datasets
        original = pd.read_csv("dsi_2000_2020_final_structured_STD_CORRECTED.csv")
        filled = pd.read_csv("dsi_2000_2020_final_structured_STD_CORRECTED_FILLED_BY_STATION.csv")
        
        # Calculate missing values
        exclude_cols = ['file', 'station_code', 'station_name', 'coordinates']
        numerical_cols = [col for col in original.columns if col not in exclude_cols]
        
        original_missing = original[numerical_cols].isna().sum()
        filled_missing = filled[numerical_cols].isna().sum()
        
        # Create comparison chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Before filling
        original_missing[original_missing > 0].plot(kind='bar', ax=ax1, color='red', alpha=0.7)
        ax1.set_title('Missing Values Before Filling', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Columns', fontsize=12)
        ax1.set_ylabel('Missing Count', fontsize=12)
        ax1.tick_params(axis='x', rotation=45)
        
        # After filling
        filled_missing[filled_missing > 0].plot(kind='bar', ax=ax2, color='green', alpha=0.7)
        ax2.set_title('Missing Values After Filling', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Columns', fontsize=12)
        ax2.set_ylabel('Missing Count', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('missing_values_filling_comparison.png', dpi=300, bbox_inches='tight')
        print(f"\nComparison chart saved to: missing_values_filling_comparison.png")
        plt.close()
        
    except ImportError:
        print("Matplotlib not available for chart creation")

if __name__ == "__main__":
    print("Filling missing values using station-specific data only...")
    print("Using: dsi_2000_2020_final_structured_STD_CORRECTED.csv")
    
    # Fill missing values
    output_file = fill_missing_values_by_station()
    
    # Create comparison chart
    create_comparison_chart()
    
    print(f"\n[SUCCESS] Missing values filling completed!")
    print(f"Output file: {output_file}")
    print("Method: Station-specific filling (no data mixing between stations)")
