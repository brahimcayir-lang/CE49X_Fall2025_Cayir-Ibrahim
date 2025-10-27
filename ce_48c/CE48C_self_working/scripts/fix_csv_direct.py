#!/usr/bin/env python3
"""
Fix the CSV file with correct 2020 data from terminal output
"""

import pandas as pd

def fix_csv_with_correct_data():
    csv_path = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_final_structured.csv"
    
    # Read the current CSV
    df = pd.read_csv(csv_path)
    print(f"Current CSV has {len(df)} records")
    
    # Correct 2020 data based on terminal output
    correct_2020_data = {
        'D14A011': {'page': 462, 'annual_avg_flow_m3s': 2.097, 'annual_total_m3': 66.32, 'mm_total': 457.0, 'avg_ltsnkm2': 14.5},
        'D14A117': {'page': 475, 'annual_avg_flow_m3s': 0.314, 'annual_total_m3': 9.91, 'mm_total': 127.0, 'avg_ltsnkm2': 4.0},
        'D14A144': {'page': 482, 'annual_avg_flow_m3s': 0.127, 'annual_total_m3': 4.02, 'mm_total': 245.0, 'avg_ltsnkm2': 7.8},
        'D14A146': {'page': 483, 'annual_avg_flow_m3s': 0.154, 'annual_total_m3': 4.87, 'mm_total': 230.0, 'avg_ltsnkm2': 7.3},
        'D14A149': {'page': 484, 'annual_avg_flow_m3s': 0.151, 'annual_total_m3': 4.79, 'mm_total': 108.0, 'avg_ltsnkm2': 3.4},
        'D14A162': {'page': 486, 'annual_avg_flow_m3s': 6.783, 'annual_total_m3': 214.45, 'mm_total': 301.0, 'avg_ltsnkm2': 9.5},
        'D14A172': {'page': 489, 'annual_avg_flow_m3s': 50.962, 'annual_total_m3': 1612.10, 'mm_total': 151.0, 'avg_ltsnkm2': 4.8},
        'D14A192': {'page': 504, 'annual_avg_flow_m3s': 64.762, 'annual_total_m3': 2047.00, 'mm_total': 189.0, 'avg_ltsnkm2': 6.0},
        'D22A093': {'page': 863, 'annual_avg_flow_m3s': 4.711, 'annual_total_m3': 149.05, 'mm_total': 710.0, 'avg_ltsnkm2': 22.4},
        'D22A095': {'page': 864, 'annual_avg_flow_m3s': 1.040, 'annual_total_m3': 32.93, 'mm_total': 299.0, 'avg_ltsnkm2': 9.5},
        'D22A105': {'page': 868, 'annual_avg_flow_m3s': 2.262, 'annual_total_m3': 71.60, 'mm_total': 961.0, 'avg_ltsnkm2': 30.4},
        'D22A106': {'page': 869, 'annual_avg_flow_m3s': 2.893, 'annual_total_m3': 91.60, 'mm_total': 751.0, 'avg_ltsnkm2': 23.7},
        'D22A116': {'page': 874, 'annual_avg_flow_m3s': None, 'annual_total_m3': None, 'mm_total': None, 'avg_ltsnkm2': None},
        'D22A158': {'page': 900, 'annual_avg_flow_m3s': 4.380, 'annual_total_m3': 138.47, 'mm_total': 505.0, 'avg_ltsnkm2': 16.0},
        'E22A054': {'page': 909, 'annual_avg_flow_m3s': 5.597, 'annual_total_m3': 177.03, 'mm_total': 797.0, 'avg_ltsnkm2': 25.2},
        'E22A065': {'page': 913, 'annual_avg_flow_m3s': 5.005, 'annual_total_m3': 158.30, 'mm_total': 410.0, 'avg_ltsnkm2': 13.0}
    }
    
    # Update 2020 records with correct data
    for station_code, correct_data in correct_2020_data.items():
        # Find the 2020 record for this station
        mask = (df['year'] == 2020) & (df['station_code'] == station_code)
        if mask.any():
            # Update the record
            df.loc[mask, 'annual_avg_flow_m3s'] = correct_data['annual_avg_flow_m3s']
            df.loc[mask, 'annual_total_m3'] = correct_data['annual_total_m3']
            df.loc[mask, 'mm_total'] = correct_data['mm_total']
            df.loc[mask, 'avg_ltsnkm2'] = correct_data['avg_ltsnkm2']
            print(f"Updated {station_code}: annual_total_m3={correct_data['annual_total_m3']}, mm_total={correct_data['mm_total']}, avg_ltsnkm2={correct_data['avg_ltsnkm2']}")
    
    # Save the corrected CSV
    df.to_csv(csv_path, index=False)
    print(f"\nCSV file updated and saved!")
    
    # Verify the changes
    print(f"\nVerification - 2020 data:")
    df_2020 = df[df['year'] == 2020]
    print(df_2020[['station_code', 'page', 'annual_avg_flow_m3s', 'annual_total_m3', 'mm_total', 'avg_ltsnkm2']].to_string())

if __name__ == "__main__":
    fix_csv_with_correct_data()
