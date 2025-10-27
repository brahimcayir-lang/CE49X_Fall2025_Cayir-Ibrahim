#!/usr/bin/env python3
"""
DSİ PDF Debug Viewer - Shows raw text content from PDF files
"""

import fitz  # PyMuPDF
import csv
from pathlib import Path
import re

def debug_pdf_content(pdf_path, output_file="pdf_debug_output.csv"):
    """Extract and save raw text content from PDF for debugging."""
    
    print(f"Debugging PDF: {pdf_path}")
    
    try:
        doc = fitz.open(pdf_path)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Page_Number', 'Line_Number', 'Text_Content'])
            
            for page_num in range(min(10, len(doc))):  # Only first 10 pages for debugging
                page = doc[page_num]
                text = page.get_text()
                lines = text.split('\n')
                
                print(f"\n=== PAGE {page_num + 1} ===")
                print(f"Total lines: {len(lines)}")
                
                for line_num, line in enumerate(lines[:20]):  # First 20 lines per page
                    line = line.strip()
                    if line:  # Only non-empty lines
                        writer.writerow([page_num + 1, line_num + 1, line])
                        print(f"Line {line_num + 1}: {line}")
                        
                        # Check for station codes
                        station_match = re.search(r'[A-Z]\d{2}[A-Z]\d{3}', line)
                        if station_match:
                            print(f"  *** STATION CODE FOUND: {station_match.group(0)} ***")
                
                print(f"End of page {page_num + 1}")
                print("-" * 50)
        
        doc.close()
        print(f"\nDebug output saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

def main():
    # Test with 2020 PDF
    pdf_path = r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi\dsi_2020.pdf"
    
    if Path(pdf_path).exists():
        debug_pdf_content(pdf_path, "dsi_2020_debug.csv")
    else:
        print(f"PDF file not found: {pdf_path}")
        
        # Try to find any PDF in the directory
        pdf_dir = Path(r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi")
        if pdf_dir.exists():
            pdf_files = list(pdf_dir.glob("*.pdf"))
            if pdf_files:
                print(f"Found PDF files: {[f.name for f in pdf_files[:5]]}")
                # Use the first available PDF
                debug_pdf_content(pdf_files[0], "pdf_debug_output.csv")
            else:
                print("No PDF files found in directory")
        else:
            print("PDF directory does not exist")

if __name__ == "__main__":
    main()
