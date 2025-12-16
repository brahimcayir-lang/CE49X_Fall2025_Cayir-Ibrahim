"""
Calculate distances of DSI stations from a reference coordinate.
Author: Ibrahim Çayır
"""

import pandas as pd
import re
from math import radians, sin, cos, sqrt, atan2

# ==========================================================
# 1. File path and reference coordinate
# ==========================================================
INPUT_FILE = "extracted_coordinates_dsi_2020.csv"
OUTPUT_FILE = "stations_with_distances.csv"

# Reference coordinate (decimal degrees)
REF_LAT = 40.74878   # 40°44′55.61″ K
REF_LON = 37.44946   # 37°26′58.06″ D

# ==========================================================
# 2. Function: Convert DMS string (e.g. "36°1'14'' Doğu - 40°55'13'' Kuzey") to decimal
# ==========================================================
def dms_to_decimal(coord_str):
    """Extract DMS parts and convert to decimal degrees."""
    try:
        parts = re.findall(r"(\d+)°(\d+)'([\d\.]+)\"*\s*([A-Za-zÇçĞğİıÖöŞşÜü]+)", coord_str)
        if len(parts) != 2:
            return None, None

        lon_deg, lon_min, lon_sec, lon_dir = parts[0]
        lat_deg, lat_min, lat_sec, lat_dir = parts[1]

        lon = float(lon_deg) + float(lon_min)/60 + float(lon_sec)/3600
        lat = float(lat_deg) + float(lat_min)/60 + float(lat_sec)/3600

        # Direction corrections
        if "Güney" in lat_dir:
            lat = -lat
        if "Batı" in lon_dir:
            lon = -lon

        return lat, lon
    except Exception:
        return None, None

# ==========================================================
# 3. Haversine distance (in km)
# ==========================================================
def haversine(lat1, lon1, lat2, lon2):
    """Compute great-circle distance between two coordinates."""
    if None in (lat1, lon1, lat2, lon2):
        return None
    R = 6371  # Earth's radius (km)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))

# ==========================================================
# 4. Load CSV and compute distances
# ==========================================================
df = pd.read_csv(INPUT_FILE, encoding="utf-8")

# Extract latitude & longitude
df[["latitude", "longitude"]] = df["coordinates"].apply(lambda x: pd.Series(dms_to_decimal(str(x))))

# Compute distance
df["distance_km"] = df.apply(
    lambda row: haversine(REF_LAT, REF_LON, row["latitude"], row["longitude"]),
    axis=1
)

# ==========================================================
# 5. Save new CSV
# ==========================================================
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

print(f"✅ Successfully processed {len(df)} stations")
print(f"📁 Output saved to: {OUTPUT_FILE}")
print(f"📍 Reference point: {REF_LAT}°N, {REF_LON}°E")

# Display some statistics
valid_distances = df["distance_km"].dropna()
if len(valid_distances) > 0:
    print(f"📊 Distance statistics:")
    print(f"   • Closest station: {valid_distances.min():.2f} km")
    print(f"   • Farthest station: {valid_distances.max():.2f} km")
    print(f"   • Average distance: {valid_distances.mean():.2f} km")
