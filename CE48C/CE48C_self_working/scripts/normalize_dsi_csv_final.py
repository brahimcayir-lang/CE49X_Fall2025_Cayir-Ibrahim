#!/usr/bin/env python3
"""
Final DSİ CSV Normalizer
Creates the final normalized CSV with English month names and proper column structure
"""

import pandas as pd
import numpy as np

def normalize_dsi_csv_final():
    """Create the final normalized DSİ CSV with English month names and proper structure"""
    
    # Read the improved CSV
    input_path = r'C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_monthly_full_improved.csv'
    output_path = r'C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_final_normalized.csv'
    
    df = pd.read_csv(input_path)
    
    print(f"Original CSV: {len(df)} rows, {len(df.columns)} columns")
    
    # Turkish to English month mapping
    month_mapping = {
        'ekim': 'oct', 'kasım': 'nov', 'aralık': 'dec', 'ocak': 'jan',
        'şubat': 'feb', 'mart': 'mar', 'nisan': 'apr', 'mayıs': 'may',
        'haziran': 'jun', 'temmuz': 'jul', 'ağustos': 'aug', 'eylül': 'sep'
    }
    
    # Chronological order (water year: Oct to Sep)
    chronological_months = ['oct', 'nov', 'dec', 'jan', 'feb', 'mar', 
                           'apr', 'may', 'jun', 'jul', 'aug', 'sep']
    
    # Metrics in order
    metrics = ['flow_max', 'flow_min', 'flow_avg', 'ltsnkm2', 'akim_mm', 'milm3']
    
    # Basic columns (non-monthly)
    basic_cols = [
        'file', 'page', 'year', 'station_code', 'station_name', 'coordinates',
        'catchment_area_km2', 'annual_avg_flow_m3s', 'annual_total_m3', 
        'mm_total', 'avg_ltsnkm2'
    ]
    
    # Create new dataframe with basic columns
    new_df = df[basic_cols].copy()
    
    # Process monthly columns
    monthly_cols = [col for col in df.columns if any(metric in col for metric in metrics)]
    
    print(f"Found {len(monthly_cols)} monthly columns to process")
    
    # Create new column structure
    new_cols = basic_cols.copy()
    
    # Add monthly columns in the target order
    for metric in metrics:
        for month_eng in chronological_months:
            col_name = f'{month_eng}_{metric}_m3'
            new_cols.append(col_name)
            
            # Find corresponding Turkish column
            turkish_month = None
            for tr_month, en_month in month_mapping.items():
                if en_month == month_eng:
                    turkish_month = tr_month
                    break
            
            if turkish_month:
                turkish_col = f'{turkish_month}_{metric}_m3'
                if turkish_col in df.columns:
                    new_df[col_name] = df[turkish_col]
                    print(f"Mapped: {turkish_col} -> {col_name}")
                else:
                    new_df[col_name] = np.nan
                    print(f"Missing: {turkish_col} -> {col_name} (filled with NaN)")
            else:
                new_df[col_name] = np.nan
                print(f"Missing: {col_name} (filled with NaN)")
    
    # Reorder columns to match target structure
    new_df = new_df[new_cols]
    
    # Save the normalized CSV
    new_df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"\n[OK] Normalized CSV created: {output_path}")
    print(f"New structure: {len(new_df)} rows, {len(new_df.columns)} columns")
    print(f"Columns: {len(basic_cols)} basic + {len(chronological_months) * len(metrics)} monthly")
    
    # Verify structure
    print("\nColumn structure verification:")
    print("Basic columns (1-11):")
    for i, col in enumerate(new_cols[:11]):
        print(f"  {i+1:2d}. {col}")
    
    print("\nMonthly columns by metric type:")
    start_idx = 11
    for i, metric in enumerate(metrics):
        print(f"\n{metric.upper()} ({len(chronological_months)} months):")
        for j, month in enumerate(chronological_months):
            col_idx = start_idx + i * len(chronological_months) + j
            col_name = f'{month}_{metric}_m3'
            print(f"  {col_idx+1:2d}. {col_name}")
    
    # Count non-null values
    print("\nData completeness:")
    for metric in metrics:
        metric_cols = [col for col in new_cols if col.endswith(f'_{metric}_m3')]
        non_null_count = new_df[metric_cols].notna().sum().sum()
        print(f"{metric}: {non_null_count} non-null values across {len(metric_cols)} columns")
    
    return new_df

if __name__ == "__main__":
    df_normalized = normalize_dsi_csv_final()
