#!/usr/bin/env python3
"""
Improved 2020 DSİ hydrological data extraction
"""

import os
import fitz  # PyMuPDF
import pandas as pd
import re
from pathlib import Path

def extract_2020_data_improved():
    """Extract 2020 data with improved parsing"""
    pdf_path = r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi\dsi_2020.pdf"
    
    # Target stations
    target_stations = {
        'D14A011', 'D14A117', 'D14A144', 'D14A146', 'D14A149', 'D14A162',
        'D14A172', 'D14A192', 'D14A018', 'D22A093', 'D22A095', 'D22A105',
        'D22A106', 'D22A158', 'E22A054', 'D22A116', 'E22A065'
    }
    
    doc = fitz.open(pdf_path)
    extracted_data = []
    
    print("Extracting 2020 data with improved parsing...")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # Look for station codes
        for station_code in target_stations:
            if station_code in text:
                print(f"Processing station {station_code} on page {page_num + 1}")
                
                # Extract data for this station
                station_data = extract_station_data_improved(text, station_code, page_num + 1)
                if station_data:
                    extracted_data.append(station_data)
                    print(f"  [OK] Extracted: {station_data['station_name']}")
                    if station_data['annual_avg_flow_m3s']:
                        print(f"    Annual flow: {station_data['annual_avg_flow_m3s']} m³/s")
    
    doc.close()
    return extracted_data

def extract_station_data_improved(text, station_code, page_num):
    """Extract data for a specific station with improved parsing"""
    lines = text.split('\n')
    
    # Find the line with the station
    station_line_idx = None
    station_name = None
    
    for i, line in enumerate(lines):
        if station_code in line:
            station_line_idx = i
            # Extract station name (text after station code)
            station_name = line.replace(station_code, '').strip()
            # Clean up the name
            station_name = re.sub(r'\s+', ' ', station_name).strip()
            break
    
    if station_line_idx is None:
        return None
    
    # Look for coordinates in nearby lines
    coordinates = None
    for i in range(max(0, station_line_idx - 10), min(len(lines), station_line_idx + 15)):
        line = lines[i]
        if '°' in line and ('Doğu' in line or 'Kuzey' in line or 'Batı' in line or 'Güney' in line):
            coordinates = line.strip()
            break
    
    # Look for catchment area
    catchment_area = None
    for i in range(max(0, station_line_idx - 10), min(len(lines), station_line_idx + 15)):
        line = lines[i]
        if 'YAĞIŞ ALANI' in line or 'km²' in line:
            # Extract number before km²
            numbers = re.findall(r'(\d+[.,]\d+|\d+)', line)
            if numbers:
                catchment_area = float(numbers[0].replace(',', '.'))
            break
    
    # Look for annual average flow - try multiple patterns
    annual_avg_flow = None
    for i in range(max(0, station_line_idx - 10), min(len(lines), station_line_idx + 15)):
        line = lines[i]
        # Look for patterns like "Su Yılında ... m3/sn"
        if 'm3/sn' in line or 'm³/s' in line or 'm3/s' in line:
            # Extract number before m3/sn
            numbers = re.findall(r'(\d+[.,]\d+|\d+)', line)
            if numbers:
                annual_avg_flow = float(numbers[0].replace(',', '.'))
                break
    
    # Look for annual total
    annual_total = None
    for i in range(max(0, station_line_idx - 10), min(len(lines), station_line_idx + 15)):
        line = lines[i]
        if 'MİLYON M3' in line or 'MİL. M3' in line:
            # Extract number before MİLYON M3
            numbers = re.findall(r'(\d+[.,]\d+|\d+)', line)
            if numbers:
                annual_total = float(numbers[0].replace(',', '.'))
            break
    
    # Look for mm total
    mm_total = None
    for i in range(max(0, station_line_idx - 10), min(len(lines), station_line_idx + 15)):
        line = lines[i]
        if 'MM.' in line and 'SU YILI' in line:
            # Extract number before MM.
            numbers = re.findall(r'(\d+[.,]\d+|\d+)', line)
            if numbers:
                mm_total = float(numbers[0].replace(',', '.'))
            break
    
    # Look for avg ltsnkm2
    avg_ltsnkm2 = None
    for i in range(max(0, station_line_idx - 10), min(len(lines), station_line_idx + 15)):
        line = lines[i]
        if 'LT/SN/Km2' in line and 'SU YILI' in line:
            # Extract number before LT/SN/Km2
            numbers = re.findall(r'(\d+[.,]\d+|\d+)', line)
            if numbers:
                avg_ltsnkm2 = float(numbers[0].replace(',', '.'))
            break
    
    # Look for monthly data
    monthly_data = extract_monthly_data_improved(text, station_line_idx)
    
    return {
        'file': 'dsi_2020.pdf',
        'page': page_num,
        'year': 2020,
        'station_code': station_code,
        'station_name': station_name,
        'coordinates': coordinates,
        'catchment_area_km2': catchment_area,
        'annual_avg_flow_m3s': annual_avg_flow,
        'annual_total_m3': annual_total,
        'mm_total': mm_total,
        'avg_ltsnkm2': avg_ltsnkm2,
        **monthly_data
    }

