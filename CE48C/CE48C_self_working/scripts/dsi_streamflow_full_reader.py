#!/usr/bin/env python3
"""
DSİ Streamflow Full Reader (Smart Row Scan System)

A robust Python script to read all DSİ annual streamflow report PDFs between 2000–2020
and extract comprehensive hydrological station data using line-by-line scanning method.

Author: AI Assistant
Date: 2024
"""

import os
import re
import csv
import pdfplumber
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('dsi_extraction.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class DSIStreamflowFullReader:
    """
    DSİ Streamflow Full Reader with Smart Row Scan System
    
    Implements line-by-line scanning method to extract comprehensive
    hydrological station data from DSİ annual streamflow report PDFs.
    """
    
    def __init__(self, pdf_directory: str, output_csv: str = None):
        """
        Initialize the DSİ Streamflow Full Reader.
        
        Args:
            pdf_directory: Path to directory containing DSİ PDF files
            output_csv: Output CSV file path
        """
        self.pdf_directory = Path(pdf_directory)
        
        # Set output path
        if output_csv is None:
            output_dir = Path("C:/Users/Asus/Desktop/bitirme_projesi/outputs")
            output_dir.mkdir(parents=True, exist_ok=True)
            self.output_csv = output_dir / "dsi_2000_2020_rowwise_extracted.csv"
        else:
            self.output_csv = Path(output_csv)
            # Ensure the output directory exists
            self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        
        # Target station codes to extract (exactly as specified)
        self.target_stations = {
            'D14A011', 'D14A117', 'D14A144', 'D14A146', 'D14A149', 'D14A162',
            'D14A172', 'D14A192', 'D14A018', 'D22A093', 'D22A095', 'D22A105',
            'D22A106', 'D22A158', 'E22A054', 'D22A116', 'E22A065'
        }
        
        # Regex patterns for data extraction
        self.station_pattern = re.compile(r"[A-Z]\d{2}[A-Z]\d{3}")
        self.num_pattern = re.compile(r"[\d.,]+")
        
        # Month order as specified
        self.months = [
            "Ekim", "Kasım", "Aralık", "Ocak", "Şubat", "Mart", "Nisan",
            "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül"
        ]
        
        # Initialize CSV with headers
        self._initialize_csv()
        
        # Track processed combinations to avoid duplicates
        self.processed_combinations: Set[Tuple[str, int]] = set()
        
        logger.info(f"Initialized DSİ Streamflow Full Reader")
        logger.info(f"Target stations: {len(self.target_stations)}")
        logger.info(f"Output CSV: {self.output_csv}")
    
    def _initialize_csv(self):
        """Initialize CSV file with comprehensive headers."""
        if not self.output_csv.exists():
            headers = [
                'file', 'year', 'station_code', 'station_name', 'coordinates', 
                'catchment_area_km2', 'annual_avg_flow_m3s'
            ]
            
            # Add monthly flow columns (max, min, avg)
            for month in self.months:
                headers.extend([
                    f'{month.lower()}_flow_max_m3',
                    f'{month.lower()}_flow_min_m3', 
                    f'{month.lower()}_flow_avg_m3'
                ])
            
            # Add LT/SN/Km2 columns
            for month in self.months:
                headers.append(f'{month.lower()}_ltsnkm2')
            
            # Add AKIM mm columns
            for month in self.months:
                headers.append(f'{month.lower()}_akim_mm')
            
            # Add MIL. M3 columns
            for month in self.months:
                headers.append(f'{month.lower()}_milm3')
            
            # Add annual summary columns
            headers.extend(['annual_total_m3', 'mm_total', 'avg_ltsnkm2'])
            
            with open(self.output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            
            logger.info(f"Created CSV file with {len(headers)} columns: {self.output_csv}")
    
    def extract_year_from_filename(self, filename: str) -> Optional[int]:
        """Extract year from PDF filename."""
        year_match = re.search(r'(\d{4})', filename)
        return int(year_match.group(1)) if year_match else None
    
    def is_target_station_page(self, lines: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Check if page contains a target station by examining line 2.
        
        Args:
            lines: List of text lines from the page
            
        Returns:
            Tuple of (is_target, station_code)
        """
        if len(lines) < 2:
            return False, None
        
        line_2 = lines[1].strip()
        station_matches = self.station_pattern.findall(line_2)
        
        for station_code in station_matches:
            if station_code in self.target_stations:
                return True, station_code
        
        return False, None
    
    def extract_header_info(self, lines: List[str], station_code: str) -> Dict[str, str]:
        """
        Extract header information from station page.
        
        Args:
            lines: List of text lines from the page
            station_code: The detected station code
            
        Returns:
            Dictionary with header information
        """
        header_info = {
            'station_code': station_code,
            'station_name': '',
            'coordinates': '',
            'catchment_area_km2': '',
            'annual_avg_flow_m3s': ''
        }
        
        try:
            # Extract station name from line 2 (after station code)
            line_2 = lines[1].strip()
            station_pos = line_2.find(station_code)
            if station_pos != -1:
                station_name_part = line_2[station_pos + len(station_code):].strip()
                # Clean up the station name
                station_name_part = re.sub(r'^\W+', '', station_name_part)  # Remove leading non-word chars
                header_info['station_name'] = station_name_part
            
            # Extract coordinates from line 5
            if len(lines) >= 5:
                coords_line = lines[4].strip()
                header_info['coordinates'] = coords_line
            
            # Extract catchment area (YAĞIŞ ALANI)
            for line in lines[:20]:  # Check first 20 lines
                if 'YAĞIŞ ALANI' in line or 'yağış alanı' in line:
                    numbers = self.num_pattern.findall(line)
                    if numbers:
                        # Convert comma to dot and clean
                        area_value = numbers[0].replace(',', '.')
                        header_info['catchment_area_km2'] = area_value
                    break
            
            # Extract annual average flow (Su Yılında)
            for line in lines[:20]:
                if 'Su Yılında' in line or 'su yılında' in line:
                    numbers = self.num_pattern.findall(line)
                    if numbers:
                        flow_value = numbers[0].replace(',', '.')
                        header_info['annual_avg_flow_m3s'] = flow_value
                    break
        
        except Exception as e:
            logger.warning(f"Error extracting header info for {station_code}: {e}")
        
        return header_info
    
    def extract_flow_tables(self, lines: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Extract flow table data starting from around line 58.
        
        Args:
            lines: List of text lines from the page
            
        Returns:
            Dictionary with flow table data
        """
        flow_data = {}
        
        try:
            # Find the start of flow tables (around line 58)
            table_start = 58
            if len(lines) < table_start:
                table_start = len(lines) // 2
            
            # Look for table start indicators
            for i, line in enumerate(lines[table_start-10:table_start+20]):
                if 'Maks.' in line or 'Min.' in line or 'Ortalama' in line:
                    table_start = table_start - 10 + i
                    break
            
            # Extract data for each row type
            row_types = ['Maks.', 'Min.', 'Ortalama', 'LT/SN/Km2', 'AKIM mm.', 'MİL. M3']
            
            for row_type in row_types:
                flow_data[row_type] = {}
                
                # Find the row with this type
                for i, line in enumerate(lines[table_start:table_start+20]):
                    if row_type in line:
                        # Extract numbers from this line
                        numbers = self.num_pattern.findall(line)
                        
                        # Map numbers to months (assuming 12 months in order)
                        for j, month in enumerate(self.months):
                            if j < len(numbers):
                                value = numbers[j].replace(',', '.')
                                flow_data[row_type][month.lower()] = value
                        break
            
        except Exception as e:
            logger.warning(f"Error extracting flow tables: {e}")
        
        return flow_data
    
    def extract_footer_data(self, lines: List[str]) -> Dict[str, str]:
        """
        Extract footer data (annual summary) from below the double line.
        
        Args:
            lines: List of text lines from the page
            
        Returns:
            Dictionary with footer data
        """
        footer_data = {
            'annual_total_m3': '',
            'mm_total': '',
            'avg_ltsnkm2': ''
        }
        
        try:
            # Find the double line (====)
            double_line_found = False
            
            for i, line in enumerate(lines):
                if '====' in line or '===' in line:
                    double_line_found = True
                    footer_start = i
                    break
            
            if not double_line_found:
                # Look for footer data in the last 10 lines
                footer_start = max(0, len(lines) - 10)
            
            # Extract annual total flow
            for line in lines[footer_start:]:
                if 'SU YILI' in line and 'YILLIK TOPLAM AKIM' in line:
                    numbers = self.num_pattern.findall(line)
                    if numbers:
                        footer_data['annual_total_m3'] = numbers[0].replace(',', '.')
                    break
            
            # Extract mm total
            for line in lines[footer_start:]:
                if 'MM.' in line:
                    numbers = self.num_pattern.findall(line)
                    if numbers:
                        footer_data['mm_total'] = numbers[0].replace(',', '.')
                    break
            
            # Extract avg LT/SN/Km2
            for line in lines[footer_start:]:
                if 'LT/SN/Km2' in line:
                    numbers = self.num_pattern.findall(line)
                    if numbers:
                        footer_data['avg_ltsnkm2'] = numbers[0].replace(',', '.')
                    break
        
        except Exception as e:
            logger.warning(f"Error extracting footer data: {e}")
        
        return footer_data
    
    def extract_station_data_from_page(self, pdf_path: Path, page_num: int, year: int) -> Optional[Dict]:
        """
        Extract complete station data from a single page.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)
            year: Year from filename
            
        Returns:
            Dictionary with complete station data or None
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_num >= len(pdf.pages):
                    return None
                
                page = pdf.pages[page_num]
                text = page.extract_text()
                
                if not text:
                    return None
                
                lines = text.split('\n')
                
                # Check if this is a target station page
                is_target, station_code = self.is_target_station_page(lines)
                
                if not is_target or not station_code:
                    logger.debug(f"⚠️ Skipped: not target station (page {page_num + 1})")
                    return None
                
                # Check for duplicates
                if (station_code, year) in self.processed_combinations:
                    logger.info(f"⚠️ Skipped duplicate: {station_code} in {pdf_path.name}")
                    return None
                
                logger.info(f"✅ {station_code} found in {pdf_path.name} page {page_num + 1}")
                
                # Extract all data
                header_info = self.extract_header_info(lines, station_code)
                flow_tables = self.extract_flow_tables(lines)
                footer_data = self.extract_footer_data(lines)
                
                # Combine all data
                station_data = {
                    'file': pdf_path.name,
                    'year': year,
                    **header_info,
                    **footer_data
                }
                
                # Add flow table data with proper column names
                for row_type in ['Maks.', 'Min.', 'Ortalama', 'LT/SN/Km2', 'AKIM mm.', 'MİL. M3']:
                    if row_type in flow_tables:
                        for month in self.months:
                            month_key = month.lower()
                            value = flow_tables[row_type].get(month_key, '')
                            
                            # Create appropriate column name based on row type
                            if row_type == 'Maks.':
                                column_name = f'{month_key}_flow_max_m3'
                            elif row_type == 'Min.':
                                column_name = f'{month_key}_flow_min_m3'
                            elif row_type == 'Ortalama':
                                column_name = f'{month_key}_flow_avg_m3'
                            elif row_type == 'LT/SN/Km2':
                                column_name = f'{month_key}_ltsnkm2'
                            elif row_type == 'AKIM mm.':
                                column_name = f'{month_key}_akim_mm'
                            elif row_type == 'MİL. M3':
                                column_name = f'{month_key}_milm3'
                            else:
                                continue
                            
                            station_data[column_name] = value
                
                # Mark as processed
                self.processed_combinations.add((station_code, year))
                
                return station_data
        
        except Exception as e:
            logger.error(f"Error processing page {page_num + 1} of {pdf_path.name}: {e}")
            return None
    
    def process_pdf(self, pdf_path: Path) -> int:
        """
        Process a single PDF file.
        
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
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                stations_found = 0
                
                # Process each page
                for page_num in range(total_pages):
                    station_data = self.extract_station_data_from_page(pdf_path, page_num, year)
                    
                    if station_data:
                        # Append to CSV
                        self._append_to_csv(station_data)
                        stations_found += 1
                
                logger.info(f"Completed {pdf_path.name}: {stations_found} stations found")
                return stations_found
        
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path.name}: {e}")
            return 0
    
    def _append_to_csv(self, station_data: Dict):
        """Append station data to CSV file."""
        try:
            # Read existing data to get column order
            if self.output_csv.exists() and self.output_csv.stat().st_size > 0:
                existing_df = pd.read_csv(self.output_csv)
                columns = existing_df.columns.tolist()
            else:
                # Use the order from _initialize_csv
                columns = [
                    'file', 'year', 'station_code', 'station_name', 'coordinates', 
                    'catchment_area_km2', 'annual_avg_flow_m3s'
                ]
                
                # Add monthly flow columns
                for month in self.months:
                    columns.extend([
                        f'{month.lower()}_flow_max_m3',
                        f'{month.lower()}_flow_min_m3', 
                        f'{month.lower()}_flow_avg_m3'
                    ])
                
                # Add other columns
                for month in self.months:
                    columns.append(f'{month.lower()}_ltsnkm2')
                
                for month in self.months:
                    columns.append(f'{month.lower()}_akim_mm')
                
                for month in self.months:
                    columns.append(f'{month.lower()}_milm3')
                
                columns.extend(['annual_total_m3', 'mm_total', 'avg_ltsnkm2'])
            
            # Create row with proper column order
            row_data = []
            for col in columns:
                row_data.append(station_data.get(col, ''))
            
            # Append to CSV
            with open(self.output_csv, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row_data)
        
        except Exception as e:
            logger.error(f"Error appending to CSV: {e}")
    
    def process_all_pdfs(self) -> Dict[str, int]:
        """
        Process all PDF files in the directory.
        
        Returns:
            Dictionary with processing statistics
        """
        if not self.pdf_directory.exists():
            logger.error(f"PDF directory does not exist: {self.pdf_directory}")
            return {}
        
        # Find all PDF files
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        
        if not pdf_files:
            logger.error(f"No PDF files found in {self.pdf_directory}")
            return {}
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        total_stations = 0
        processed_files = 0
        
        # Process each PDF file
        for pdf_file in sorted(pdf_files):
            stations_in_file = self.process_pdf(pdf_file)
            total_stations += stations_in_file
            processed_files += 1
            
            logger.info(f"Progress: {processed_files}/{len(pdf_files)} files, {total_stations} total stations")
        
        logger.info(f"Processing complete!")
        logger.info(f"Files processed: {processed_files}")
        logger.info(f"Total stations found: {total_stations}")
        logger.info(f"Output CSV: {self.output_csv}")
        
        return {
            'files_processed': processed_files,
            'total_stations': total_stations,
            'output_csv': str(self.output_csv)
        }


def main():
    """Main function to run the DSİ Streamflow Full Reader."""
    
    # PDF directory path
    pdf_directory = r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi"
    
    # Output CSV path
    output_csv = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_rowwise_extracted.csv"
    
    logger.info("Starting DSİ Streamflow Full Reader")
    logger.info(f"PDF Directory: {pdf_directory}")
    logger.info(f"Output CSV: {output_csv}")
    
    try:
        # Initialize the reader
        reader = DSIStreamflowFullReader(pdf_directory, output_csv)
        
        # Process all PDFs
        results = reader.process_all_pdfs()
        
        logger.info("=" * 60)
        logger.info("EXTRACTION COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"Files processed: {results.get('files_processed', 0)}")
        logger.info(f"Total stations found: {results.get('total_stations', 0)}")
        logger.info(f"Output file: {results.get('output_csv', 'N/A')}")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
