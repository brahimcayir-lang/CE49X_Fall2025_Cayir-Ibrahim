# -*- coding: utf-8 -*-
"""
Scan for target stations in PDF to see what's actually there
"""

import re
from pathlib import Path
import fitz
import sys

YEAR = "2009"
PDF_PATH = f"debi_raporlari/akim_gözlem_yilligi/dsi_{YEAR}.pdf"

TARGET_STATIONS = {
    "E22A065","E22A066","D22A093","E22A071","D14A185","E22A054","E22A063",
    "E14A018","D14A162","D14A186","D22A105","E22A053","D14A172","D14A117",
    "E14A027","D22A106","D14A200","E14A002","D14A179","D22A098","D22A159",
    "D14A064","E14A038","D14A201","D14A184","D14A211","D14A208","D14A214",
    "D14A207","D14A141","E22A062","E14A040","D14A215","D14A176","D14A011",
    "D14A188","D14A081"
}

def scan_for_stations(pdf_path):
    doc = fitz.open(pdf_path)
    found_stations = {}
    
    for pno in range(doc.page_count):
        text = doc.load_page(pno).get_text("text")
        if not text.strip():
            continue
        
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        
        for i, line in enumerate(lines):
            # Look for any target station code
            m = re.search(r"\b([DE]\d{2}A\d{3})\b", line, re.IGNORECASE)
            if m:
                code = m.group(1).upper()
                if code in TARGET_STATIONS and code not in found_stations:
                    # Look at the next 5 lines for context
                    context = '\n'.join(lines[i:min(i+6, len(lines))])
                    found_stations[code] = {
                        "page": pno + 1,
                        "context": context[:200]
                    }
                    print(f"[FOUND] {code} on page {pno+1}")
    
    doc.close()
    return found_stations

if __name__ == "__main__":
    pdf_path = Path(PDF_PATH)
    if not pdf_path.exists():
        print(f"[ERROR] {pdf_path} not found.")
    else:
        found = scan_for_stations(pdf_path)
        print(f"\nTotal stations found: {len(found)}")
        print(f"Missing: {len(TARGET_STATIONS) - len(found)}")
        
        if found:
            print("\nFound stations:")
            for code in sorted(found.keys()):
                print(f"  {code}: page {found[code]['page']}")
        
        missing = sorted(TARGET_STATIONS - set(found.keys()))
        if missing:
            print(f"\nMissing stations ({len(missing)}):")
            print(f"  {', '.join(missing)}")

