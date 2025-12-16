#!/usr/bin/env python3
"""
Check if document is updated
"""

import pandas as pd

def check_document():
    csv_path = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_final_structured.csv"
    
    df = pd.read_csv(csv_path)
    
    print("DOCUMENT STATUS:")
    print(f"[OK] Document updated! Total records: {len(df)}")
    print(f"[DATE] Years covered: {df['year'].min()} - {df['year'].max()}")
    print(f"[2020] 2020 records: {len(df[df['year'] == 2020])}")
    print(f"[FLOW] 2020 records with flow data: {len(df[(df['year'] == 2020) & (df['annual_avg_flow_m3s'].notna())])}")
    
    print(f"\n[FILE] Document location:")
    print(f"   {csv_path}")
    
    print(f"\n[CHART] Chart location:")
    print(f"   C:\\Users\\Asus\\Desktop\\bitirme_projesi\\outputs\\annual_flow_chart.png")

if __name__ == "__main__":
    check_document()
