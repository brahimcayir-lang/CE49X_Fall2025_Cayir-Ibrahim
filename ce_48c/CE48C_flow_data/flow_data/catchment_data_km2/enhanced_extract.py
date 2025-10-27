# -*- coding: utf-8 -*-
"""
Enhanced extraction with more flexible search patterns
"""

import re
from pathlib import Path
import fitz  # PyMuPDF
import pandas as pd
import sys

YEAR = "2009"
PDF_PATH = f"debi_raporlari/akim_gözlem_yilligi/dsi_{YEAR}.pdf"
OUTPUT_FILE = f"dsi_{YEAR}_catchment_areas.csv"

TARGET_STATIONS = {
    "E22A065","E22A066","D22A093","E22A071","D14A185","E22A054","E22A063",
    "E14A018","D14A162","D14A186","D22A105","E22A053","D14A172","D14A117",
    "E14A027","D22A106","D14A200","E14A002","D14A179","D22A098","D22A159",
    "D14A064","E14A038","D14A201","D14A184","D14A211","D14A208","D14A214",
    "D14A207","D14A141","E22A062","E14A040","D14A215","D14A176","D14A011",
    "D14A188","D14A081"
}

def clean_num(x: str):
    """Convert '210,00' or '210.00' to float."""
    return float(x.strip().replace(",", "."))

def extract_catchments_enhanced(pdf_path):
    doc = fitz.open(pdf_path)
    results = []
    found_codes = set()

    for pno in range(doc.page_count):
        text = doc.load_page(pno).get_text("text")
        if not text.strip():
            continue

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        
        for i, line in enumerate(lines):
            # Look for station code in the line (more flexible pattern)
            # Try multiple patterns
            patterns = [
                r"^([DE]\d{2}A\d{3})\s",  # Original: "D22A093 "
                r"\b([DE]\d{2}A\d{3})\s",  # With word boundary
                r"([DE]\d{2}A\d{3})",      # Anywhere in line
            ]
            
            code = None
            for pattern in patterns:
                m = re.search(pattern, line, re.IGNORECASE)
                if m:
                    test_code = m.group(1).upper()
                    if test_code in TARGET_STATIONS:
                        code = test_code
                        break
            
            if not code:
                continue
            
            if code in found_codes:
                continue  # Skip duplicates
            found_codes.add(code)

            # Look for YAĞIŞ ALANI line near this station (increase search range)
            for j in range(i, min(i + 20, len(lines))):
                line_upper = lines[j].upper()
                
                # Check various forms of "catchment area"
                keywords = [
                    "YAĞIŞ ALANI", "YAGIS ALANI", "YAGIS ALANI:", 
                    "HAVZA ALANI", "CATCHMENT", "HAVZA"
                ]
                
                if any(keyword in line_upper for keyword in keywords):
                    # Try multiple patterns to extract numbers
                    patterns = [
                        r"YA[GĞ]I[SŞ]\s*ALANI\s*:\s*([0-9\.,]+)",
                        r"ALANI\s*:\s*([0-9\.,]+)",
                        r"([0-9\.,]+)\s*km[²2]",
                        r"([0-9\.,]+)",
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, lines[j], flags=re.I)
                        if match:
                            try:
                                val = clean_num(match.group(1))
                                results.append({
                                    "station_code": code,
                                    "catchment_area_km2": val,
                                    "page": pno + 1
                                })
                                print(f"[FOUND] {code}: {val} km2 (p{pno+1}, line: {lines[j][:60]})")
                                break
                            except:
                                pass
                    break

    doc.close()
    return pd.DataFrame(results)

if __name__ == "__main__":
    pdf_path = Path(PDF_PATH)
    if not pdf_path.exists():
        print(f"[ERROR] {pdf_path} not found.")
    else:
        df = extract_catchments_enhanced(pdf_path)
        if df.empty:
            print("[WARN] No YAĞIŞ ALANI found.")
        else:
            # Save to CSV
            df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
            print(f"\n[DONE] Extracted {len(df)} stations -> {OUTPUT_FILE}")
            
            # Show which stations we found
            print(f"\nFound stations: {', '.join(sorted(df['station_code'].unique()))}")
            
            # Show which stations are still missing
            found_set = set(df['station_code'].unique())
            missing = sorted(TARGET_STATIONS - found_set)
            if missing:
                print(f"Missing stations: {', '.join(missing)}")

