#!/usr/bin/env python3
"""
DSİ Hydrological Station Data Extractor - Final Structured Version
Extracts structured data from DSİ annual streamflow report PDFs (2000-2020)
with exact column specification and improved parsing
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
        logging.FileHandler('dsi_extraction_final.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DSIFinalExtractor:
    def __init__(self, pdf_directory: str, output_file: str):
        self.pdf_directory = pdf_directory
        self.output_file = output_file
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
        
        # Initialize CSV with exact headers as specified
        self._initialize_csv()
        
    def _initialize_csv(self):
        """Initialize CSV file with exact headers as specified"""
        headers = [
            'file', 'page', 'year', 'station_code', 'station_name', 'coordinates',
            'catchment_area_km2', 'annual_avg_flow_m3s', 'annual_total_m3',
            'mm_total', 'avg_ltsnkm2'
        ]
        
        # Add monthly columns: metric first, then month (as specified)
        for metric in self.metrics:
            for month in self.months:
                headers.append(f"{month}_{metric}_m3")
        
        # Create CSV file with UTF-8 encoding
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        
        logger.info(f"[OK] Initialized CSV file: {self.output_file}")
        logger.info(f"Total columns: {len(headers)} (11 metadata + {len(self.metrics) * len(self.months)} monthly)")
    
    def _normalize_number(self, text: str) -> Optional[float]:
        """Convert Turkish number format to float"""
        if not text or text.strip() == '':
            return None
        
        # Remove extra spaces and normalize Turkish decimal separators
        text = text.strip().replace(',', '.').replace(' ', '')
        
        # Extract number using regex
        numbers = re.findall(r'[\d.]+', text)
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                return None
        return None
    
    def _extract_station_code(self, text: str) -> Optional[str]:
        """Extract station code from text"""
        pattern = r'[A-Z]\d{2}[A-Z]\d{3}'
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
        """Extract monthly data with structured parsing"""
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
        """Extract annual totals from footer"""
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
        """Extract all station data with structured approach"""
        lines = page_text.split('\n')
        
        # Look for station code in every 2nd row (as specified)
        station_code = None
        station_name = None
        
        for i in range(0, min(20, len(lines)), 2):  # Check every 2nd row, first 20 lines
            line = lines[i]
            code = self._extract_station_code(line)
            if code and code in self.target_stations:
                station_code = code
                # Extract station name (text after the code)
                name_part = line.replace(code, '').strip()
                if name_part:
                    station_name = name_part
                break
        
        if not station_code:
            return None
        
        logger.info(f"[OK] Found station {station_code} on page {page_num}")
        
        # Extract all data
        coordinates = None
        catchment_area = None
        annual_avg_flow = None
        
        for line in lines:
            if not coordinates:
                coordinates = self._extract_coordinates(line)
            if not catchment_area:
                catchment_area = self._extract_catchment_area(line)
            if not annual_avg_flow:
                annual_avg_flow = self._extract_annual_avg_flow(line, year)
        
        # Extract monthly data with structured parsing
        monthly_data = self._extract_monthly_data_structured(page_text)
        
        # Extract annual totals
        annual_total, mm_total, avg_ltsnkm2 = self._extract_annual_totals(page_text)
        
        # Prepare result
        result = {
            'file': filename,
            'page': page_num,
            'year': year,
            'station_code': station_code,
            'station_name': station_name or 'N/A',
            'coordinates': coordinates or 'N/A',
            'catchment_area_km2': catchment_area,
            'annual_avg_flow_m3s': annual_avg_flow,
            'annual_total_m3': annual_total,
            'mm_total': mm_total,
            'avg_ltsnkm2': avg_ltsnkm2
        }
        
        # Add monthly data in metric-first order (as specified)
        for metric in self.metrics:
            for month in self.months:
                key = f"{month}_{metric}_m3"
                if month in monthly_data and metric in monthly_data[month]:
                    result[key] = monthly_data[month][metric]
                else:
                    result[key] = None
        
        # Count extracted values for debugging
        extracted_values = sum(1 for metric in self.metrics 
                             for month in self.months
                             if month in monthly_data and metric in monthly_data[month] 
                             and monthly_data[month][metric] is not None)
        
        total_expected = len(self.metrics) * len(self.months)
        logger.info(f"✅ Extracted {station_code} ({year}): {extracted_values}/{total_expected} values")
        
        # Debug if too many missing values
        if extracted_values < total_expected * 0.5:  # Less than 50% extracted
            logger.warning(f"⚠️ {station_code} ({year}): Only {extracted_values}/{total_expected} values extracted - checking for issues")
            # Log the raw text for debugging
            logger.debug(f"Raw page text: {page_text[:500]}...")
        
        return result
    
    def _process_pdf_structured(self, pdf_path: str) -> List[Dict]:
        """Process a single PDF file with structured approach"""
        results = []
        filename = os.path.basename(pdf_path)
        
        # Extract year from filename
        year_match = re.search(r'(\d{4})', filename)
        if not year_match:
            logger.warning(f"Could not extract year from filename: {filename}")
            return results
        
        year = int(year_match.group(1))
        
        try:
            doc = fitz.open(pdf_path)
            logger.info(f"Processing {filename} ({len(doc)} pages)")
            
            pages_processed = 0
            pages_skipped = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text with proper encoding
                page_text = page.get_text()
                
                # Extract station data from this page
                station_data = self._extract_station_data_structured(page_text, page_num + 1, filename, year)
                if station_data:
                    results.append(station_data)
                    pages_processed += 1
                else:
                    pages_skipped += 1
            
            doc.close()
            
            logger.info(f"📁 {filename}: {pages_processed} stations extracted, {pages_skipped} pages skipped")
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
        
        return results
    
    def _append_to_csv(self, data: Dict):
        """Append extracted data to CSV file"""
        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Prepare row data in the correct order
            row = [
                data['file'], data['page'], data['year'], data['station_code'],
                data['station_name'], data['coordinates'], data['catchment_area_km2'],
                data['annual_avg_flow_m3s'], data['annual_total_m3'], data['mm_total'],
                data['avg_ltsnkm2']
            ]
            
            # Add monthly data in metric-first order (as specified)
            for metric in self.metrics:
                for month in self.months:
                    key = f"{month}_{metric}_m3"
                    row.append(data.get(key))
            
            writer.writerow(row)
    
    def process_all_pdfs_structured(self):
        """Process all PDF files with structured approach"""
        if not os.path.exists(self.pdf_directory):
            logger.error(f"PDF directory not found: {self.pdf_directory}")
            return
        
        pdf_files = [f for f in os.listdir(self.pdf_directory) if f.endswith('.pdf')]
        pdf_files.sort()
        
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        total_extracted = 0
        processed_stations = set()
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.pdf_directory, pdf_file)
            
            # Extract year from filename
            year_match = re.search(r'(\d{4})', pdf_file)
            if not year_match:
                continue
            
            year = int(year_match.group(1))
            
            # Process PDF
            results = self._process_pdf_structured(pdf_path)
            
            for result in results:
                # Check for duplicates
                station_year_key = (result['station_code'], year)
                if station_year_key in processed_stations:
                    logger.warning(f"⚠️ {result['station_code']} skipped (duplicate)")
                    continue
                
                # Append to CSV
                self._append_to_csv(result)
                processed_stations.add(station_year_key)
                total_extracted += 1
        
        logger.info(f"[OK] CSV updated: {self.output_file}")
        logger.info(f"Total stations extracted: {total_extracted}")


def main():
    """Main function"""
    # Paths as specified
    pdf_directory = r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi"
    output_file = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_final_structured.csv"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Initialize extractor
    extractor = DSIFinalExtractor(pdf_directory, output_file)
    
    # Process all PDFs
    extractor.process_all_pdfs_structured()


if __name__ == "__main__":
    main()
