#!/usr/bin/env python3
"""
DSİ PDF Data Extractor - Uses page references from index to find actual data
"""

import fitz  # PyMuPDF
import csv
from pathlib import Path
import re

def extract_station_data_from_referenced_pages(pdf_path, target_stations, output_file="station_data_extracted.csv"):
    """Extract data from pages referenced in the index."""
    
    print(f"Extracting data for stations: {target_stations}")
    
    try:
        doc = fitz.open(pdf_path)
        station_pattern = re.compile(r'[A-Z]\d{2}[A-Z]\d{3}')
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Station_Code', 'Station_Name', 'Page_Number', 'Text_Content', 'Has_Coordinates', 'Has_Discharge_Data'])
            
            found_stations = set()
            
            # First, find the index pages and extract page references
            station_page_map = {}
            
            print("Step 1: Building station-to-page mapping from index...")
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                lines = text.split('\n')
                
                for line in lines:
                    station_matches = station_pattern.findall(line)
                    for station_code in station_matches:
                        if station_code in target_stations:
                            # Extract page number from the end of the line
                            page_match = re.search(r'(\d+)\s*$', line.strip())
                            if page_match:
                                referenced_page = int(page_match.group(1))
                                station_page_map[station_code] = referenced_page
                                print(f"Found {station_code} → page {referenced_page}")
            
            print(f"\nStep 2: Extracting data from referenced pages...")
            # Now extract data from the referenced pages
            for station_code, referenced_page in station_page_map.items():
                if referenced_page <= len(doc):
                    page = doc[referenced_page - 1]  # Convert to 0-based index
                    text = page.get_text()
                    lines = text.split('\n')
                    
                    # Find station name (usually in first few lines)
                    station_name = ""
                    for line in lines[:10]:
                        if station_code in line:
                            # Extract everything after the station code
                            parts = line.split(station_code)
                            if len(parts) > 1:
                                station_name = parts[1].strip()
                                break
                    
                    # Check if this page has coordinate and discharge data
                    has_coordinates = any(keyword in text.lower() for keyword in ['°', 'doğu', 'batı', 'kuzey', 'güney', 'koordinat'])
                    has_discharge = any(keyword in text.lower() for keyword in ['m3/sn', 'akım', 'debi', 'ortalama', 'toplam'])
                    
                    # Get first 20 lines of the page for context
                    context_lines = []
                    for i, line in enumerate(lines[:20]):
                        if line.strip():
                            context_lines.append(f"Line {i+1}: {line.strip()}")
                    
                    context = " | ".join(context_lines)
                    
                    writer.writerow([
                        station_code,
                        station_name,
                        referenced_page,
                        context,
                        has_coordinates,
                        has_discharge
                    ])
                    
                    found_stations.add(station_code)
                    
                    print(f"\n=== {station_code} - Page {referenced_page} ===")
                    print(f"Station Name: {station_name}")
                    print(f"Has coordinates: {has_coordinates}")
                    print(f"Has discharge data: {has_discharge}")
                    print("First 10 lines:")
                    for i, line in enumerate(lines[:10]):
                        if line.strip():
                            print(f"  Line {i+1}: {line.strip()}")
                    print("-" * 50)
        
        doc.close()
        print(f"\nExtracted data for stations: {sorted(found_stations)}")
        print(f"Missing stations: {sorted(target_stations - found_stations)}")
        print(f"Results saved to: {output_file}")
        
        return found_stations
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return set()

def main():
    # Target stations
    target_stations = {
        'D22A144', 'D22A145', 'D22A065', 'D22A093', 
        'D22A095', 'D14A149', 'D22A158'
    }
    
    # Test with 2020 PDF
    pdf_path = r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi\dsi_2020.pdf"
    
    if Path(pdf_path).exists():
        found_stations = extract_station_data_from_referenced_pages(pdf_path, target_stations, "dsi_2020_extracted_data.csv")
    else:
        print(f"PDF file not found: {pdf_path}")

if __name__ == "__main__":
    main()
