# -*- coding: utf-8 -*-
import re
from pathlib import Path
import fitz
import pandas as pd
import sys

TARGET_STATIONS = {
    "E22A065","E22A066","D22A093","E22A071","D14A185","E22A054","E22A063",
    "E14A018","D14A162","D14A186","D22A105","E22A053","D14A172","D14A117",
    "E14A027","D22A106","D14A200","E14A002","D14A179","D22A098","D22A159",
    "D14A064","E14A038","D14A201","D14A184","D14A211","D14A208","D14A214",
    "D14A207","D14A141","E22A062","E14A040","D14A215","D14A176","D14A011",
    "D14A188","D14A081"
}

def clean_num(x):
    try:
        return float(x.strip().replace(",", ".").replace(" ", ""))
    except:
        return None

def extract_catchments(pdf_path, year):
    doc = fitz.open(pdf_path)
    results = []
    found_codes = set()
    
    for pno in range(doc.page_count):
        text = doc.load_page(pno).get_text("text")
        if not text.strip():
            continue
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for i, line in enumerate(lines):
            m = re.search(r"\b([DE]\d{2}A\d{3})\b", line, re.IGNORECASE)
            if not m:
                continue
            code = m.group(1).upper()
            if code not in TARGET_STATIONS or code in found_codes:
                continue
            
            for j in range(i, min(i + 15, len(lines))):
                if j == i:
                    continue
                line_text = lines[j]
                line_upper = line_text.upper()
                if any(k in line_upper for k in ["YAĞIŞ ALANI", "YAGIS ALANI", "HAVZA", "KM2", "KM²"]):
                    match = re.search(r'(\d+[,\.]\d+|\d+)\s*(km2|km²|km)', line_text, re.IGNORECASE)
                    if match:
                        val = clean_num(match.group(1))
                        if val and val > 0:
                            results.append({"station_code": code, "catchment_area_km2": val, "page": pno + 1})
                            found_codes.add(code)
                            break
    doc.close()
    return pd.DataFrame(results)

years = [str(y) for y in range(2005, 2021)]
for year in years:
    pdf_path = Path(f"debi_raporlari/akim_gözlem_yilligi/dsi_{year}.pdf")
    if pdf_path.exists():
        df = extract_catchments(pdf_path, year)
        if not df.empty:
            df.to_csv(f"dsi_{year}_catchment_areas.csv", index=False, encoding="utf-8")
            print(f"{year}: {len(df)} stations -> dsi_{year}_catchment_areas.csv")

