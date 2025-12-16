#!/usr/bin/env python3
"""
Check D22A095 2020 data extraction
"""

import pandas as pd

def check_d22a095_data():
    csv_path = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_final_structured.csv"
    
    df = pd.read_csv(csv_path)
    
    # Find D22A095 2020 data
    d22a095_2020 = df[(df['station_code'] == 'D22A095') & (df['year'] == 2020)]
    
    print("D22A095 2020 data:")
    if len(d22a095_2020) > 0:
        row = d22a095_2020.iloc[0]
        print(f"Annual flow: {row['annual_avg_flow_m3s']}")
        print(f"Annual total: {row['annual_total_m3']}")
        print(f"MM total: {row['mm_total']}")
        print(f"Avg LT/SN/Km2: {row['avg_ltsnkm2']}")
        print()
        
        # Check monthly data
        monthly_cols = [col for col in df.columns if 'flow_max_m3' in col]
        print("Monthly flow_max data:")
        print(d22a095_2020[monthly_cols].iloc[0].to_string())
        print()
        
        print("Monthly flow_min data:")
        monthly_cols = [col for col in df.columns if 'flow_min_m3' in col]
        print(d22a095_2020[monthly_cols].iloc[0].to_string())
        print()
        
        print("Monthly flow_avg data:")
        monthly_cols = [col for col in df.columns if 'flow_avg_m3' in col]
        print(d22a095_2020[monthly_cols].iloc[0].to_string())
    else:
        print("D22A095 2020 data not found")

if __name__ == "__main__":
    check_d22a095_data()
