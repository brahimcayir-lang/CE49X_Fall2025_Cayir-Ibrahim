#!/usr/bin/env python3
"""
Extract Only 9 Missing Stations from DSİ Annual Report PDFs (2000-2020)

This script extracts data for the 9 missing stations:
D14A011, D14A117, D14A144, D14A146, D14A149, D14A018, D22A106, E22A054, D22A116

And merges them with the existing dsi_2000_2020_final.csv dataset.
"""

import os
import re
import pandas as pd
import pdfplumber
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration
PDF_FOLDER = r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi"
EXISTING_CSV = "dsi_2000_2020_final.csv"
OUTPUT_CSV = "dsi_2000_2020_final_extended.csv"

# Stations to extract (9 missing stations)
TARGET_STATIONS = [
    "D14A011", "D14A117", "D14A144", "D14A146", "D14A149", 
    "D14A018", "D22A106", "E22A054", "D22A116"
]

# Already existing stations (skip these)
EXISTING_STATIONS = [
    "D14A162", "D14A172", "D14A192", "D22A093", "D22A095", 
    "D22A105", "D22A158", "E22A065"
]

# Month order for Turkish months
MONTH_ORDER = [
    "Ekim", "Kasım", "Aralık", "Ocak", "Şubat", "Mart", 
    "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül"
]

def normalize_number(text):
    """Normalize Turkish number format (comma to dot) and convert to float."""
    if not text or text.strip() == '':
        return None
    try:
        # Replace comma with dot for decimal separator
        normalized = str(text).replace(',', '.')
        # Remove any non-numeric characters except dots and minus signs
        cleaned = re.sub(r'[^\d\.\-]', '', normalized)
        if cleaned == '' or cleaned == '.':
            return None
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def extract_station_codes(text):
    """Extract station codes using regex pattern."""
    pattern = r"[A-Z]\d{2}[A-Z]\d{3}"
    return re.findall(pattern, text)

def find_data_table_lines(text_lines):
    """Find lines that contain data tables for hydrological measurements."""
    data_lines = []
    for i, line in enumerate(text_lines):
        line_clean = line.strip()
        # Look for lines that contain multiple numeric values (potential data rows)
        numbers = re.findall(r'[\d.,]+', line_clean)
        if len(numbers) >= 10:  # At least 10 numeric values suggests a data row
            data_lines.append((i, line_clean))
    return data_lines

def extract_monthly_data(line, month_order):
    """Extract monthly data from a line containing 12 monthly values."""
    # Find all numeric values in the line
    numbers = re.findall(r'[\d.,]+', line)
    
    if len(numbers) >= 12:
        # Take the first 12 numbers as monthly values
        monthly_values = []
        for num in numbers[:12]:
            normalized = normalize_number(num)
            monthly_values.append(normalized)
        
        # Create dictionary with month names
        monthly_data = {}
        for i, month in enumerate(month_order):
            if i < len(monthly_values):
                monthly_data[f"flow_{month.lower()}_m3s"] = monthly_values[i]
            else:
                monthly_data[f"flow_{month.lower()}_m3s"] = None
        
        return monthly_data
    return {}

def extract_station_data_from_page(page_text, station_code, year):
    """Extract station data from a single page."""
    lines = page_text.split('\n')
    
    # Find station code in the text
    station_found = False
    station_name = ""
    coordinates = ""
    catchment_area = None
    
    # Look for station information
    for i, line in enumerate(lines):
        if station_code in line:
            station_found = True
            # Extract station name (usually follows the station code)
            name_match = re.search(rf'{station_code}[^\d]*([A-Za-zÇĞİÖŞÜçğıöşü\s]+)', line)
            if name_match:
                station_name = name_match.group(1).strip()
            
            # Look for coordinates and catchment area in nearby lines
            for j in range(max(0, i-3), min(len(lines), i+10)):
                nearby_line = lines[j]
                
                # Look for coordinates pattern
                coord_match = re.search(r'(\d+°\d+[\'"]?\d*[\'"]?\s*[NSEW])', nearby_line)
                if coord_match and not coordinates:
                    coordinates = coord_match.group(1)
                
                # Look for catchment area
                area_match = re.search(r'(\d+[.,]\d+)\s*km²', nearby_line)
                if area_match and catchment_area is None:
                    catchment_area = normalize_number(area_match.group(1))
    
    if not station_found:
        return None
    
    # Find data tables
    data_lines = find_data_table_lines(lines)
    
    # Extract annual totals and monthly data
    annual_total_m3_million = None
    annual_mm = None
    annual_lps_km2 = None
    
    monthly_flow_data = {}
    monthly_ltsnkm2_data = {}
    monthly_mm_akim_data = {}
    monthly_mil_m3_data = {}
    
    # Process data lines to find the "Ortalama" (average) row
    for line_idx, line in data_lines:
        line_lower = line.lower()
        
        # Look for the average row
        if 'ortalama' in line_lower or 'average' in line_lower:
            numbers = re.findall(r'[\d.,]+', line)
            
            if len(numbers) >= 12:
                # Extract monthly flow data
                monthly_flow_data = extract_monthly_data(line, MONTH_ORDER)
                
                # Calculate annual average flow
                flow_values = [v for v in monthly_flow_data.values() if v is not None]
                if flow_values:
                    annual_avg_flow = sum(flow_values) / len(flow_values)
                else:
                    annual_avg_flow = None
            else:
                annual_avg_flow = None
        else:
            # Look for annual totals in other lines
            numbers = re.findall(r'[\d.,]+', line)
            if len(numbers) >= 3:
                # Try to identify annual totals
                for num_str in numbers:
                    num_val = normalize_number(num_str)
                    if num_val and num_val > 10:  # Likely annual total
                        if annual_total_m3_million is None:
                            annual_total_m3_million = num_val
                        elif annual_mm is None:
                            annual_mm = num_val
                        elif annual_lps_km2 is None:
                            annual_lps_km2 = num_val
    
    # Create the data record
    record = {
        'file': f'dsi_{year}.pdf',
        'page': 0,  # Will be updated when we know the actual page
        'year': year,
        'station_code': station_code,
        'station_name': station_name,
        'coordinates': coordinates,
        'catchment_area_km2': catchment_area,
        'annual_total_m3_million': annual_total_m3_million,
        'annual_mm': annual_mm,
        'annual_lps_km2': annual_lps_km2,
        'flow_avg_annual_m3s': annual_avg_flow,
    }
    
    # Add monthly flow data
    record.update(monthly_flow_data)
    
    # Add empty columns for LT/SN/Km2, AKIM mm., and MİL. M3 (as per requirements)
    for month in MONTH_ORDER:
        record[f'ltsnkm2_{month}'] = None
        record[f'mm_akim_{month}'] = None
        record[f'mil_m3_{month}'] = None
    
    # Add average columns
    record['ltsnkm2_average'] = None
    record['mm_akim_annual_average'] = None
    record['mil_m3_annual_average'] = None
    
    return record

