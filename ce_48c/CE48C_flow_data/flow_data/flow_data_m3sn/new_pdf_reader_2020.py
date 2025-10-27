#!/usr/bin/env python3
"""
new_pdf_reader_2020.py
Extract structured hydrological data from DSI annual streamflow reports (2020).

Usage:
    python new_pdf_reader_2020.py "path/to/dsi_2020.pdf" -o output.csv
"""

import re
import sys
import argparse
from typing import List, Dict, Optional, Tuple
import fitz  # PyMuPDF
import pandas as pd


# Allowed station codes
ALLOWED_STATIONS = {
    'E22A065', 'E22A066', 'D22A093', 'E22A071', 'D14A185', 'E22A054',
    'E22A063', 'E14A018', 'D14A162', 'D14A186', 'D22A105', 'E22A053',
    'D14A172', 'D14A117', 'E14A027', 'D22A106', 'D14A200', 'E14A002',
    'D14A179', 'D22A098', 'D22A159', 'D14A064', 'E14A038', 'D14A201',
    'D14A184', 'D14A211', 'D14A208', 'D14A214', 'D14A207', 'D14A141',
    'E22A062', 'E14A040', 'D14A215', 'D14A176', 'D14A011', 'D14A188', 'D14A081'
}

# Region patterns
REGION_PATTERNS = [
    r"14\.\s*Ye[şs]ilirmak\s*Havzas[ıi]",
    r"14\s*-\s*YE[ŞS][İI]LIRMAK\s*HAVZASI",
    r"22\.\s*Do[ğg]u\s*Karadeniz\s*Havzas[ıi]"
]


def normalize_text(text: str) -> str:
    """Normalize text by replacing special characters."""
    # Replace common Turkish character issues in OCR
    text = text.replace("ı", "i").replace("İ", "I")
    text = text.replace("ğ", "g").replace("Ğ", "G")
    text = text.replace("ü", "u").replace("Ü", "U")
    text = text.replace("ş", "s").replace("Ş", "S")
    text = text.replace("ö", "o").replace("Ö", "O")
    text = text.replace("ç", "c").replace("Ç", "C")
    return text


def is_valid_region(line: str) -> bool:
    """Check if line matches any of the valid region patterns."""
    normalized = normalize_text(line)
    for pattern in REGION_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True
    return False


def extract_number(text: str, allow_negative: bool = False) -> Optional[float]:
    """Extract the first valid number from text, handling commas and dots."""
    if not text or text.strip() in ["KURU", "-----", ""]:
        return 0.0
    
    # Replace comma with dot for decimal separator
    text = text.replace(",", ".")
    
    # Find all numbers in the text
    numbers = re.findall(r"-?\d+\.?\d*", text)
    if numbers:
        try:
            value = float(numbers[0])
            if not allow_negative and value < 0:
                return 0.0
            return value
        except (ValueError, IndexError):
            return 0.0
    return 0.0


def extract_station_info(lines: List[str]) -> Optional[Dict[str, str]]:
    """Extract station code and name from station line.
    
    Expected format: "D22A093 TURNASUYU CUMHURİYET KÖYÜ"
    """
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line starts with a station code pattern
        match = re.match(r"([A-Z]\d{2}[A-Z]\d{3})\s+(.+)", line)
        if match:
            station_code = match.group(1)
            station_name = match.group(2).strip()
            return {"station_code": station_code, "station_name": station_name}
    
    return None


def extract_catchment_info(lines: List[str]) -> Tuple[Optional[float], Optional[float]]:
    """Extract catchment area and estimated elevation.
    
    Expected format: "YAĞIŞ ALANI : 210,00 km2 YAKLAŞIK KOT : 404 m"
    """
    for line in lines:
        if "YAĞIŞ ALANI" in line or "YAGIS ALANI" in line:
            # Extract catchment area
            catchment_match = re.search(r"YA[ĞG]I[ŞS]\s*ALANI\s*:\s*([\d,\.]+)\s*km", line, re.IGNORECASE)
            catchment = None
            if catchment_match:
                catchment_str = catchment_match.group(1).replace(",", ".")
                catchment = float(catchment_str) if catchment_match else None
            
            # Extract elevation
            elevation_match = re.search(r"YAKLA[ŞS]IK\s*KOT\s*:\s*([\d,\.]+)\s*m", line, re.IGNORECASE)
            elevation = None
            if elevation_match:
                elevation_str = elevation_match.group(1).replace(",", ".")
                elevation = float(elevation_str) if elevation_match else None
            
            return catchment, elevation
    
    return None, None


