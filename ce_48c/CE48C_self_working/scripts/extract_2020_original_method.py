#!/usr/bin/env python3
"""
Use the ORIGINAL working code for 2020 extraction
"""

import os
import re
import csv
import fitz  # PyMuPDF
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dsi_extraction_2020_original.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DSIExtractor2020:
    def __init__(self):
        self.target_stations = {
            'D14A011', 'D14A117', 'D14A144', 'D14A146', 'D14A149', 'D14A162',
            'D14A172', 'D14A192', 'D14A018', 'D22A093', 'D22A095', 'D22A105',
            'D22A106', 'D22A158', 'E22A054', 'D22A116', 'E22A065'
        }
        
        # English month order (water year: Oct to Sep)
        self.months = ["oct", "nov", "dec", "jan", "feb", "mar", 
                      "apr", "may", "jun", "jul", "aug", "sep"]
        
        # Metrics in exact order as specified
        self.metrics = ['flow_max', 'flow_min', 'flow_avg', 'ltsnkm2', 'akim_mm', 'milm3']
        
        # Turkish metric keywords
        self.metric_keywords = {
            'flow_max': ['Maks.', 'MAKS.'],
            'flow_min': ['Min.', 'MIN.'],
            'flow_avg': ['Ortalama', 'ORTALAMA'],
            'ltsnkm2': ['LT/SN/Km2', 'LT/SN/KM2'],
            'akim_mm': ['AKIM mm.', 'AKIM MM.'],
            'milm3': ['MİL. M3', 'MIL. M3']
        }
    
    def _normalize_number(self, text: str) -> Optional[float]:
        """Normalize number from text"""
        if not text:
            return None
        try:
            # Replace comma with dot for decimal separator
            normalized = text.replace(',', '.')
            return float(normalized)
        except (ValueError, TypeError):
            return None
    
    def _extract_station_code(self, text: str) -> Optional[str]:
        """Extract station code from text"""
        pattern = r'\b([A-Z]\d{2}[A-Z]\d{3})\b'
        matches = re.findall(pattern, text)
        if matches:
            return matches[0]
        return None
    
    def _extract_coordinates(self, text: str) -> Optional[str]:
        """Extract coordinates from text"""
        pattern = r'\d+°\d+\'\d+"\s*(?:Doğu|Kuzey|DOĞU|KUZEY)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        if len(matches) >= 2:
            return ' '.join(matches[:2])
        return None
    
    def _extract_catchment_area(self, text: str) -> Optional[float]:
        """Extract catchment area from YAĞIŞ ALANI line"""
        if 'YAĞIŞ ALANI' in text or 'YAĞIS ALANI' in text:
            return self._normalize_number(text)
        return None
    
    def _extract_annual_avg_flow(self, text: str, year: int) -> Optional[float]:
        """Extract annual average flow for specific year"""
        year_pattern = rf'{year}\s*Su\s*yılında.*?(\d+[.,]\d+)\s*m3/sn'
        matches = re.findall(year_pattern, text, re.IGNORECASE)
        if matches:
            return self._normalize_number(matches[0])
        return None
    
    def _extract_monthly_data_structured(self, text: str) -> Dict[str, Dict[str, float]]:
        """Extract monthly data with structured parsing - SAME AS ORIGINAL"""
        monthly_data = {}
        
        # Split text into lines
        lines = text.split('\n')
        
        # Find lines with metric keywords
        for line in lines:
            # Check if this line contains a metric keyword
            current_metric = None
            for metric, keywords in self.metric_keywords.items():
                if any(keyword in line for keyword in keywords):
                    current_metric = metric
                    break
            
            if not current_metric:
                continue
            
            logger.info(f"Processing {current_metric} line: {line[:100]}...")
            
            # Extract numbers from this line - should have exactly 12 values
            numbers = re.findall(r'[\d.,]+', line)
            
            if len(numbers) >= 12:  # Should have 12 monthly values
                logger.info(f"Found {len(numbers)} values for {current_metric}")
                
                # Map values to months (Oct-Sep order)
                for j, month in enumerate(self.months):
                    if j < len(numbers):
                        value = self._normalize_number(numbers[j])
                        
                        if month not in monthly_data:
                            monthly_data[month] = {}
                        monthly_data[month][current_metric] = value
                        
                        if value is not None:
                            logger.debug(f"  {month}: {value}")
            else:
                logger.warning(f"Only found {len(numbers)} values for {current_metric}, expected 12")
        
        return monthly_data
    
    def _extract_annual_totals(self, text: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Extract annual totals from footer - SAME AS ORIGINAL"""
        annual_total = None
        mm_total = None
        avg_ltsnkm2 = None
        
        # Extract annual total
        annual_pattern = r'SU\s*YILI.*?YILLIK\s*TOPLAM\s*AKIM.*?(\d+[.,]\d+)\s*MİLYON\s*M3'
        matches = re.findall(annual_pattern, text, re.IGNORECASE)
        if matches:
            annual_total = self._normalize_number(matches[0])
        
        # Extract mm total and avg ltsnkm2
        mm_pattern = r'(\d+[.,]?\d*)\s*MM\.'
        ltsnkm2_pattern = r'(\d+[.,]?\d*)\s*LT/SN/Km2'
        
        mm_matches = re.findall(mm_pattern, text)
        ltsnkm2_matches = re.findall(ltsnkm2_pattern, text)
        
        if mm_matches:
            mm_total = self._normalize_number(mm_matches[-1])  # Take last occurrence
        if ltsnkm2_matches:
            avg_ltsnkm2 = self._normalize_number(ltsnkm2_matches[-1])  # Take last occurrence
        
        return annual_total, mm_total, avg_ltsnkm2
    
    def _extract_station_data_structured(self, page_text: str, page_num: int, filename: str, year: int) -> Optional[Dict]:
        """Extract all station data with structured approach - SAME AS ORIGINAL"""
        lines = page_text.split('\n')
        
        # Look for station code in every 2nd row (as specified)
        for i in range(0, len(lines), 2):
            line = lines[i]
            station_code = self._extract_station_code(line)
            
            if station_code and station_code in self.target_stations:
                logger.info(f"Found station {station_code} on page {page_num}")
                
                # Extract station name (text after station code)
                station_name = line.replace(station_code, '').strip()
                station_name = re.sub(r'\s+', ' ', station_name)
                
                # Extract other data from the page
                coordinates = self._extract_coordinates(page_text)
                catchment_area = self._extract_catchment_area(page_text)
                annual_avg_flow = self._extract_annual_avg_flow(page_text, year)
                annual_total, mm_total, avg_ltsnkm2 = self._extract_annual_totals(page_text)
                
                # Extract monthly data
                monthly_data = self._extract_monthly_data_structured(page_text)
                
                # Create result dictionary
                result = {
                    'file': filename,
                    'page': page_num,
                    'year': year,
                    'station_code': station_code,
                    'station_name': station_name,
                    'coordinates': coordinates,
                    'catchment_area_km2': catchment_area,
                    'annual_avg_flow_m3s': annual_avg_flow,
                    'annual_total_m3': annual_total,
                    'mm_total': mm_total,
                    'avg_ltsnkm2': avg_ltsnkm2
                }
                
                # Add monthly data
                for month in self.months:
                    for metric in self.metrics:
                        key = f"{month}_{metric}_m3"
                        if month in monthly_data and metric in monthly_data[month]:
                            result[key] = monthly_data[month][metric]
                        else:
                            result[key] = None
                
                return result
        
        return None
    
    def extract_2020_data(self):
        """Extract 2020 data using the ORIGINAL working method"""
        pdf_path = r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi\dsi_2020.pdf"
        
        if not os.path.exists(pdf_path):
            logger.error(f"PDF not found: {pdf_path}")
            return []
        
        results = []
        doc = fitz.open(pdf_path)
        
        logger.info(f"Processing dsi_2020.pdf with ORIGINAL method...")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            
            # Extract station data from this page
            station_data = self._extract_station_data_structured(page_text, page_num + 1, 'dsi_2020.pdf', 2020)
            if station_data:
                results.append(station_data)
                logger.info(f"[OK] Extracted: {station_data['station_code']} - {station_data['station_name']}")
                if station_data['annual_avg_flow_m3s']:
                    logger.info(f"  Annual flow: {station_data['annual_avg_flow_m3s']} m³/s")
        
        doc.close()
        return results

def update_csv_with_original_method():
    """Update CSV using the ORIGINAL working method"""
    csv_path = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_final_structured.csv"
    
    # Read existing data
    existing_df = pd.read_csv(csv_path)
    
    # Remove all 2020 data
    existing_df = existing_df[existing_df['year'] != 2020]
    print(f"Removed 2020 data. Remaining records: {len(existing_df)}")
    
    # Extract 2020 data using ORIGINAL method
    extractor = DSIExtractor2020()
    extracted_data = extractor.extract_2020_data()
    
    if not extracted_data:
        print("No 2020 data extracted")
        return
    
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
    
    print(f"\nUpdated CSV with {len(extracted_data)} ORIGINAL METHOD 2020 records")
    print(f"Total records: {len(combined_df)}")
    
    # Show summary
    stations_with_flow = [d for d in extracted_data if d['annual_avg_flow_m3s'] is not None]
    print(f"Stations with flow data: {len(stations_with_flow)}")
    
    if stations_with_flow:
        print("\nStations with annual flow data:")
        for data in stations_with_flow:
            print(f"  {data['station_code']}: {data['annual_avg_flow_m3s']} m³/s")

def main():
    update_csv_with_original_method()

if __name__ == "__main__":
    main()
