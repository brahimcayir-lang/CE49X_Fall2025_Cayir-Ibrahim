#!/usr/bin/env python3
"""
DSİ Monthly Data Extractor - Extracts monthly statistics directly from flow tables
"""

import fitz  # PyMuPDF
import csv
import os
from pathlib import Path
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DSIMonthlyExtractor:
    """Extracts monthly hydrological data directly from DSİ flow tables."""
    
    def __init__(self, pdf_directory: str, output_csv: str = "dsi_monthly_data_2000_2020.csv"):
        self.pdf_directory = Path(pdf_directory)
        self.output_csv = output_csv
        
        # Target station codes
        self.target_stations = {
            'D22A144', 'D22A145', 'D22A065', 'D22A093', 
            'D22A095', 'D14A149', 'D22A158'
        }
        
        # Regex patterns
        self.station_code_pattern = re.compile(r'[A-Z]\d{2}[A-Z]\d{3}')
        
        # Coordinate patterns
        self.coord_patterns = [
            re.compile(r'(\d{1,2})°(\d{1,2})\'(\d{1,2})"\s*(Doğu|Batı)\s*-\s*(\d{1,2})°(\d{1,2})\'(\d{1,2})"\s*(Kuzey|Güney)'),
            re.compile(r'(\d{1,2})°(\d{1,2})\'(\d{1,2})"([KD])\s+(\d{1,2})°(\d{1,2})\'(\d{1,2})"([KD])'),
            re.compile(r'(\d{1,2})°(\d{1,2})\'(\d{1,2})"([NS])\s+(\d{1,2})°(\d{1,2})\'(\d{1,2})"([EW])')
        ]
        
        # Numeric patterns
        self.numeric_pattern = re.compile(r'(\d+[.,]\d+|\d+)')
        
        # Month names in Turkish
        self.months = [
            'Ekim', 'Kasım', 'Aralık', 'Ocak', 'Şubat', 'Mart',
            'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül'
        ]
        
        # Initialize CSV
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Initialize CSV file with comprehensive headers."""
        if not os.path.exists(self.output_csv):
            headers = [
                'Year', 'Station_Code', 'Station_Name', 'Latitude', 'Longitude', 
                'Catchment_Area', 'Elevation', 'Observation_Period', 'Data_Page_Number'
            ]
            
            # Add monthly columns for each statistic type
            for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
                headers.extend([
                    f'{month}_Mean', f'{month}_Max', f'{month}_Min',
                    f'{month}_MilM3', f'{month}_mm', f'{month}_LtSnKm2'
                ])
            
            with open(self.output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            logger.info(f"Created CSV file: {self.output_csv}")
    
    def extract_year_from_filename(self, filename: str) -> int:
        """Extract year from PDF filename."""
        year_match = re.search(r'(\d{4})', filename)
        return int(year_match.group(1)) if year_match else None
    
    def parse_coordinates(self, text: str) -> tuple:
        """Parse coordinates from text."""
        for pattern in self.coord_patterns:
            match = pattern.search(text)
            if match:
                groups = match.groups()
                
                if len(groups) == 8:
                    # Turkish notation: "26°34'20" Doğu - 41°38'50" Kuzey"
                    if groups[3] in ['Doğu', 'Batı'] and groups[7] in ['Kuzey', 'Güney']:
                        lon_deg, lon_min, lon_sec, lon_dir = groups[:4]
                        lat_deg, lat_min, lat_sec, lat_dir = groups[4:]
                        
                        lat_decimal = float(lat_deg) + float(lat_min)/60 + float(lat_sec)/3600
                        lon_decimal = float(lon_deg) + float(lon_min)/60 + float(lon_sec)/3600
                        
                        if lat_dir == 'Güney':
                            lat_decimal = -lat_decimal
                        if lon_dir == 'Batı':
                            lon_decimal = -lon_decimal
                            
                        return f"{lat_decimal:.6f}", f"{lon_decimal:.6f}"
        
        return None, None
    
    def extract_numeric_value(self, text: str, keywords: list) -> str:
        """Extract numeric value following keywords."""
        text_lower = text.lower()
        
        for keyword in keywords:
            keyword_pos = text_lower.find(keyword.lower())
            if keyword_pos != -1:
                after_keyword = text[keyword_pos + len(keyword):keyword_pos + len(keyword) + 50]
                match = self.numeric_pattern.search(after_keyword)
                if match:
                    return match.group(1).replace(',', '.')
        
        return None
    
    def build_station_page_mapping(self, doc) -> dict:
        """Build mapping from target station codes to page numbers."""
        station_page_map = {}
        
        logger.info("Building comprehensive station-to-page mapping...")
        
        # Search more thoroughly for missing stations
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            lines = text.split('\n')
            
            for line in lines:
                station_matches = self.station_code_pattern.findall(line)
                for station_code in station_matches:
                    if station_code in self.target_stations:
                        # Extract page number from the end of the line
                        page_match = re.search(r'(\d+)\s*$', line.strip())
                        if page_match:
                            referenced_page = int(page_match.group(1))
                            station_page_map[station_code] = referenced_page
                            logger.info(f"Found {station_code} → page {referenced_page}")
        
        return station_page_map
    
    def extract_monthly_data_from_table(self, text: str) -> dict:
        """Extract monthly statistics from flow table."""
        monthly_data = {}
        
        lines = text.split('\n')
        
        # Find the flow table section
        table_start = -1
        for i, line in enumerate(lines):
            if 'akımlar' in line.lower() and ('ekim' in line.lower() or 'kasım' in line.lower()):
                table_start = i
                break
        
        if table_start == -1:
            logger.warning("Flow table not found")
            return monthly_data
        
        # Look for summary rows (Ortalama, Maks., Min., etc.)
        summary_rows = {}
        for i in range(table_start, min(table_start + 100, len(lines))):
            line = lines[i].strip()
            
            if 'ortalama' in line.lower() or 'average' in line.lower():
                summary_rows['mean'] = line
            elif 'maks.' in line.lower() or 'max' in line.lower():
                summary_rows['max'] = line
            elif 'min.' in line.lower():
                summary_rows['min'] = line
            elif 'mİl. m3' in line.upper() or 'milyon' in line.lower():
                summary_rows['mil_m3'] = line
            elif 'akim mm.' in line.lower() or 'mm.' in line.lower():
                summary_rows['mm'] = line
            elif 'lt/sn/km2' in line.lower() or 'lt/sn/km' in line.lower():
                summary_rows['lt_sn_km2'] = line
        
        # Extract values for each month
        month_columns = {}
        for month in self.months:
            month_columns[month] = {}
        
        # Parse each summary row
        for row_type, row_content in summary_rows.items():
            # Split by whitespace and extract numeric values
            values = re.findall(r'(\d+[.,]\d+|\d+)', row_content)
            
            if len(values) >= 12:  # Should have 12 monthly values
                for i, month in enumerate(self.months):
                    if i < len(values):
                        try:
                            val = float(values[i].replace(',', '.'))
                            month_columns[month][row_type] = val
                        except ValueError:
                            month_columns[month][row_type] = None
        
        # Convert to final format
        month_mapping = {
            'Ekim': 'Oct', 'Kasım': 'Nov', 'Aralık': 'Dec',
            'Ocak': 'Jan', 'Şubat': 'Feb', 'Mart': 'Mar',
            'Nisan': 'Apr', 'Mayıs': 'May', 'Haziran': 'Jun',
            'Temmuz': 'Jul', 'Ağustos': 'Aug', 'Eylül': 'Sep'
        }
        
        for tr_month, en_month in month_mapping.items():
            monthly_data[en_month] = {
                'mean': month_columns[tr_month].get('mean'),
                'max': month_columns[tr_month].get('max'),
                'min': month_columns[tr_month].get('min'),
                'mil_m3': month_columns[tr_month].get('mil_m3'),
                'mm': month_columns[tr_month].get('mm'),
                'lt_sn_km2': month_columns[tr_month].get('lt_sn_km2')
            }
        
        return monthly_data
    
    def extract_station_data_from_page(self, doc, target_station_code: str, page_number: int, year: int) -> dict:
        """Extract complete monthly data from a specific page."""
        try:
            page = doc[page_number - 1]  # Convert to 0-based index
            text = page.get_text()
            lines = text.split('\n')
            
            # Find actual station code and name
            actual_station_code = None
            station_name = ""
            
            for line in lines[:10]:
                station_matches = self.station_code_pattern.findall(line)
                if station_matches:
                    actual_station_code = station_matches[0]
                    # Extract station name
                    parts = line.split(actual_station_code)
                    if len(parts) > 1:
                        station_name = parts[1].strip()
                    break
            
            # Parse coordinates
            latitude, longitude = self.parse_coordinates(text)
            
            # Extract catchment area and elevation
            catchment_area = self.extract_numeric_value(text, ['yağış alanı', 'catchment area'])
            elevation = self.extract_numeric_value(text, ['yaklaşık kot', 'elevation', 'kot'])
            
            # Extract observation period
            obs_period = ""
            for line in lines:
                if 'gözlem süresi' in line.lower() or 'observation period' in line.lower():
                    obs_period = line.strip()
                    break
            
            # Extract monthly data from flow table
            monthly_data = self.extract_monthly_data_from_table(text)
            
            # Build result dictionary
            result = {
                'Year': year,
                'Station_Code': target_station_code,  # Use target code as requested
                'Station_Name': station_name,
                'Latitude': latitude,
                'Longitude': longitude,
                'Catchment_Area': catchment_area,
                'Elevation': elevation,
                'Observation_Period': obs_period,
                'Data_Page_Number': page_number
            }
            
            # Add monthly data
            for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
                month_data = monthly_data.get(month, {})
                result[f'{month}_Mean'] = month_data.get('mean')
                result[f'{month}_Max'] = month_data.get('max')
                result[f'{month}_Min'] = month_data.get('min')
                result[f'{month}_MilM3'] = month_data.get('mil_m3')
                result[f'{month}_mm'] = month_data.get('mm')
                result[f'{month}_LtSnKm2'] = month_data.get('lt_sn_km2')
            
            return result
            
        except Exception as e:
            logger.warning(f"Error extracting data for {target_station_code} from page {page_number}: {e}")
            return None
    
    def process_pdf(self, pdf_path: Path) -> int:
        """Process a single PDF file."""
        year = self.extract_year_from_filename(pdf_path.name)
        if not year:
            logger.warning(f"Could not extract year from filename: {pdf_path.name}")
            return 0
        
        logger.info(f"Processing {pdf_path.name} (Year: {year})")
        
        try:
            doc = fitz.open(pdf_path)
            
            # Build station-to-page mapping
            station_page_map = self.build_station_page_mapping(doc)
            
            stations_found = 0
            
            # Extract data from mapped pages
            for target_station_code, page_number in station_page_map.items():
                logger.info(f"Extracting monthly data for {target_station_code} from page {page_number}")
                
                station_data = self.extract_station_data_from_page(doc, target_station_code, page_number, year)
                
                if station_data:
                    # Append to CSV
                    with open(self.output_csv, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        
                        # Build row data
                        row_data = [
                            station_data['Year'],
                            station_data['Station_Code'],
                            station_data['Station_Name'],
                            station_data['Latitude'],
                            station_data['Longitude'],
                            station_data['Catchment_Area'],
                            station_data['Elevation'],
                            station_data['Observation_Period'],
                            station_data['Data_Page_Number']
                        ]
                        
                        # Add monthly data
                        for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
                            row_data.extend([
                                station_data[f'{month}_Mean'],
                                station_data[f'{month}_Max'],
                                station_data[f'{month}_Min'],
                                station_data[f'{month}_MilM3'],
                                station_data[f'{month}_mm'],
                                station_data[f'{month}_LtSnKm2']
                            ])
                        
                        writer.writerow(row_data)
                    
                    stations_found += 1
                    logger.info(f"Successfully extracted monthly data for {target_station_code}: {station_data['Station_Name']}")
            
            # Handle missing stations
            missing_stations = self.target_stations - set(station_page_map.keys())
            for missing_station in missing_stations:
                logger.warning(f"Station {missing_station} not found in {pdf_path.name}")
                
                # Add N/A row for missing station
                with open(self.output_csv, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    row_data = [year, missing_station, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']
                    # Add N/A for all monthly data
                    for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
                        row_data.extend(['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'])
                    writer.writerow(row_data)
            
            doc.close()
            logger.info(f"Completed {pdf_path.name}: {stations_found} stations found, {len(missing_stations)} missing")
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
    OUTPUT_CSV = "dsi_monthly_data_2000_2020.csv"
    
    # Create extractor and run
    extractor = DSIMonthlyExtractor(PDF_DIRECTORY, OUTPUT_CSV)
    extractor.run()

if __name__ == "__main__":
    main()