def process_pdf_file(pdf_path, target_stations):
    """Process a single PDF file and extract data for target stations."""
    extracted_data = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            year = int(pdf_path.stem.split('_')[1])  # Extract year from filename
            
            print(f"Processing {pdf_path.name} (Year: {year})...")
            
            for page_num, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if not page_text:
                        continue
                    
                    # Extract station codes from this page
                    station_codes = extract_station_codes(page_text)
                    
                    # Check if any target stations are on this page
                    found_stations = [code for code in station_codes if code in target_stations]
                    
                    if found_stations:
                        print(f"  Page {page_num + 1}: Found stations {found_stations}")
                        
                        for station_code in found_stations:
                            station_data = extract_station_data_from_page(page_text, station_code, year)
                            if station_data:
                                station_data['page'] = page_num + 1
                                extracted_data.append(station_data)
                                print(f"    Extracted data for {station_code}")
                
                except Exception as e:
                    print(f"  Error processing page {page_num + 1}: {e}")
                    continue
    
    except Exception as e:
        print(f"Error processing {pdf_path.name}: {e}")
    
    return extracted_data

def main():
    """Main function to extract missing stations and merge with existing data."""
    print("Cursor Prompt - Extract Only 9 Missing Stations")
    print("=" * 60)
    
    # Check if PDF folder exists
    pdf_folder = Path(PDF_FOLDER)
    if not pdf_folder.exists():
        print(f"ERROR: PDF folder not found: {PDF_FOLDER}")
        return
    
    # Check if existing CSV exists
    if not os.path.exists(EXISTING_CSV):
        print(f"ERROR: Existing CSV not found: {EXISTING_CSV}")
        return
    
    print(f"PDF Folder: {PDF_FOLDER}")
    print(f"Existing CSV: {EXISTING_CSV}")
    print(f"Target Stations: {', '.join(TARGET_STATIONS)}")
    print(f"Skipping Existing: {', '.join(EXISTING_STATIONS)}")
    print()
    
    # Load existing data
    print("Loading existing dataset...")
    existing_df = pd.read_csv(EXISTING_CSV)
    print(f"SUCCESS: Loaded {len(existing_df)} existing records")
    
    # Process all PDF files
    all_extracted_data = []
    pdf_files = sorted(pdf_folder.glob("dsi_*.pdf"))
    
    print(f"\nProcessing {len(pdf_files)} PDF files...")
    
    for pdf_file in pdf_files:
        extracted_data = process_pdf_file(pdf_file, TARGET_STATIONS)
        all_extracted_data.extend(extracted_data)
    
    print(f"\nExtraction Summary:")
    print(f"   Total records extracted: {len(all_extracted_data)}")
    
    if all_extracted_data:
        # Convert to DataFrame
        new_df = pd.DataFrame(all_extracted_data)
        
        # Count unique stations found
        unique_stations = new_df['station_code'].unique()
        print(f"   Unique stations found: {len(unique_stations)}")
        print(f"   Stations: {', '.join(unique_stations)}")
        
        # Merge with existing data
        print(f"\nMerging with existing data...")
        merged_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # Remove duplicates based on station_code and year
        print("Removing duplicates...")
        initial_count = len(merged_df)
        merged_df = merged_df.drop_duplicates(subset=['station_code', 'year'], keep='first')
        final_count = len(merged_df)
        duplicates_removed = initial_count - final_count
        
        print(f"   Removed {duplicates_removed} duplicate records")
        
        # Save the extended dataset
        print(f"\nSaving extended dataset to {OUTPUT_CSV}...")
        merged_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
        
        # Print final summary
        print(f"\nSUCCESS!")
        print(f"SUCCESS: Extracted data for {len(unique_stations)} new stations: {', '.join(unique_stations)}")
        print(f"SUCCESS: Appended to {EXISTING_CSV}")
        print(f"WARNING: Skipped {len(EXISTING_STATIONS)} existing stations already in dataset")
        print(f"Final dataset: {final_count} records")
        print(f"Saved as: {OUTPUT_CSV}")
        
    else:
        print("ERROR: No data extracted for target stations")
        print("   This could mean:")
        print("   - Station codes not found in PDFs")
        print("   - PDF parsing issues")
        print("   - Different data format than expected")

if __name__ == "__main__":
    main()
