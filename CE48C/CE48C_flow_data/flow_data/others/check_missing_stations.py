import pandas as pd
from pathlib import Path
import glob

# Target stations from testt.py
TARGET_STATIONS = {
    "E22A065","E22A066","D22A093","E22A071","D14A185","E22A054","E22A063",
    "E14A018","D14A162","D14A186","D22A105","E22A053","D14A172","D14A117",
    "E14A027","D22A106","D14A200","E14A002","D14A179","D22A098","D22A159",
    "D14A064","E14A038","D14A201","D14A184","D14A211","D14A208","D14A214",
    "D14A207","D14A141","E22A062","E14A040","D14A215","D14A176","D14A011",
    "D14A188","D14A081"
}

# Find all CSV files
csv_files = sorted(glob.glob("flow_data_m3sn/dsi_*_avg_flows_filtered.csv"))

print(f"Total target stations: {len(TARGET_STATIONS)}")
print("\nChecking for missing stations in each year:\n")

missing_info = {}

for csv_file in csv_files:
    year = Path(csv_file).stem.replace("dsi_", "").replace("_avg_flows_filtered", "")
    df = pd.read_csv(csv_file)
    stations_found = set(df['station_code'].unique())
    missing_stations = TARGET_STATIONS - stations_found
    
    missing_info[year] = {
        'found': len(stations_found),
        'missing': missing_stations,
        'missing_count': len(missing_stations)
    }
    
    if missing_stations:
        print(f"{year}: Found {len(stations_found)}/{len(TARGET_STATIONS)} stations - MISSING: {sorted(missing_stations)}")
    else:
        print(f"{year}: Found {len(stations_found)}/{len(TARGET_STATIONS)} stations - COMPLETE")

print("\nSummary:")
print("-" * 60)
for year in sorted(missing_info.keys()):
    info = missing_info[year]
    if info['missing_count'] > 0:
        print(f"{year}: {info['found']} stations, {info['missing_count']} missing")