def extract_observation_period(lines: List[str]) -> Optional[str]:
    """Extract observation period.
    
    Expected format: "GÖZLEM SÜRESİ : 06.11.1990 - 30.09.2020"
    """
    for line in lines:
        if "GÖZLEM SÜRESİ" in line or "GOZLEM SURESI" in line:
            match = re.search(r"GÖZLEM\s*SÜRESİ\s*:\s*(.+)", line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    return None


def extract_avg_annual_flow(lines: List[str]) -> Optional[float]:
    """Extract average annual flow for the specific water year.
    
    Expected format: "ORTALAMA AKIMLAR : ... 2020 Su yılında 4.711 m3/sn."
    Extract the number after "Su yılında" (for water year) that is followed by "m3/sn"
    """
    for line in lines:
        if "ORTALAMA AKIMLAR" in line or "ORTALAMA AKIMLAR" in line:
            # Look for pattern: "Su yılında X.XXX m3/sn"
            match = re.search(r"Su\s*y[iİl]+[ıI]+nda\s+([\d,\.]+)\s*m3/?sn", line, re.IGNORECASE)
            if match:
                flow_str = match.group(1).replace(",", ".")
                return float(flow_str)
    return None


def extract_monthly_data(lines: List[str]) -> Dict[str, List[float]]:
    """Extract the 6 consecutive lines of monthly data.
    
    Expected labels: Maks., Min., Ortalama, LT/SN/Km2, AKIM mm., MİL. M3
    Returns dict with keys like 'oct_max_flow_m3s', 'nov_max_flow_m3s', etc.
    """
    monthly_data = {}
    month_short = ['oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep']
    labels = ['Maks.', 'Min.', 'Ortalama', 'LT/SN/Km2', 'AKIM mm.', 'MİL. M3']
    suffixes = ['max_flow_m3s', 'min_flow_m3s', 'avg_flow_m3s', 'lt_sn_km2', 'mm', 'mil_m3']
    
    label_found = {}
    current_label = None
    current_values = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check if this line starts with any of our labels
        label_found = False
        for label in labels:
            if line.startswith(label) or re.match(rf"^{re.escape(label)}\s+", line, re.IGNORECASE):
                # Save previous label if exists
                if current_label and current_values:
                    label_key = labels.index(current_label)
                    suffix = suffixes[label_key]
                    for month_idx, month in enumerate(month_short):
                        field_name = f"{month}_{suffix}"
                        monthly_data[field_name] = current_values[month_idx] if month_idx < len(current_values) else 0.0
                
                # Start new label
                current_label = label
                # Extract numbers from the rest of the line
                rest_of_line = line[len(label):].strip()
                numbers = re.findall(r"[\d,\.]+", rest_of_line)
                current_values = [extract_number(n) for n in numbers]
                label_found = True
                break
        
        if not label_found and current_label:
            # Continue collecting values for current label
            numbers = re.findall(r"[\d,\.]+", line)
            for n in numbers:
                val = extract_number(n)
                current_values.append(val)
    
    # Don't forget the last label
    if current_label and current_values:
        label_key = labels.index(current_label)
        suffix = suffixes[label_key]
        for month_idx, month in enumerate(month_short):
            field_name = f"{month}_{suffix}"
            monthly_data[field_name] = current_values[month_idx] if month_idx < len(current_values) else 0.0
    
    return monthly_data


def extract_annual_totals(lines: List[str]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Extract annual totals from the summary line.
    
    Expected format: "SU YILI (2020) YILLIK TOPLAM AKIM 149.05 MİLYON M3 710 MM. 22.4 LT/SN/Km2"
    Returns: (annual_total_flow_m3, annual_mm, annual_lt_sn_km2)
    Note: annual_total_flow_m3 should be in million m3, not converted to m3
    """
    for line in lines:
        if "SU YILI" in line and "YILLIK TOPLAM AKIM" in line:
            # Extract year
            year_match = re.search(r"SU\s*YILI\s*\((\d+)\)", line, re.IGNORECASE)
            
            # Extract total flow (million m3)
            total_flow_match = re.search(r"YILLIK\s*TOPLAM\s*AKIM\s*([\d,\.]+)\s*MİLYON\s*M3", line, re.IGNORECASE)
            total_flow = None
            if total_flow_match:
                total_flow_str = total_flow_match.group(1).replace(",", ".")
                total_flow = float(total_flow_str)  # Keep as million m3
            
            # Extract mm
            mm_match = re.search(r"([\d,\.]+)\s*MM\.", line, re.IGNORECASE)
            mm = None
            if mm_match:
                mm_str = mm_match.group(1).replace(",", ".")
                mm = float(mm_str)
            
            # Extract LT/SN/Km2
            lt_sn_km2_match = re.search(r"([\d,\.]+)\s*LT/?SN?/?Km2", line, re.IGNORECASE)
            lt_sn_km2 = None
            if lt_sn_km2_match:
                lt_sn_km2_str = lt_sn_km2_match.group(1).replace(",", ".")
                lt_sn_km2 = float(lt_sn_km2_str)
            
            return total_flow, mm, lt_sn_km2
    
    return None, None, None


def parse_station_page(page_text: str, page_num: int, filename: str, year: str) -> Optional[Dict]:
    """Parse a complete station page and extract all data."""
    lines = [line.strip() for line in page_text.split('\n') if line.strip()]
    
    if not lines:
        return None
    
    # Check if this is a valid region
    if not is_valid_region(lines[0]):
        return None
    
    # Extract region name (remove the number and period)
    region_name_match = re.match(r"\d+\.\s*(.+)", lines[0])
    region_name = region_name_match.group(1).strip() if region_name_match else lines[0]
    
    # Extract station info (should be in second non-empty line or nearby)
    station_info = extract_station_info(lines[1:5])  # Check next few lines
    if not station_info:
        return None
    
    station_code = station_info['station_code']
    station_name = station_info['station_name']
    
    # Check if station is in allowed list
    if station_code not in ALLOWED_STATIONS:
        print(f"  Page {page_num}: Station {station_code} not in allowed list - SKIPPED")
        return None
    
    # Extract catchment and elevation
    catchment_area, estimated_elevation = extract_catchment_info(lines)
    
    # Extract observation period
    observation_period = extract_observation_period(lines)
    
    # Extract average annual flow
    avg_annual_flow = extract_avg_annual_flow(lines)
    
    # Extract monthly data
    monthly_data = extract_monthly_data(lines)
    
    # Extract annual totals
    annual_total_flow, annual_mm, annual_lt_sn_km2 = extract_annual_totals(lines)
    
    # Build result dictionary
    result = {
        'file': filename,
        'page': page_num,
        'region_name': region_name,
        'year': year,
        'station_code': station_code,
        'station_name': station_name,
        'catchment_area_km2': catchment_area,
        'estimated_elevation_m': estimated_elevation,
        'observation_period': observation_period,
        'avg_annual_flow_m3s': avg_annual_flow,
        'annual_total_flow_m3': annual_total_flow,  # in million m3
        'annual_mm': annual_mm,
        'annual_lt_sn_km2': annual_lt_sn_km2,
        **monthly_data
    }
    
    return result


def process_pdf(pdf_path: str, output_csv: str):
    """Main function to process the PDF and extract data."""
    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    
    # Extract year from filename
    year_match = re.search(r"(\d{4})\.pdf$", pdf_path)
    year = year_match.group(1) if year_match else "2020"
    
    all_results = []
    total_pages = len(doc)
    
    print(f"Processing {total_pages} pages...")
    
    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text()
        
        # Check if this page has a valid region
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            print(f"Page {page_num + 1}: Empty page - SKIPPED")
            continue
        
        if not is_valid_region(lines[0]):
            print(f"Page {page_num + 1}: Region '{lines[0][:50]}...' not valid - SKIPPED")
            continue
        
        # Try to parse as a station page
        result = parse_station_page(text, page_num + 1, pdf_path, year)
        
        if result:
            all_results.append(result)
            print(f"Page {page_num + 1}: Station {result['station_code']} - EXTRACTED")
        else:
            print(f"Page {page_num + 1}: Valid region but could not extract station data - SKIPPED")
    
    doc.close()
    
    # Save to CSV
    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"\nExtracted {len(all_results)} stations")
        print(f"Saved to: {output_csv}")
    else:
        print("\nNo data extracted!")
    
    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Extract hydrological data from DSI annual streamflow reports"
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("-o", "--output", default="extracted_data.csv",
                       help="Output CSV file (default: extracted_data.csv)")
    
    args = parser.parse_args()
    
    try:
        process_pdf(args.pdf_path, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

