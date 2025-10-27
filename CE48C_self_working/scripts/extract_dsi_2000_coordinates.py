#!/usr/bin/env python3
"""
Fast DSI 2000 PDF Coordinate Extractor
Extracts station coordinates from DSI 2000 PDF and appends to existing CSV
Only processes regions 14 and 22, skips everything else for efficiency
"""

import pdfplumber
import csv
import re
import os
from pathlib import Path

def is_target_region(line):
    """Check if line contains target regions (14 or 22) - must start with number and dot"""
    # More flexible pattern to catch variations like "14.YEŞİLIRMAK HAVZASI" or "14.KM'DEDİR."
    match = re.match(r'^(14|22)\.', line.strip())
    if match:
        # Only accept if it contains "HAVZASI" or "HAVZASI" to avoid false matches
        return "HAVZASI" in line.upper()
    return False

def extract_station_info(line):
    """Extract station code and name from line"""
    # Pattern: D14A011 LADİK G. REG. ÇIKIŞI
    match = re.match(r'^([DE]\d{2}[A-Z]\d{3})\s+(.+)$', line.strip())
    if match:
        return match.group(1), match.group(2)
    return None, None

def extract_coordinates(line):
    """Extract coordinates from line"""
    # Pattern: 36°1'14" Doğu - 40°55'13" Kuzey
    coord_pattern = r'(\d+°\d+\'\d+")\s+Doğu\s+-\s+(\d+°\d+\'\d+")\s+Kuzey'
    match = re.search(coord_pattern, line)
    if match:
        return f"{match.group(1)} Doğu - {match.group(2)} Kuzey"
    return None

def process_pdf(pdf_path, output_csv):
    """Process PDF and extract coordinates for target regions"""
    
    # Read existing stations to avoid duplicates
    existing_stations = set()
    if os.path.exists(output_csv):
        with open(output_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 4:
                    existing_stations.add(row[3])  # station_code
    
    new_stations = []
    pdf_name = os.path.basename(pdf_path)
    
    print(f"Processing {pdf_name}...")
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text:
                continue
                
            lines = text.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Check if this is a target region (must start with 14. or 22.)
                if is_target_region(line):
                    region = line
                    print(f"Found region: {region}")
                    
                    # Check line 2 (i + 1) for station info
                    if i + 1 < len(lines):
                        station_line = lines[i + 1].strip()
                        print(f"  Checking station line: '{station_line}'")
                        station_code, station_name = extract_station_info(station_line)
                        
                        if station_code and station_name:
                            print(f"  Found station: {station_code} - {station_name}")
                            # Skip if station already exists
                            if station_code in existing_stations:
                                print(f"Skipping existing station: {station_code}")
                                i += 5  # Skip to next potential region
                                continue
                                
                            # Check line 5 (i + 4) for coordinates - SKIP lines 3 and 4
                            if i + 4 < len(lines):
                                coord_line = lines[i + 4].strip()
                                print(f"  Checking coord line: '{coord_line}'")
                                coordinates = extract_coordinates(coord_line)
                                
                                if coordinates:
                                    new_stations.append({
                                        'file_name': pdf_name,
                                        'page': page_num,
                                        'region': region,
                                        'station_code': station_code,
                                        'station_name': station_name,
                                        'coordinates': coordinates
                                    })
                                    print(f"Found new station: {station_code} - {station_name}")
                                    print(f"  Coordinates: {coordinates}")
                                    i += 5  # Move to next potential region
                                    continue
                                else:
                                    print(f"No coordinates found for {station_code}")
                        else:
                            print(f"  No station info found in line: '{station_line}'")
                    
                    i += 5  # Skip to next potential region
                else:
                    i += 1
    
    # Append new stations to CSV
    if new_stations:
        file_exists = os.path.exists(output_csv)
        with open(output_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header if file doesn't exist
            if not file_exists:
                writer.writerow(['file_name', 'page', 'region', 'station_code', 'station_name', 'coordinates'])
            
            # Write new stations
            for station in new_stations:
                writer.writerow([
                    station['file_name'],
                    station['page'],
                    station['region'],
                    station['station_code'],
                    station['station_name'],
                    station['coordinates']
                ])
        
        print(f"\nAdded {len(new_stations)} new stations to {output_csv}")
        for station in new_stations:
            print(f"  - {station['station_code']}: {station['station_name']}")
    else:
        print("No new stations found.")

def main():
    pdf_path = r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi\dsi_2000.pdf"
    output_csv = "extracted_coordinates_dsi_2020.csv"
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return
    
    process_pdf(pdf_path, output_csv)

if __name__ == "__main__":
    main()