def extract_monthly_data_improved(text, station_line_idx):
    """Extract monthly data with improved parsing"""
    lines = text.split('\n')
    
    # Look for the data section - find lines with numeric data
    monthly_data = {}
    
    # Look for the 6 metric lines in a broader range
    metrics = ['Maks.', 'Min.', 'Ortalama', 'LT/SN/Km2', 'AKIM mm.', 'MİL. M3']
    
    for i in range(max(0, station_line_idx - 5), min(len(lines), station_line_idx + 30)):
        line = lines[i].strip()
        
        for metric in metrics:
            if line.startswith(metric):
                # Extract 12 numeric values
                numbers = re.findall(r'(\d+[.,]\d+|\d+)', line)
                if len(numbers) >= 12:
                    # Map to months (Oct-Sep order)
                    months = ['oct', 'nov', 'dec', 'jan', 'feb', 'mar', 
                             'apr', 'may', 'jun', 'jul', 'aug', 'sep']
                    
                    metric_prefix = metric.lower().replace('.', '').replace('/', '').replace(' ', '_')
                    if metric_prefix == 'maks':
                        metric_prefix = 'flow_max'
                    elif metric_prefix == 'min':
                        metric_prefix = 'flow_min'
                    elif metric_prefix == 'ortalama':
                        metric_prefix = 'flow_avg'
                    elif metric_prefix == 'ltsnkm2':
                        metric_prefix = 'ltsnkm2'
                    elif metric_prefix == 'akim_mm':
                        metric_prefix = 'akim_mm'
                    elif metric_prefix == 'mil_m3':
                        metric_prefix = 'milm3'
                    
                    for j, month in enumerate(months):
                        if j < len(numbers):
                            col_name = f"{month}_{metric_prefix}_m3"
                            monthly_data[col_name] = float(numbers[j].replace(',', '.'))
                break
    
    return monthly_data

def update_csv_with_improved_2020_data():
    """Update CSV with improved 2020 data"""
    csv_path = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_final_structured.csv"
    
    # Extract improved data
    extracted_data = extract_2020_data_improved()
    
    if not extracted_data:
        print("No data extracted")
        return
    
    # Read existing data
    existing_df = pd.read_csv(csv_path)
    
    # Remove existing 2020 data
    existing_df = existing_df[existing_df['year'] != 2020]
    
    # Create DataFrame from extracted data
    new_df = pd.DataFrame(extracted_data)
    
    # Ensure all columns exist
    for col in existing_df.columns:
        if col not in new_df.columns:
            new_df[col] = None
    
    # Reorder columns to match existing structure
    new_df = new_df[existing_df.columns]
    
    # Combine dataframes
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    # Save updated CSV
    combined_df.to_csv(csv_path, index=False)
    
    print(f"\nUpdated CSV with {len(extracted_data)} improved 2020 records")
    print(f"Total records: {len(combined_df)}")
    
    # Show summary of extracted data
    stations_with_flow = [d for d in extracted_data if d['annual_avg_flow_m3s'] is not None]
    print(f"Stations with flow data: {len(stations_with_flow)}")
    
    if stations_with_flow:
        print("\nStations with annual flow data:")
        for data in stations_with_flow:
            print(f"  {data['station_code']}: {data['annual_avg_flow_m3s']} m³/s")
    
    return combined_df

def main():
    update_csv_with_improved_2020_data()

if __name__ == "__main__":
    main()
