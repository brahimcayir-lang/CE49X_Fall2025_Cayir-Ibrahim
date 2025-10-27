#!/usr/bin/env python3
"""
Remove duplicate 2020 records and keep only those with actual data
"""

import pandas as pd

def remove_duplicates_and_keep_valid():
    csv_path = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_final_structured.csv"
    
    df = pd.read_csv(csv_path)
    print(f"Original CSV has {len(df)} records")
    
    # Get all 2020 data
    df_2020 = df[df['year'] == 2020].copy()
    print(f"2020 records: {len(df_2020)}")
    
    # Remove all 2020 data from main dataframe
    df_clean = df[df['year'] != 2020]
    print(f"Non-2020 records: {len(df_clean)}")
    
    # For each station, keep only the record with the most complete data
    df_2020_clean = []
    
    for station_code in df_2020['station_code'].unique():
        station_records = df_2020[df_2020['station_code'] == station_code]
        
        # Score each record based on completeness
        best_record = None
        best_score = -1
        
        for _, record in station_records.iterrows():
            score = 0
            if pd.notna(record['annual_avg_flow_m3s']):
                score += 1
            if pd.notna(record['annual_total_m3']):
                score += 1
            if pd.notna(record['mm_total']):
                score += 1
            if pd.notna(record['avg_ltsnkm2']):
                score += 1
            
            if score > best_score:
                best_score = score
                best_record = record
        
        if best_record is not None:
            df_2020_clean.append(best_record)
            print(f"  {station_code}: kept record with score {best_score}")
    
    # Create clean 2020 dataframe
    df_2020_final = pd.DataFrame(df_2020_clean)
    
    # Combine with non-2020 data
    df_final = pd.concat([df_clean, df_2020_final], ignore_index=True)
    
    # Save final CSV
    df_final.to_csv(csv_path, index=False)
    
    print(f"\nFINAL RESULT:")
    print(f"Total records: {len(df_final)}")
    print(f"2020 records: {len(df_2020_final)}")
    print(f"2020 records with flow data: {len(df_2020_final[df_2020_final['annual_avg_flow_m3s'].notna()])}")
    
    # Show the final 2020 data
    print(f"\nFinal 2020 data:")
    print(df_2020_final[['station_code', 'page', 'annual_avg_flow_m3s', 'annual_total_m3', 'mm_total', 'avg_ltsnkm2']].to_string())

if __name__ == "__main__":
    remove_duplicates_and_keep_valid()
