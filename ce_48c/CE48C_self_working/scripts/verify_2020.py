#!/usr/bin/env python3
"""
Final verification of 2020 data
"""

import pandas as pd

def verify_2020_data():
    csv_path = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_final_structured.csv"
    
    df = pd.read_csv(csv_path)
    
    print("FINAL VERIFICATION - 2020 data only:")
    df_2020 = df[df['year'] == 2020]
    print(df_2020[['station_code', 'page', 'annual_avg_flow_m3s', 'annual_total_m3', 'mm_total', 'avg_ltsnkm2']].to_string())
    
    print(f'\nTotal 2020 records: {len(df_2020)}')
    print(f'2020 records with flow data: {len(df_2020[df_2020["annual_avg_flow_m3s"].notna()])}')
    print(f'2020 records with annual total: {len(df_2020[df_2020["annual_total_m3"].notna()])}')
    print(f'2020 records with MM total: {len(df_2020[df_2020["mm_total"].notna()])}')
    print(f'2020 records with avg LT/SN/Km2: {len(df_2020[df_2020["avg_ltsnkm2"].notna()])}')
    
    # Check for duplicates
    duplicates = df_2020.duplicated(subset=['station_code', 'page'], keep=False)
    if duplicates.any():
        print(f"\nWARNING: Found {duplicates.sum()} duplicate records!")
        print(df_2020[duplicates][['station_code', 'page']].to_string())
    else:
        print("\n✅ No duplicate records found!")

if __name__ == "__main__":
    verify_2020_data()
