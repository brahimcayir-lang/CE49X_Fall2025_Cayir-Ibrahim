#!/usr/bin/env python3
"""
DSİ PDF Complete Data Extractor - Handles index-to-data page mapping correctly
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

class DSIExtractorComplete:
    """Complete DSİ PDF data extractor that handles index-to-data mapping."""
    
    def __init__(self, pdf_directory: str, output_csv: str = "dsi_complete_data.csv"):
        self.pdf_directory = Path(pdf_directory)
        self.output_csv = output_csv
        
        # Target station codes to extract
        self.target_stations = {
            'D22A144', 'D22A145', 'D22A065', 'D22A093', 
            'D22A095', 'D14A149', 'D22A158'
            # Add new stations here - example:
            # 'D14A162', 'D22A105', 'D22A192', 'D22A172'
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
        self.numeric_with_unit_pattern = re.compile(r'(\d+[.,]\d+|\d+)\s*(m3/sn|m³/sn|milyon|m3|lt/sn|mm)', re.IGNORECASE)
        
        # Initialize CSV
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Initialize CSV file with headers."""
        if not os.path.exists(self.output_csv):
            headers = [
                'Year', 'Target_Station_Code', 'Actual_Station_Code', 'Station_Name', 
                'Latitude', 'Longitude', 'Catchment_Area', 'Elevation',
                'Annual_Mean_Discharge', 'Total_Annual_Flow', 'Specific_Flow',
                'Observation_Period', 'Data_Page_Number'
            ]
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
                after_keyword = text[keyword_pos + len(keyword):keyword_pos + len(keyword) + 100]
                
                match = self.numeric_with_unit_pattern.search(after_keyword)
                if match:
                    return match.group(1).replace(',', '.')
                
                match = self.numeric_pattern.search(after_keyword)
                if match:
                    return match.group(1).replace(',', '.')
        
        return None
    
    def build_station_page_mapping(self, doc) -> dict:
        """Build mapping from target station codes to page numbers using index."""
        station_page_map = {}
        
        logger.info("Building station-to-page mapping from index...")
        
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
    
    def extract_station_data_from_page(self, doc, target_station_code: str, page_number: int, year: int) -> dict:
        """Extract complete data from a specific page."""
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
            
            # Extract catchment area
            catchment_area = self.extract_numeric_value(text, ['yağış alanı', 'catchment area'])
            
            # Extract elevation
            elevation = self.extract_numeric_value(text, ['yaklaşık kot', 'elevation', 'kot'])
            
            # Extract discharge data
            annual_mean_keywords = [
                f'{year} su yılında', 'su yılında', 'yıllık ortalama', 
                'annual mean', 'ortalama', 'm3/sn'
            ]
            
            total_flow_keywords = [
                'yıllık toplam', 'total annual', 'toplam',
                'yıllık toplam akım', 'milyon m3', 'milyon'
            ]
            
            specific_flow_keywords = [
                'özgül debi', 'specific flow', 'özgül',
                'lt/sn/km2', 'lt/sn/km', 'lt/sn'
            ]
            
            annual_mean = self.extract_numeric_value(text, annual_mean_keywords)
            total_flow = self.extract_numeric_value(text, total_flow_keywords)
            specific_flow = self.extract_numeric_value(text, specific_flow_keywords)
            
            # Extract observation period
            obs_period = ""
            for line in lines:
                if 'gözlem süresi' in line.lower() or 'observation period' in line.lower():
                    obs_period = line.strip()
                    break
            
            return {
                'Year': year,
                'Target_Station_Code': target_station_code,
                'Actual_Station_Code': actual_station_code,
                'Station_Name': station_name,
                'Latitude': latitude,
                'Longitude': longitude,
                'Catchment_Area': catchment_area,
                'Elevation': elevation,
                'Annual_Mean_Discharge': annual_mean,
                'Total_Annual_Flow': total_flow,
                'Specific_Flow': specific_flow,
                'Observation_Period': obs_period,
                'Data_Page_Number': page_number
            }
            
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
                logger.info(f"Extracting data for {target_station_code} from page {page_number}")
                
                station_data = self.extract_station_data_from_page(doc, target_station_code, page_number, year)
                
                if station_data:
                    # Append to CSV
                    with open(self.output_csv, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            station_data['Year'],
                            station_data['Target_Station_Code'],
                            station_data['Actual_Station_Code'],
                            station_data['Station_Name'],
                            station_data['Latitude'],
                            station_data['Longitude'],
                            station_data['Catchment_Area'],
                            station_data['Elevation'],
                            station_data['Annual_Mean_Discharge'],
                            station_data['Total_Annual_Flow'],
                            station_data['Specific_Flow'],
                            station_data['Observation_Period'],
                            station_data['Data_Page_Number']
                        ])
                    
                    stations_found += 1
                    logger.info(f"Successfully extracted data for {target_station_code}: {station_data['Station_Name']}")
            
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
    OUTPUT_CSV = "dsi_complete_data.csv"
    
    # Create extractor and run
    extractor = DSIExtractorComplete(PDF_DIRECTORY, OUTPUT_CSV)
    extractor.run()

if __name__ == "__main__":
    main()
