# -*- coding: utf-8 -*-
"""
Extract annual average flow (m³/sn) for specific stations from dsi PDFs
------------------------------------------------------------
Looks for lines like:
  "ORTALAMA AKIMLAR : ... Su yılında 4.711 m3/sn."
and returns station_code + avg_annual_flow_m3s
"""

import re
from pathlib import Path
import fitz  # PyMuPDF
import pandas as pd

PDF_NAME = "debi_raporlari/akim_gözlem_yilligi/dsi_2005.pdf"
OUTPUT_NAME = "dsi_2005_avg_flows_filtered.csv"

# === target station codes ===
TARGET_STATIONS = {
    "E22A065","E22A066","D22A093","E22A071","D14A185","E22A054","E22A063",
    "E14A018","D14A162","D14A186","D22A105","E22A053","D14A172","D14A117",
    "E14A027","D22A106","D14A200","E14A002","D14A179","D22A098","D22A159",
    "D14A064","E14A038","D14A201","D14A184","D14A211","D14A208","D14A214",
    "D14A207","D14A141","E22A062","E14A040","D14A215","D14A176","D14A011",
    "D14A188","D14A081"
}

def clean_num(x):
    return float(x.replace(",", ".").strip())

def extract_flows(pdf_path):
    doc = fitz.open(pdf_path)
    results = []

    for pno in range(doc.page_count):
        text = doc.load_page(pno).get_text("text")
        if not text.strip():
            continue
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for i, line in enumerate(lines):
            # station code line - more flexible matching
            m = re.match(r"^([DE]\d{2}A\d{3})[\s\.]", line)
            if not m:
                # Try alternative format
                m = re.search(r"\b([DE]\d{2}A\d{3})\b", line[:20])
            
            if m:
                code = m.group(1).upper()
                if code not in TARGET_STATIONS:
                    continue

                # search next lines for "Su yılında" - increased window
                for j in range(i, min(i+50, len(lines))):
                    if "Su yılında" in lines[j] or "Su yilinda" in lines[j]:
                        # Try multiple patterns
                        match = re.search(r"([0-9\.,]+)\s*m3/?sn", lines[j])
                        if not match:
                            match = re.search(r"([0-9\.,]+)\s*metreküp/saniye", lines[j])
                        if not match:
                            match = re.search(r"([0-9\.,]+)\s*m³/sn", lines[j])
                        
                        if match:
                            val = clean_num(match.group(1))
                            results.append({
                                "station_code": code,
                                "avg_annual_flow_m3s": val,
                                "page": pno + 1
                            })
                            print(f"[FOUND] {code}: {val} m³/s (p{pno+1})")
                        break
    doc.close()
    return pd.DataFrame(results)

if __name__ == "__main__":
    pdf_path = Path(PDF_NAME)
    if not pdf_path.exists():
        print(f"[ERROR] {pdf_path} not found.")
    else:
        df = extract_flows(pdf_path)
        if df.empty:
            print("[WARN] No station values found.")
        else:
            df.to_csv(OUTPUT_NAME, index=False, encoding="utf-8")
            print(f"[DONE] Extracted {len(df)} stations → {OUTPUT_NAME}")
