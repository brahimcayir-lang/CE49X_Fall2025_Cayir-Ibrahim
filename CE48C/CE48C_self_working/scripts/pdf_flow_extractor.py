#!/usr/bin/env python3
"""
DSI Flow Report PDF Extractor (2005-2020)
"""

import os
import re
import csv
import pdfplumber
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

# PDF directory
PDF_DIR = r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi"

# Target stations (37 stations)
TARGET_STATIONS = [
    'E22A065', 'E22A066', 'D22A093', 'E22A071', 'D14A185', 'E22A054', 'E22A063',
    'E14A018', 'D14A162', 'D14A186', 'D22A105', 'E22A053', 'D14A172', 'D14A117',
    'E14A027', 'D22A106', 'D14A200', 'E14A002', 'D14A179', 'D22A098', 'D22A159',
    'D14A064', 'E14A038', 'D14A201', 'D14A184', 'D14A211', 'D14A208', 'D14A214',
    'D14A207', 'D14A141', 'E22A062', 'E14A040', 'D14A215', 'D14A176', 'D14A011',
    'D14A188', 'D14A081'
]

# Years to process
YEARS = list(range(2005, 2021))  # 2005-2020

# Output file
OUTPUT_CSV = "dsi_flow_data_2005_2020.csv"

# Region patterns to check
REGION_PATTERNS = [
    r"14\.\s*Yesilirmak\s*Havzasi",
    r"22\.\s*Dogu\s*Karadeniz\s*Havzasi",
    r"14\s*-\s*YEŞİLIRMAK\s*HAVZASI",
    r"22\s*-\s*MÜTEFERRİK\s*DOĞU\s*KARADENİZ\s*SULARI"
]

# Month names in order (Oct through Sep)
MONTHS = ['oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep']


# ============================================================================
# DATA EXTRACTION FUNCTIONS
# ============================================================================

def check_region_match(line: str) -> bool:
    """Check if line matches one of the region patterns"""
    for pattern in REGION_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False


