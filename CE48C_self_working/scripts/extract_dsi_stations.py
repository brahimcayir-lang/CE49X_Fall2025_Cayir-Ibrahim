#!/usr/bin/env python3
"""
DSİ Akım Gözlem Yıllığı PDF Data Extractor

Extracts hydrological station data from DSİ annual streamflow reports (2000-2020).
Optimized for speed and memory efficiency using PyMuPDF.

Author: AI Assistant
Date: 2024
"""

import os
import re
import csv
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DSIExtractor:
    """Fast and memory-efficient DSİ PDF data extractor."""
    
    def __init__(self, pdf_directory: str, output_csv: str = "dsi_akim_verileri_2000_2020.csv"):
        """
        Initialize the DSİ extractor.
        
        Args:
            pdf_directory: Path to directory containing DSİ PDF files
            output_csv: Output CSV filename
        """
        self.pdf_directory = Path(pdf_directory)
        self.output_csv = output_csv
        
        # Target station codes to extract
        self.target_stations = {
            'D22A144', 'D22A145', 'D22A065', 'D22A093', 
            'D22A095', 'D14A149', 'D22A158'
        }
        
        # Regex patterns for data extraction
        self.station_code_pattern = re.compile(r'[A-Z]\d{2}[A-Z]\d{3}')
        
        # Coordinate patterns (Turkish and English notation)
        self.coord_patterns = [
            # Turkish notation from screenshots: "26°34'20" Doğu - 41°38'50" Kuzey"
            re.compile(r'(\d{1,2})°(\d{1,2})\'(\d{1,2})"\s*(Doğu|Batı)\s*-\s*(\d{1,2})°(\d{1,2})\'(\d{1,2})"\s*(Kuzey|Güney)'),
            # Turkish notation: 40°12'30"K 36°52'10"D
            re.compile(r'(\d{1,2})°(\d{1,2})\'(\d{1,2})"([KD])\s+(\d{1,2})°(\d{1,2})\'(\d{1,2})"([KD])'),
            # English notation: 40°12'30"N 36°52'10"E
            re.compile(r'(\d{1,2})°(\d{1,2})\'(\d{1,2})"([NS])\s+(\d{1,2})°(\d{1,2})\'(\d{1,2})"([EW])')
        ]
        
        # Numeric patterns for discharge data (improved for comma/dot handling)
        self.numeric_pattern = re.compile(r'(\d+[.,]\d+|\d+)')
        self.numeric_with_unit_pattern = re.compile(r'(\d+[.,]\d+|\d+)\s*(m3/sn|m³/sn|milyon|m3|lt/sn|mm)', re.IGNORECASE)
        
        # Initialize CSV file with headers if it doesn't exist
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.output_csv):
            headers = [
                'Year', 'Station_Code', 'Station_Name', 'Latitude', 'Longitude',
                'Annual_Mean_Discharge', 'Total_Annual_Flow', 'Specific_Flow'
            ]
            with open(self.output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            logger.info(f"Created new CSV file: {self.output_csv}")
    
    def extract_year_from_filename(self, filename: str) -> Optional[int]:
        """
        Extract year from PDF filename.
        
        Args:
            filename: PDF filename (e.g., 'dsi_2020.pdf', 'DSI_2019.pdf')
            
        Returns:
            Year as integer or None if not found
        """
        year_match = re.search(r'(\d{4})', filename)
        return int(year_match.group(1)) if year_match else None
    
    def get_second_line_text(self, page) -> str:
        """
        Extract only the second line of text from a PDF page.
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            Second line text or empty string
        """
        try:
            text = page.get_text()
            lines = text.split('\n')
            return lines[1].strip() if len(lines) > 1 else ""
        except Exception as e:
            logger.warning(f"Error reading page text: {e}")
            return ""
    
    def parse_coordinates(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse coordinates from text using multiple patterns.
        
        Args:
            text: Text containing coordinates
            
        Returns:
            Tuple of (latitude, longitude) or (None, None)
        """
        for pattern in self.coord_patterns:
            match = pattern.search(text)
            if match:
                groups = match.groups()
                
                if len(groups) == 8:
                    # Turkish notation from screenshots: "26°34'20" Doğu - 41°38'50" Kuzey"
                    if groups[3] in ['Doğu', 'Batı'] and groups[7] in ['Kuzey', 'Güney']:
                        lon_deg, lon_min, lon_sec, lon_dir = groups[:4]
                        lat_deg, lat_min, lat_sec, lat_dir = groups[4:]
                        
                        # Convert to decimal degrees
                        lat_decimal = float(lat_deg) + float(lat_min)/60 + float(lat_sec)/3600
                        lon_decimal = float(lon_deg) + float(lon_min)/60 + float(lon_sec)/3600
                        
                        # Apply direction
                        if lat_dir == 'Güney':  # South
                            lat_decimal = -lat_decimal
                        if lon_dir == 'Batı':   # West
                            lon_decimal = -lon_decimal
                            
                        return f"{lat_decimal:.6f}", f"{lon_decimal:.6f}"
                    
                    # Turkish notation: K/D
                    elif groups[3] in 'KD' and groups[7] in 'KD':
                        lat_deg, lat_min, lat_sec, lat_dir = groups[:4]
                        lon_deg, lon_min, lon_sec, lon_dir = groups[4:]
                        
                        # Convert to decimal degrees
                        lat_decimal = float(lat_deg) + float(lat_min)/60 + float(lat_sec)/3600
                        lon_decimal = float(lon_deg) + float(lon_min)/60 + float(lon_sec)/3600
                        
                        # Apply direction
                        if lat_dir == 'K':  # Kuzey (North)
                            lat_decimal = lat_decimal
                        else:  # Güney (South)
                            lat_decimal = -lat_decimal
                            
                        if lon_dir == 'D':  # Doğu (East)
                            lon_decimal = lon_decimal
                        else:  # Batı (West)
                            lon_decimal = -lon_decimal
                            
                        return f"{lat_decimal:.6f}", f"{lon_decimal:.6f}"
                    
                    # English notation: N/S/E/W
                    elif groups[3] in 'NS' and groups[7] in 'EW':
                        lat_deg, lat_min, lat_sec, lat_dir = groups[:4]
                        lon_deg, lon_min, lon_sec, lon_dir = groups[4:]
                        
                        # Convert to decimal degrees
                        lat_decimal = float(lat_deg) + float(lat_min)/60 + float(lat_sec)/3600
                        lon_decimal = float(lon_deg) + float(lon_min)/60 + float(lon_sec)/3600
                        
                        # Apply direction
                        if lat_dir == 'S':
                            lat_decimal = -lat_decimal
                        if lon_dir == 'W':
                            lon_decimal = -lon_decimal
                            
                        return f"{lat_decimal:.6f}", f"{lon_decimal:.6f}"
        
        return None, None
    
    def extract_numeric_value(self, text: str, keywords: List[str]) -> Optional[str]:
        """
        Extract numeric value following specific keywords.
        
        Args:
            text: Text to search in
            keywords: List of keywords to look for
            
        Returns:
            Numeric value as string or None
        """
        text_lower = text.lower()
        
        for keyword in keywords:
            # Find keyword position
            keyword_pos = text_lower.find(keyword.lower())
            if keyword_pos != -1:
                # Look for numeric value with unit after keyword
                after_keyword = text[keyword_pos + len(keyword):keyword_pos + len(keyword) + 100]
                
                # First try to match numeric value with unit
                match = self.numeric_with_unit_pattern.search(after_keyword)
                if match:
                    return match.group(1).replace(',', '.')
                
                # Fallback to simple numeric pattern
                match = self.numeric_pattern.search(after_keyword)
                if match:
                    return match.group(1).replace(',', '.')
        
        return None
    
    def extract_station_data(self, page, station_code: str, year: int) -> Optional[Dict]:
        """
        Extract all required data for a station from a page.
        
        Args:
            page: PyMuPDF page object
            station_code: Detected station code
            year: Year from filename
            
        Returns:
            Dictionary with extracted data or None if extraction fails
        """
        try:
            full_text = page.get_text()
            
            # Extract station name (usually follows the station code on same line)
            lines = full_text.split('\n')
            station_name = ""
            
            # Look for station name in first few lines
            for line in lines[:5]:
                if station_code in line:
                    # Extract everything after the station code
                    parts = line.split(station_code)
                    if len(parts) > 1:
                        station_name = parts[1].strip()
                        break
            
            # Parse coordinates
            latitude, longitude = self.parse_coordinates(full_text)
            
            # Extract discharge data with improved Turkish keywords
            annual_mean_keywords = [
                f'{year} su yılında', 'su yılında', 'yıllık ortalama', 
                'annual mean', 'ortalama', 'm3/sn'
            ]
            
            total_flow_keywords = [
                'yıllık toplam', 'total annual', 'toplam',
                'yıllık toplam akım', 'milyon m3', 'milyon',
                'yıllık toplam akım', 'toplam akım'
            ]
            
            specific_flow_keywords = [
                'özgül debi', 'specific flow', 'özgül',
                'lt/sn/km2', 'lt/sn/km', 'lt/sn',
                'özgül akım'
            ]
            
            annual_mean = self.extract_numeric_value(full_text, annual_mean_keywords)
            total_flow = self.extract_numeric_value(full_text, total_flow_keywords)
            specific_flow = self.extract_numeric_value(full_text, specific_flow_keywords)
            
            return {
                'Year': year,
                'Station_Code': station_code,
                'Station_Name': station_name,
                'Latitude': latitude,
                'Longitude': longitude,
                'Annual_Mean_Discharge': annual_mean,
                'Total_Annual_Flow': total_flow,
                'Specific_Flow': specific_flow
            }
            
        except Exception as e:
            logger.warning(f"Error extracting data for station {station_code}: {e}")
            return None
    
    def process_pdf(self, pdf_path: Path) -> int:
        """
        Process a single PDF file and extract data for target stations.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Number of stations found and processed
        """
        year = self.extract_year_from_filename(pdf_path.name)
        if not year:
            logger.warning(f"Could not extract year from filename: {pdf_path.name}")
            return 0
        
        logger.info(f"Processing {pdf_path.name} (Year: {year})")
        
        try:
            doc = fitz.open(pdf_path)
            stations_found = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get only the second line for fast station code detection
                second_line = self.get_second_line_text(page)
                
                if not second_line:
                    continue
                
                # Check for station code in second line
                station_match = self.station_code_pattern.search(second_line)
                if not station_match:
                    continue
                
                station_code = station_match.group(0)
                
                # Check if this is one of our target stations
                if station_code not in self.target_stations:
                    continue
                
                logger.info(f"Found target station {station_code} on page {page_num + 1}")
                
                # Extract full data for this station
                station_data = self.extract_station_data(page, station_code, year)
                
                if station_data:
                    # Append to CSV
                    with open(self.output_csv, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            station_data['Year'],
                            station_data['Station_Code'],
                            station_data['Station_Name'],
                            station_data['Latitude'],
                            station_data['Longitude'],
                            station_data['Annual_Mean_Discharge'],
                            station_data['Total_Annual_Flow'],
                            station_data['Specific_Flow']
                        ])
                    
                    stations_found += 1
                    logger.info(f"Extracted data for {station_code}: {station_data['Station_Name']}")
            
            doc.close()
            logger.info(f"Completed {pdf_path.name}: {stations_found} stations found")
            return stations_found
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {e}")
            return 0
    
    def run(self):
        """Main execution method."""
        if not self.pdf_directory.exists():
            logger.error(f"PDF directory does not exist: {self.pdf_directory}")
            return
        
        # Find all PDF files
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        pdf_files.extend(self.pdf_directory.glob("*.PDF"))
        
        if not pdf_files:
            logger.error(f"No PDF files found in {self.pdf_directory}")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        logger.info(f"Target stations: {', '.join(sorted(self.target_stations))}")
        
        total_stations = 0
        
        for pdf_file in sorted(pdf_files):
            stations_found = self.process_pdf(pdf_file)
            total_stations += stations_found
        
        logger.info(f"Processing complete! Total stations extracted: {total_stations}")
        logger.info(f"Results saved to: {self.output_csv}")


def main():
    """Main function."""
    # Configuration
    PDF_DIRECTORY = r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi"
    OUTPUT_CSV = "dsi_akim_verileri_2000_2020.csv"
    
    # Create extractor and run
    extractor = DSIExtractor(PDF_DIRECTORY, OUTPUT_CSV)
    extractor.run()


if __name__ == "__main__":
    main()
