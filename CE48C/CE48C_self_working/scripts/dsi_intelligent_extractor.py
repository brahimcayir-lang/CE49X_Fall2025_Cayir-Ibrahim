#!/usr/bin/env python3
"""
Intelligent DSİ Hydrological Station Data Extractor
Extracts structured data from DSİ annual streamflow report PDFs (2000-2020)
"""

import os
import re
import csv
import fitz  # PyMuPDF
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DSIExtractor:
    def __init__(self, pdf_directory: str, output_file: str):
        self.pdf_directory = pdf_directory
        self.output_file = output_file
        self.target_stations = {
            'D14A011', 'D14A117', 'D14A144', 'D14A146', 'D14A149', 'D14A162',
            'D14A172', 'D14A192', 'D14A018', 'D22A093', 'D22A095', 'D22A105',
            'D22A106', 'D22A158', 'E22A054', 'D22A116', 'E22A065'
        }
        
        # Turkish month names
        self.months = ['Ekim', 'Kasım', 'Aralık', 'Ocak', 'Şubat', 'Mart',
                      'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül']
        
        # Metrics to extract
        self.metrics = ['flow_max', 'flow_min', 'flow_avg', 'ltsnkm2', 'akim_mm', 'milm3']
        
        # Initialize CSV with headers
        self._initialize_csv()
        
    def _initialize_csv(self):
        """Initialize CSV file with proper headers"""
        headers = [
            'file', 'page', 'year', 'station_code', 'station_name', 'coordinates',
            'catchment_area_km2', 'annual_avg_flow_m3s', 'annual_total_m3',
            'mm_total', 'avg_ltsnkm2'
        ]
        
        # Add monthly columns
        for month in self.months:
            for metric in self.metrics:
                headers.append(f"{month.lower()}_{metric}_m3")
        
        # Create CSV file
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        
        logger.info(f"[OK] Initialized CSV file: {self.output_file}")
    
    def _normalize_number(self, text: str) -> Optional[float]:
        """Convert Turkish number format to float"""
        if not text or text.strip() == '':
            return None
        
        # Remove extra spaces and normalize
        text = text.strip().replace(',', '.')
        
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
        # Pattern for station codes like D22A105, E03A016
        pattern = r'[A-Z]\d{2}[A-Z]\d{3}'
        matches = re.findall(pattern, text)
        if matches:
            return matches[0]
        return None
    
    def _extract_coordinates(self, text: str) -> Optional[str]:
        """Extract coordinates from text"""
        # Look for coordinate pattern with degrees, minutes, seconds
        pattern = r'\d+°\d+\'\d+"\s*(?:Doğu|Kuzey)'
        matches = re.findall(pattern, text)
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
    
    def _extract_monthly_data(self, text: str) -> Dict[str, Dict[str, float]]:
        """Extract monthly data from the summary table"""
        monthly_data = {}
        
        # Split text into lines
        lines = text.split('\n')
        
        # Find the table section with monthly data
        table_start = -1
        for i, line in enumerate(lines):
            if any(metric in line for metric in ['Maks.', 'Min.', 'Ortalama', 'LT/SN/Km2', 'AKIM mm.', 'MİL. M3']):
                table_start = i
                break
        
        if table_start == -1:
            return monthly_data
        
        # Extract data from table rows
        metric_mapping = {
            'Maks.': 'flow_max',
            'Min.': 'flow_min', 
            'Ortalama': 'flow_avg',
            'LT/SN/Km2': 'ltsnkm2',
            'AKIM mm.': 'akim_mm',
            'MİL. M3': 'milm3'
        }
        
        for i in range(table_start, min(table_start + 6, len(lines))):
            line = lines[i]
            for metric_key, metric_name in metric_mapping.items():
                if metric_key in line:
                    # Extract numbers from this line
                    numbers = re.findall(r'[\d.,]+', line)
                    if len(numbers) >= 12:  # Should have 12 monthly values
                        for j, month in enumerate(self.months):
                            if j < len(numbers):
                                value = self._normalize_number(numbers[j])
                                if month not in monthly_data:
                                    monthly_data[month] = {}
                                monthly_data[month][metric_name] = value
                    break
        
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
    
    def _extract_station_data(self, page_text: str, page_num: int, filename: str, year: int) -> Optional[Dict]:
        """Extract all station data from a page"""
        lines = page_text.split('\n')
        
        # Check if this page contains any target station
        station_code = None
        station_name = None
        
        # Look for station code in first few lines
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
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
        
        # Extract monthly data
        monthly_data = self._extract_monthly_data(page_text)
        
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
        
        # Add monthly data
        for month in self.months:
            for metric in self.metrics:
                key = f"{month.lower()}_{metric}_m3"
                if month in monthly_data and metric in monthly_data[month]:
                    result[key] = monthly_data[month][metric]
                else:
                    result[key] = None
        
        return result
    
    def _process_pdf(self, pdf_path: str) -> List[Dict]:
        """Process a single PDF file"""
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
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                
                # Extract station data from this page
                station_data = self._extract_station_data(page_text, page_num + 1, filename, year)
                if station_data:
                    results.append(station_data)
                    logger.info(f"[OK] {station_data['station_code']} extracted from {filename} (page {page_num + 1})")
            
            doc.close()
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
        
        return results
    
    def _append_to_csv(self, data: Dict):
        """Append extracted data to CSV file"""
        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Prepare row data
            row = [
                data['file'], data['page'], data['year'], data['station_code'],
                data['station_name'], data['coordinates'], data['catchment_area_km2'],
                data['annual_avg_flow_m3s'], data['annual_total_m3'], data['mm_total'],
                data['avg_ltsnkm2']
            ]
            
            # Add monthly data
            for month in self.months:
                for metric in self.metrics:
                    key = f"{month.lower()}_{metric}_m3"
                    row.append(data.get(key))
            
            writer.writerow(row)
    
    def process_all_pdfs(self):
        """Process all PDF files in the directory"""
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
            results = self._process_pdf(pdf_path)
            
            for result in results:
                # Check for duplicates
                station_year_key = (result['station_code'], year)
                if station_year_key in processed_stations:
                    logger.warning(f"[WARNING] {result['station_code']} skipped (duplicate)")
                    continue
                
                # Append to CSV
                self._append_to_csv(result)
                processed_stations.add(station_year_key)
                total_extracted += 1
        
        logger.info(f"[OK] CSV updated: {self.output_file}")
        logger.info(f"Total stations extracted: {total_extracted}")


def main():
    """Main function"""
    # Paths
    pdf_directory = r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi"
    output_file = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_auto_extracted.csv"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Initialize extractor
    extractor = DSIExtractor(pdf_directory, output_file)
    
    # Process all PDFs
    extractor.process_all_pdfs()


if __name__ == "__main__":
    main()
