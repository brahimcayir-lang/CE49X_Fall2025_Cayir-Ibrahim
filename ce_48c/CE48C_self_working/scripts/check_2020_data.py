#!/usr/bin/env python3
"""
Check 2020 data in the updated CSV
"""

import pandas as pd

def check_2020_data():
    csv_path = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_final_structured.csv"
    
    df = pd.read_csv(csv_path)
    
    print("2020 data summary:")
    print(f"Total 2020 records: {len(df[df['year'] == 2020])}")
    print(f"2020 records with flow data: {len(df[(df['year'] == 2020) & (df['annual_avg_flow_m3s'].notna())])}")
    print()
    
    print("2020 stations with flow data:")
    flow_2020 = df[(df['year'] == 2020) & (df['annual_avg_flow_m3s'].notna())]
    print(flow_2020[['station_code', 'station_name', 'annual_avg_flow_m3s']].to_string(index=False))
    
    print()
    print("Overall summary:")
    print(f"Total records: {len(df)}")
    print(f"Years covered: {df['year'].min()} - {df['year'].max()}")
    print(f"Unique stations: {df['station_code'].nunique()}")

if __name__ == "__main__":
    check_2020_data()
