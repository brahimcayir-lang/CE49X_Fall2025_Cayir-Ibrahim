# -*- coding: utf-8 -*-
"""
Extract the full 7-line flow table (Maks., Min., Ortalama, LT/SN/Km2,
AKIM mm., MİL. M3, and SU YILI annual line)
from dsi_XXXX.pdf for each target station for all years (2005-2020).
"""

import re
from pathlib import Path
import fitz  # PyMuPDF
import pandas as pd

YEARS = range(2005, 2021)  # 2005 to 2020

TARGET_STATIONS = {
    "E22A065","E22A066","D22A093","E22A071","D14A185","E22A054","E22A063",
    "E14A018","D14A162","D14A186","D22A105","E22A053","D14A172","D14A117",
    "E14A027","D22A106","D14A200","E14A002","D14A179","D22A098","D22A159",
    "D14A064","E14A038","D14A201","D14A184","D14A211","D14A208","D14A214",
    "D14A207","D14A141","E22A062","E14A040","D14A215","D14A176","D14A011",
    "D14A188","D14A081"
}

def clean_num(x):
    return float(x.replace(",", ".").strip()) if re.match(r"[0-9,\.]+", x.strip()) else 0.0

def extract_table(pdf_path):
    doc = fitz.open(pdf_path)
    results = []
    for pno in range(doc.page_count):
        text = doc.load_page(pno).get_text("text")
        if not text.strip():
            continue

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for i, line in enumerate(lines):
            # Station header
            m = re.match(r"^([DE]\d{2}A\d{3})\s", line)
            if not m:
                continue
            code = m.group(1).upper()
            if code not in TARGET_STATIONS:
                continue

            # Find where the flow table starts
            for j in range(i, len(lines)):
                if lines[j].startswith("Maks"):
                    table_lines = lines[j:j+8]  # Maks. -> SU YILI
                    block = "\n".join(table_lines)
                    # Optional: parse each line separately if needed
                    results.append({
                        "station_code": code,
                        "page": pno + 1,
                        "raw_table_text": block
                    })
                    print(f"[FOUND] {code} table block (p{pno+1})")
                    break

    doc.close()
    return pd.DataFrame(results)

if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent / "debi_raporlari" / "akim_gözlem_yilligi"
    
    for year in YEARS:
        pdf_name = f"dsi_{year}.pdf"
        pdf_path = base_dir / pdf_name
        output_name = f"dsi_{year}_full_flow_tables.csv"
        
        print(f"\n{'='*60}")
        print(f"[INFO] Processing {year}")
        print(f"[INFO] Looking for PDF at: {pdf_path}")
        
        if not pdf_path.exists():
            print(f"[ERROR] {pdf_path} not found. Skipping...")
            continue
        
        print(f"[INFO] PDF found! Extracting tables...")
        df = extract_table(pdf_path)
        
        if df.empty:
            print(f"[WARN] No tables found for {year}.")
        else:
            df.to_csv(output_name, index=False, encoding="utf-8")
            print(f"[DONE] Extracted {len(df)} tables → {output_name}")
    
    print(f"\n{'='*60}")
    print("[SUCCESS] All years processed!")
