# -*- coding: utf-8 -*-
"""
Enhanced extraction for 2009 with better logic
"""

import re
from pathlib import Path
import fitz  # PyMuPDF
import pandas as pd

PDF_PATH = f"debi_raporlari/akim_gözlem_yilligi/dsi_2009.pdf"
OUTPUT_FILE = f"dsi_2009_catchment_areas.csv"

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
    try:
        return float(x.strip().replace(",", ".").replace(" ", ""))
    except:
        return None

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
            # Look for station code
            m = re.search(r"\b([DE]\d{2}A\d{3})\b", line, re.IGNORECASE)
            if not m:
                continue
            
            code = m.group(1).upper()
            if code not in TARGET_STATIONS or code in found_codes:
                continue
            
            # Look for YAĞIŞ ALANI line after the station code (search up to 15 lines ahead)
            for j in range(i, min(i + 15, len(lines))):
                if j == i:
                    continue  # Skip the station line itself
                    
                line_text = lines[j]
                line_upper = line_text.upper()
                
                # Check if this line contains catchment area info
                if any(keyword in line_upper for keyword in ["YAĞIŞ ALANI", "YAGIS ALANI", "HAVZA", "KM2", "KM²"]):
                    # Try to extract a number from this line
                    # Look for patterns like "210,00 km2" or "210.00 km2"
                    match = re.search(r'(\d+[,\.]\d+|\d+)\s*(km2|km²|km)', line_text, re.IGNORECASE)
                    if match:
                        val = clean_num(match.group(1))
                        if val and val > 0:  # Sanity check
                            results.append({
                                "station_code": code,
                                "catchment_area_km2": val,
                                "page": pno + 1
                            })
                            print(f"[FOUND] {code}: {val} km2 (p{pno+1}, context: {line_text[:70]})")
                            found_codes.add(code)
                            break
                    else:
                        # Try to find any number in the line
                        num_match = re.search(r'(\d+[,\.]\d+)', line_text)
                        if num_match:
                            val = clean_num(num_match.group(1))
                            if val and val > 0:
                                results.append({
                                    "station_code": code,
                                    "catchment_area_km2": val,
                                    "page": pno + 1
                                })
                                print(f"[FOUND] {code}: {val} km2 (p{pno+1}, context: {line_text[:70]})")
                                found_codes.add(code)
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
            
            print(f"\nSuccessfully extracted stations: {', '.join(sorted(df['station_code'].unique()))}")