def parse_station_info(line: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse station code and name from line"""
    station_match = re.search(r'([A-Z]\d{2}[A-Z]\d{3})', line)
    if station_match:
        station_code = station_match.group(1)
        station_name = line.replace(station_code, '').strip()
        station_name = re.sub(r'\s+', ' ', station_name).strip()
        return station_code, station_name
    return None, None


def extract_catchment_and_elevation(line: str) -> Tuple[Optional[float], Optional[float]]:
    """Extract catchment area and elevation from line"""
    catchment_area = None
    elevation = None
    
    catchment_match = re.search(r'YAĞIŞ\s*ALANI\s*:\s*([0-9,]+(?:\.[0-9]+)?)', line, re.IGNORECASE)
    if catchment_match:
        catchment_area = float(catchment_match.group(1).replace(',', '.'))
    
    elevation_match = re.search(r'YAKLAŞIK\s*KOT\s*:\s*([0-9,]+(?:\.[0-9]+)?)\s*m', line, re.IGNORECASE)
    if elevation_match:
        elevation = float(elevation_match.group(1).replace(',', '.'))
    
    return catchment_area, elevation


def extract_observation_period(line: str) -> Optional[str]:
    """Extract observation period from line"""
    match = re.search(r'GÖZLEM\s*SÜRESİ\s*:\s*(.+?)(?:\s*(?:ORTALAMA|Gözlem))', line, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_annual_flow(line: str, year: int) -> Optional[float]:
    """Extract annual average flow from line"""
    match = re.search(rf'{year}\s*Su\s*yılında\s*([0-9,]+(?:\.[0-9]+)?)\s*m3/sn', line, re.IGNORECASE)
    if match:
        return float(match.group(1).replace(',', '.'))
    return None


def extract_monthly_values(line: str) -> List[Optional[float]]:
    """Extract 12 monthly values from a line"""
    values = []
    numbers = re.findall(r'([0-9,]+(?:\.[0-9]+)?)', line)
    
    for num_str in numbers[:12]:
        try:
            value = float(num_str.replace(',', '.'))
            values.append(value)
        except ValueError:
            values.append(0.0)  # Handle "-----" and "KURU" as 0
    
    while len(values) < 12:
        values.append(None)
    
    return values[:12]


def extract_annual_summary(line: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Extract annual summary values"""
    annual_total_m3 = None
    annual_mm = None
    annual_lt_sn_km2 = None
    
    if 'YILLIK TOPLAM AKIM' in line:
        numbers = re.findall(r'([0-9,]+(?:\.[0-9]+)?)', line)
        if len(numbers) >= 3:
            annual_total_m3 = float(numbers[0].replace(',', '.'))
            annual_mm = float(numbers[1].replace(',', '.'))
            annual_lt_sn_km2 = float(numbers[2].replace(',', '.'))
    
    return annual_total_m3, annual_mm, annual_lt_sn_km2


def process_pdf(pdf_path: Path, year: int) -> List[Dict]:
    """Process a single PDF file and extract all station data"""
    results = []
    print(f"\nProcessing: {pdf_path.name}")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            found_stations = set()
            
            for page_num, page in enumerate(pdf.pages, 1):
                if page_num % 200 == 0:
                    print(f"  Page {page_num}/{total_pages}")
                
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                
                if not lines or not check_region_match(lines[0]):
                    continue
                
                page_text = ' '.join(lines)
                if not any(station in page_text for station in TARGET_STATIONS):
                    continue
                
                for station_code in TARGET_STATIONS:
                    if (year, station_code) in found_stations:
                        continue
                    
                    if station_code not in page_text:
                        continue
                    
                    # Find station line
                    station_line_idx = None
                    station_name = None
                    
                    for i, line in enumerate(lines):
                        if station_code in line:
                            station_code_found, station_name = parse_station_info(line)
                            if station_code_found == station_code:
                                station_line_idx = i
                                break
                    
                    if station_line_idx is None:
                        continue
                    
                    # Extract header data
                    catchment_area = None
                    elevation = None
                    observation_period = None
                    annual_flow = None
                    
                    for i in range(min(15, len(lines) - station_line_idx)):
                        line = lines[station_line_idx + i]
                        
                        if 'YAĞIŞ ALANI' in line and 'YAKLAŞIK KOT' in line:
                            catchment_area, elevation = extract_catchment_and_elevation(line)
                        
                        if 'GÖZLEM SÜRESİ' in line:
                            observation_period = extract_observation_period(line)
                        
                        if f'{year} Su yılında' in line:
                            annual_flow = extract_annual_flow(line, year)
                    
                    # Extract monthly data
                    monthly_max = [None] * 12
                    monthly_min = [None] * 12
                    monthly_avg = [None] * 12
                    monthly_lt_sn_km2 = [None] * 12
                    monthly_mm = [None] * 12
                    monthly_mil_m3 = [None] * 12
                    
                    for i in range(min(100, len(lines))):
                        line = lines[i]
                        
                        if 'Maks.' in line:
                            monthly_max = extract_monthly_values(line)
                        elif 'Min.' in line:
                            monthly_min = extract_monthly_values(line)
                        elif 'Ortalama' in line and 'Maks.' not in line and 'Min.' not in line:
                            monthly_avg = extract_monthly_values(line)
                        elif 'LT/SN/Km2' in line:
                            monthly_lt_sn_km2 = extract_monthly_values(line)
                        elif 'AKIM mm.' in line:
                            monthly_mm = extract_monthly_values(line)
                        elif 'MİL. M3' in line:
                            monthly_mil_m3 = extract_monthly_values(line)
                    
                    # Extract annual summary
                    annual_total_m3 = None
                    annual_mm = None
                    annual_lt_sn_km2 = None
                    
                    for line in lines:
                        if 'YILLIK TOPLAM AKIM' in line:
                            annual_total_m3, annual_mm, annual_lt_sn_km2 = extract_annual_summary(line)
                            break
                    
                    # Create record
                    record = {
                        'year': year,
                        'station_code': station_code,
                        'station_name': station_name,
                        'region_name': lines[0] if lines else '',
                        'catchment_area_km2': catchment_area,
                        'estimated_elevation': elevation,
                        'observation_period': observation_period,
                        'avg_annual_flow_m3sn': annual_flow,
                    }
                    
                    # Add monthly values (Option B: all months for metric 1, then all for metric 2)
                    for i, month in enumerate(MONTHS):
                        record[f'{month}_max_flow_m3sn'] = monthly_max[i] if i < len(monthly_max) else None
                    for i, month in enumerate(MONTHS):
                        record[f'{month}_min_flow_m3sn'] = monthly_min[i] if i < len(monthly_min) else None
                    for i, month in enumerate(MONTHS):
                        record[f'{month}_avg_flow_m3sn'] = monthly_avg[i] if i < len(monthly_avg) else None
                    for i, month in enumerate(MONTHS):
                        record[f'{month}_lt_sn_km2'] = monthly_lt_sn_km2[i] if i < len(monthly_lt_sn_km2) else None
                    for i, month in enumerate(MONTHS):
                        record[f'{month}_mm'] = monthly_mm[i] if i < len(monthly_mm) else None
                    for i, month in enumerate(MONTHS):
                        record[f'{month}_mil_m3'] = monthly_mil_m3[i] if i < len(monthly_mil_m3) else None
                    
                    record['annual_total_flow_m3'] = annual_total_m3
                    record['annual_mm'] = annual_mm
                    record['annual_lt_sn_km2'] = annual_lt_sn_km2
                    
                    results.append(record)
                    found_stations.add((year, station_code))
                    print(f"  Found: {station_code} - {station_name}")
    
    except Exception as e:
        print(f"  ERROR: {str(e)}")
    
    return results


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    print("\n" + "="*80)
    print("DSI Flow Report PDF Extractor (2005-2020)")
    print("="*80)
    print(f"Target stations: {len(TARGET_STATIONS)}")
    print(f"Years: {YEARS[0]}-{YEARS[-1]}")
    print(f"PDF directory: {PDF_DIR}\n")
    
    # Check PDF directory
    pdf_dir_path = Path(PDF_DIR)
    if not pdf_dir_path.exists():
        print(f"ERROR: PDF directory not found: {PDF_DIR}")
        return
    
    # Find all PDF files
    pdf_files = {}
    for year in YEARS:
        pdf_name = f"dsi_{year}.pdf"
        pdf_path = pdf_dir_path / pdf_name
        if pdf_path.exists():
            pdf_files[year] = pdf_path
        else:
            print(f"WARNING: PDF not found for year {year}")
    
    if not pdf_files:
        print("ERROR: No PDF files found!")
        return
    
    print(f"Found {len(pdf_files)} PDF files\n")
    
    # Process each PDF
    all_results = []
    for i, (year, pdf_path) in enumerate(sorted(pdf_files.items()), 1):
        print(f"\n[{i}/{len(pdf_files)}] Year {year}")
        results = process_pdf(pdf_path, year)
        all_results.extend(results)
        print(f"  Extracted {len(results)} stations\n")
    
    # Summary
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"Total records: {len(all_results)}")
    print(f"Expected: {len(TARGET_STATIONS) * len(pdf_files)}")
    print(f"Missing: {len(TARGET_STATIONS) * len(pdf_files) - len(all_results)}")
    
    # Show missing stations
    found_stations_by_year = {}
    for record in all_results:
        year = record['year']
        if year not in found_stations_by_year:
            found_stations_by_year[year] = set()
        found_stations_by_year[year].add(record['station_code'])
    
    print("\nMissing stations by year:")
    for year in sorted(YEARS):
        if year in pdf_files:
            found = found_stations_by_year.get(year, set())
            missing = set(TARGET_STATIONS) - found
            if missing:
                print(f"\nYear {year}: {len(missing)} missing")
                for station in sorted(missing):
                    print(f"  - {station}")
    
    # Save to CSV
    if all_results:
        print("\n" + "="*80)
        print("SAVING RESULTS")
        print("="*80)
        
        output_path = Path(OUTPUT_CSV)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        all_keys = set()
        for record in all_results:
            all_keys.update(record.keys())
        
        # Ordered columns
        ordered_keys = []
        
        basic_keys = ['year', 'station_code', 'station_name', 'region_name', 
                     'catchment_area_km2', 'estimated_elevation', 'observation_period', 
                     'avg_annual_flow_m3sn']
        for key in basic_keys:
            if key in all_keys:
                ordered_keys.append(key)
        
        metrics = ['max_flow_m3sn', 'min_flow_m3sn', 'avg_flow_m3sn', 'lt_sn_km2', 'mm', 'mil_m3']
        for metric in metrics:
            for month in MONTHS:
                key = f'{month}_{metric}'
                if key in all_keys:
                    ordered_keys.append(key)
        
        annual_keys = ['annual_total_flow_m3', 'annual_mm', 'annual_lt_sn_km2']
        for key in annual_keys:
            if key in all_keys:
                ordered_keys.append(key)
        
        for key in sorted(all_keys):
            if key not in ordered_keys:
                ordered_keys.append(key)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=ordered_keys)
            writer.writeheader()
            writer.writerows(all_results)
        
        print(f"Data saved to: {output_path}")
        print(f"Total records: {len(all_results)}")
        print(f"Total columns: {len(ordered_keys)}")
    
    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
