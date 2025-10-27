# -*- coding: utf-8 -*-
"""
Extract catchment areas (YAĞIŞ ALANI) from DSI yearbooks
---------------------------------------------------------------
Finds station code lines like "D22A093 TURNASUYU CUMHURİYET KÖYÜ"
and the next line that contains "YAĞIŞ ALANI : ... km2".
Outputs station_code + catchment_area_km2.

Usage:
    python catchment_data_km2.py [YEAR]
    
Example:
    python catchment_data_km2.py 2019
    python catchment_data_km2.py 2018
"""

import re
from pathlib import Path
import fitz  # PyMuPDF
import pandas as pd
import sys

# Default year is 2020 if not provided as argument
YEAR = sys.argv[1] if len(sys.argv) > 1 else "2020"
PDF_NAME = f"debi_raporlari/akim_gözlem_yilligi/dsi_{YEAR}.pdf"
OUTPUT_NAME = f"dsi_{YEAR}_catchment_areas.csv"

# === Target stations ===
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


def extract_catchments(pdf_path):
    doc = fitz.open(pdf_path)
    results = []

    for pno in range(doc.page_count):
        text = doc.load_page(pno).get_text("text")
        if not text.strip():
            continue

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for i, line in enumerate(lines):
            # Check for station line
            m = re.match(r"^([DE]\d{2}A\d{3})\s", line)
            if not m:
                continue

            code = m.group(1).upper()
            if code not in TARGET_STATIONS:
                continue

            # Look for YAĞIŞ ALANI line near this station
            for j in range(i, min(i + 10, len(lines))):
                if "YAĞIŞ ALANI" in lines[j].upper() or "YAGIS ALANI" in lines[j].upper():
                    match = re.search(r"YA[GĞ]I[SŞ]\s*ALANI\s*:\s*([0-9\.,]+)", lines[j], flags=re.I)
                    if match:
                        val = clean_num(match.group(1))
                        results.append({
                            "station_code": code,
                            "catchment_area_km2": val,
                            "page": pno + 1
                        })
                        print(f"[FOUND] {code}: {val} km2 (p{pno+1})")
                    break

    doc.close()
    return pd.DataFrame(results)


if __name__ == "__main__":
    pdf_path = Path(PDF_NAME)
    if not pdf_path.exists():
        print(f"[ERROR] {pdf_path} not found.")
    else:
        df = extract_catchments(pdf_path)
        if df.empty:
            print("[WARN] No YAĞIŞ ALANI found.")
        else:
            df.to_csv(OUTPUT_NAME, index=False, encoding="utf-8")
            print(f"[DONE] Extracted {len(df)} stations -> {OUTPUT_NAME}")
