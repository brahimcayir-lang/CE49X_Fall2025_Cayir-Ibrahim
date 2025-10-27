#!/usr/bin/env python3
"""
PDF Coordinates Extractor

This script extracts coordinates data from PDF files containing hydrological station information.
The expected structure is:
- Line 1: Region name
- Line 2: Station code + Station name  
- Skip 2 lines
- Next line: Coordinates (e.g., "41°15'30" Doğu - 41°13'51" Kuzey")

Output: CSV file with columns: file_name, page, region, station_code, station_name, coordinates
"""

import os
import re
import csv
import pdfplumber
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class PDFCoordinatesExtractor:
    """Extract coordinates data from PDF files with hydrological station information."""
    
    def __init__(self, pdf_directory: str, output_csv: str):
        """
        Initialize the extractor.
        
        Args:
            pdf_directory: Path to directory containing PDF files
            output_csv: Path for output CSV file
        """
        self.pdf_directory = Path(pdf_directory)
        self.output_csv = output_csv
        self.extracted_data = []
        
        # Target regions - only process pages with these regions
        self.target_regions = {
            "22. Doğu Karadeniz Havzası",
            "22. Dogu Karadeniz Havzasi",  # Alternative spelling
            "14. Yeşilırmak Havzası",
            "14. Yesilirmak Havzasi"  # Alternative spelling
        }
        
        # Coordinate pattern to match formats like "41°15'30" Doğu - 41°13'51" Kuzey"
        self.coordinate_pattern = re.compile(
            r'(\d+°\d+\'\d+(?:\.\d+)?\"?)\s*(?:Doğu|D)\s*-\s*(\d+°\d+\'\d+(?:\.\d+)?\"?)\s*(?:Kuzey|K)',
            re.IGNORECASE
        )
        
        # Station code pattern (e.g., D22A006, E22A054)
        self.station_code_pattern = re.compile(r'([A-Z]\d{2}[A-Z]\d{3})')
    
    def is_target_region(self, region_line: str) -> bool:
        """
        Check if the region line matches our target regions.
        
        Args:
            region_line: First line of the page (region name)
            
        Returns:
            True if region matches target regions, False otherwise
        """
        region_line = region_line.strip()
        return region_line in self.target_regions
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[List[str]]:
        """
        Extract text from PDF file, returning list of pages with lines.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of pages, each page is a list of lines
        """
        pages_text = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        pages_text.append(lines)
                    else:
                        pages_text.append([])
                        
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return []
            
        return pages_text
    
    def parse_station_line(self, line: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse station code and name from line.
        
        Args:
            line: Text line containing station information
            
        Returns:
            Tuple of (station_code, station_name)
        """
        # Find station code
        station_match = self.station_code_pattern.search(line)
        if not station_match:
            return None, None
            
        station_code = station_match.group(1)
        
        # Extract station name (everything after the station code)
        station_name = line[station_match.end():].strip()
        
        return station_code, station_name
    
    def find_coordinates(self, lines: List[str], start_index: int = 0) -> Optional[str]:
        """
        Find coordinates in the lines starting from given index.
        
        Args:
            lines: List of text lines
            start_index: Index to start searching from
            
        Returns:
            Coordinates string if found, None otherwise
        """
        for i in range(start_index, len(lines)):
            line = lines[i]
            match = self.coordinate_pattern.search(line)
            if match:
                return line.strip()
        return None
    
    def extract_page_data(self, pdf_path: Path, page_num: int, lines: List[str]) -> Optional[Dict]:
        """
        Extract data from a single page.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (1-indexed)
            lines: List of text lines from the page
            
        Returns:
            Dictionary with extracted data or None if not found
        """
        if len(lines) < 6:  # Need at least 6 lines for the expected structure
            return None
            
        # Line 1: Region name - check if it's a target region
        region = lines[0].strip()
        if not self.is_target_region(region):
            return None  # Skip pages that don't match target regions
        
        # Line 2: Station code + Station name
        station_code, station_name = self.parse_station_line(lines[1])
        if not station_code:
            return None
            
        # Skip 2 lines (lines 2 and 3 are already processed, skip lines 3 and 4)
        # Look for coordinates starting from line 5 (index 4)
        coordinates = self.find_coordinates(lines, 4)
        if not coordinates:
            return None
            
        return {
            'file_name': pdf_path.name,
            'page': page_num,
            'region': region,
            'station_code': station_code,
            'station_name': station_name,
            'coordinates': coordinates
        }
    
    def process_pdf(self, pdf_path: Path) -> List[Dict]:
        """
        Process a single PDF file and extract coordinates data.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of extracted data dictionaries
        """
        print(f"Processing: {pdf_path.name}")
        pages_text = self.extract_text_from_pdf(pdf_path)
        
        extracted_data = []
        skipped_pages = 0
        
        for page_num, lines in enumerate(pages_text, 1):
            if not lines:  # Skip empty pages
                skipped_pages += 1
                continue
                
            # Quick check: if first line doesn't match target regions, skip immediately
            if lines and not self.is_target_region(lines[0].strip()):
                skipped_pages += 1
                continue
                
            page_data = self.extract_page_data(pdf_path, page_num, lines)
            if page_data:
                extracted_data.append(page_data)
                print(f"  ✅ Found data on page {page_num}: {page_data['station_code']} - {page_data['station_name']}")
            else:
                skipped_pages += 1
        
        print(f"  📊 Processed {len(pages_text)} pages, found {len(extracted_data)} target pages, skipped {skipped_pages} pages")
        return extracted_data
    
    def process_all_pdfs(self) -> List[Dict]:
        """
        Process all PDF files in the directory.
        
        Returns:
            List of all extracted data
        """
        if not self.pdf_directory.exists():
            print(f"Error: Directory {self.pdf_directory} does not exist")
            return []
            
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in {self.pdf_directory}")
            return []
            
        print(f"Found {len(pdf_files)} PDF files to process")
        
        all_data = []
        for pdf_path in pdf_files:
            try:
                pdf_data = self.process_pdf(pdf_path)
                all_data.extend(pdf_data)
            except Exception as e:
                print(f"Error processing {pdf_path.name}: {e}")
                
        return all_data
    
    def save_to_csv(self, data: List[Dict]) -> None:
        """
        Save extracted data to CSV file.
        
        Args:
            data: List of extracted data dictionaries
        """
        if not data:
            print("No data to save")
            return
            
        fieldnames = ['file_name', 'page', 'region', 'station_code', 'station_name', 'coordinates']
        
        try:
            with open(self.output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
                
            print(f"✅ Data saved to {self.output_csv}")
            print(f"📊 Total records: {len(data)}")
            
        except Exception as e:
            print(f"Error saving CSV: {e}")
    
    def run(self) -> None:
        """Run the complete extraction process."""
        print("🚀 Starting PDF coordinates extraction...")
        
        # Process all PDFs
        all_data = self.process_all_pdfs()
        
        if all_data:
            # Save to CSV
            self.save_to_csv(all_data)
            
            # Print summary
            print("\n📋 Summary:")
            print(f"Total files processed: {len(set(item['file_name'] for item in all_data))}")
            print(f"Total pages with data: {len(all_data)}")
            print(f"Unique stations found: {len(set(item['station_code'] for item in all_data))}")
            
            # Show sample data
            if all_data:
                print("\n📄 Sample extracted data:")
                for i, item in enumerate(all_data[:3]):  # Show first 3 records
                    print(f"  {i+1}. {item['file_name']} (page {item['page']})")
                    print(f"     Region: {item['region']}")
                    print(f"     Station: {item['station_code']} - {item['station_name']}")
                    print(f"     Coordinates: {item['coordinates']}")
                    print()
        else:
            print("❌ No data extracted")


def main():
    """Main function to run the extractor."""
    # Configuration - using the specific PDF file you mentioned
    pdf_file = r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi\dsi_2020.pdf"
    output_csv = r"C:\Users\Asus\Desktop\CE 49X\CE49X_SELF_WORKING\extracted_coordinates_dsi_2020.csv"
    
    # Check if PDF file exists
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        print("Please check the file path and try again.")
        return
    
    print(f"🎯 Processing specific PDF file: {os.path.basename(pdf_file)}")
    print(f"📁 Target regions: 22. Doğu Karadeniz Havzası, 14. Yeşilırmak Havzası")
    print(f"💾 Output CSV: {output_csv}")
    print()
    
    # Initialize and run extractor with single file
    extractor = PDFCoordinatesExtractor(os.path.dirname(pdf_file), output_csv)
    
    # Process only the specific PDF file
    try:
        pdf_path = Path(pdf_file)
        pdf_data = extractor.process_pdf(pdf_path)
        
        if pdf_data:
            extractor.save_to_csv(pdf_data)
            
            # Print summary
            print("\n📋 Summary:")
            print(f"Total pages with target regions: {len(pdf_data)}")
            print(f"Unique stations found: {len(set(item['station_code'] for item in pdf_data))}")
            
            # Show all extracted data
            print("\n📄 All extracted data:")
            for i, item in enumerate(pdf_data, 1):
                print(f"  {i}. Page {item['page']}")
                print(f"     Region: {item['region']}")
                print(f"     Station: {item['station_code']} - {item['station_name']}")
                print(f"     Coordinates: {item['coordinates']}")
                print()
        else:
            print("❌ No data extracted from target regions")
            
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")


if __name__ == "__main__":
    main()
