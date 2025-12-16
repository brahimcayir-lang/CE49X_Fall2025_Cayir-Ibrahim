# -*- coding: utf-8 -*-
"""
Create a readable table for stations with name, code, region, coordinates, and observation period
from dsi_final_distance_lt_84.csv
"""

import pandas as pd
from pathlib import Path

def create_stations_table():
    """Create a readable table of station information."""
    
    input_file = Path(__file__).parent / "dsi_final_distance_lt_84.csv"
    output_file = Path(__file__).parent / "stations_info_table.csv"
    
    print(f"Reading {input_file.name}...")
    df = pd.read_csv(input_file)
    
    # Group by station to get unique stations and calculate observation period
    stations_data = []
    
    for station_code in df['station_code'].unique():
        station_df = df[df['station_code'] == station_code]
        
        # Get station info (should be same for all years)
        station_name = station_df['station_name'].iloc[0]
        region = station_df['region'].iloc[0]
        coordinates = station_df['coordinates'].iloc[0]
        
        # Calculate observation period
        min_year = station_df['year'].min()
        max_year = station_df['year'].max()
        
        # Format observation period
        if min_year == max_year:
            obs_period = str(min_year)
        else:
            obs_period = f"{int(min_year)}-{int(max_year)}"
        
        stations_data.append({
            'Station Code': station_code,
            'Station Name': station_name,
            'Region': region,
            'Coordinates': coordinates,
            'Observation Period': obs_period,
            'Min Year': int(min_year),
            'Max Year': int(max_year),
            'Years of Data': int(max_year - min_year + 1)
        })
    
    # Create DataFrame and sort by station code
    stations_df = pd.DataFrame(stations_data)
    stations_df = stations_df.sort_values('Station Code').reset_index(drop=True)
    
    # Reorder columns for the main table
    main_columns = ['Station Code', 'Station Name', 'Region', 'Coordinates', 'Observation Period']
    stations_table = stations_df[main_columns].copy()
    
    # Save to CSV
    stations_table.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n[SUCCESS] Created stations table: {output_file.name}")
    print(f"  Total stations: {len(stations_table)}")
    print(f"\nFirst 10 stations:")
    print("-" * 100)
    print(stations_table.head(10).to_string(index=False))
    
    # Also create a summary
    summary_file = Path(__file__).parent / "stations_info_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("STATIONS INFORMATION TABLE\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"Total number of stations: {len(stations_table)}\n")
        f.write(f"Observation period range: {stations_df['Min Year'].min()}-{stations_df['Max Year'].max()}\n\n")
        f.write("\nDETAILED STATION INFORMATION\n")
        f.write("-" * 100 + "\n\n")
        
        for idx, row in stations_table.iterrows():
            f.write(f"{idx + 1}. {row['Station Code']} - {row['Station Name']}\n")
            f.write(f"   Region: {row['Region']}\n")
            f.write(f"   Coordinates: {row['Coordinates']}\n")
            f.write(f"   Observation Period: {row['Observation Period']}\n")
            f.write("\n")
    
    print(f"\n[SUCCESS] Created summary file: {summary_file.name}")
    
    return stations_table

if __name__ == "__main__":
    create_stations_table()

