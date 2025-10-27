#!/usr/bin/env python3
"""
DSİ PDF Data Page Finder - Finds actual data pages for specific stations
"""

import fitz  # PyMuPDF
import csv
from pathlib import Path
import re

def find_data_pages_for_stations(pdf_path, target_stations, output_file="station_data_pages.csv"):
    """Find actual data pages for specific stations."""
    
    print(f"Searching for data pages for stations: {target_stations}")
    
    try:
        doc = fitz.open(pdf_path)
        station_pattern = re.compile(r'[A-Z]\d{2}[A-Z]\d{3}')
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Page_Number', 'Station_Code', 'Line_Number', 'Text_Content', 'Has_Coordinates', 'Has_Discharge_Data'])
            
            found_stations = set()
            
            # Search from page 1000 onwards (where actual data pages start)
            for page_num in range(1000, len(doc)):
                page = doc[page_num]
                text = page.get_text()
                lines = text.split('\n')
                
                page_stations = []
                
                for line_num, line in enumerate(lines):
                    line = line.strip()
                    if line:
                        # Check for target station codes in this line
                        station_matches = station_pattern.findall(line)
                        
                        for station_code in station_matches:
                            if station_code in target_stations:
                                page_stations.append(station_code)
                                found_stations.add(station_code)
                                
                                # Check if this page has coordinate and discharge data
                                has_coordinates = any(keyword in text.lower() for keyword in ['°', 'doğu', 'batı', 'kuzey', 'güney', 'koordinat'])
                                has_discharge = any(keyword in text.lower() for keyword in ['m3/sn', 'akım', 'debi', 'ortalama', 'toplam'])
                                
                                writer.writerow([
                                    page_num + 1, 
                                    station_code, 
                                    line_num + 1, 
                                    line,
                                    has_coordinates,
                                    has_discharge
                                ])
                                
                                print(f"Page {page_num + 1}, Line {line_num + 1}: {station_code}")
                                print(f"  Text: {line}")
                                print(f"  Has coordinates: {has_coordinates}")
                                print(f"  Has discharge data: {has_discharge}")
                                
                                # Show more context for this page
                                print(f"  Page context (first 10 lines):")
                                for i, context_line in enumerate(lines[:10]):
                                    if context_line.strip():
                                        print(f"    Line {i+1}: {context_line.strip()}")
                                print("-" * 50)
                
                if page_stations:
                    print(f"Found stations on page {page_num + 1}: {page_stations}")
        
        doc.close()
        print(f"\nFound data pages for stations: {sorted(found_stations)}")
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
        found_stations = find_data_pages_for_stations(pdf_path, target_stations, "dsi_2020_data_pages.csv")
    else:
        print(f"PDF file not found: {pdf_path}")

if __name__ == "__main__":
    main()
