# -*- coding: utf-8 -*-
"""
Process all year files (2005-2020) using the table_arranger logic.
"""

import re
import pandas as pd
from pathlib import Path

MONTHS = ["oct","nov","dec","jan","feb","mar","apr","may","jun","jul","aug","sep"]

def clean_num(x):
    """Convert Turkish-formatted numbers like '66,32' to float."""
    if not isinstance(x, str):
        return None
    x = x.strip().replace(",", ".")
    # Handle "KURU" (dry/no data) and other non-numeric values
    if x.upper() == "KURU" or x == "nan" or not x:
        return None
    try:
        return float(x)
    except:
        return None


def parse_block(block):
    """Parse a raw 7-line block (Maks. → SU YILI) into structured numeric data."""
    data = {}
    patterns = {
        "Maks.": "max",
        "Min.": "min",
        "Ortalama": "avg",
        "LT/SN/Km2": "ltsnkm2",
        "AKIM mm.": "mm",
        "MİL. M3": "mil_m3",
    }

    # --- 1. Extract monthly values ---
    for label, key in patterns.items():
        # Updated regex to also match "KURU" (dry/no data) values
        m = re.search(rf"{label}\s+([0-9\.\,\sKURU]+)", block, flags=re.I)
        if m:
            # Split by whitespace to get all values including "KURU"
            nums = m.group(1).split()
            nums = [clean_num(n) for n in nums]
            nums = nums[:12] if len(nums) >= 12 else nums + [None]*(12-len(nums))
            for i, month in enumerate(MONTHS):
                data[f"{month}_{key}"] = nums[i] if i < len(nums) else None
        else:
            for month in MONTHS:
                data[f"{month}_{key}"] = None

    # --- 2. Extract annual totals (SU YILI line) ---
    # Handles different spacing/capitalization variants:
    annual_pattern = re.compile(
        r"SU\s*YILI.*?YILLIK\s*TOPLAM\s*AKIM\s*([0-9\.,]+)\s*M[Iİ]LYON\s*M3"
        r".*?([0-9\.,]+)\s*MM\.?"
        r".*?([0-9\.,]+)\s*LT\s*/?\s*SN\s*/?\s*KM2",
        flags=re.I
    )
    m = re.search(annual_pattern, block)
    if m:
        data["annual_total_m3"] = clean_num(m.group(1)) * 1_000_000
        data["annual_mm"] = clean_num(m.group(2))
        data["annual_lt_sn_km2"] = clean_num(m.group(3))
    else:
        data["annual_total_m3"] = None
        data["annual_mm"] = None
        data["annual_lt_sn_km2"] = None

    return data


def process_file(input_file):
    """Process a single year file."""
    year = input_file.stem.replace("dsi_", "").replace("_full_flow_tables", "")
    output_file = input_file.parent / f"dsi_{year}_full_flow_tables_parsed.csv"
    
    print(f"\nProcessing {input_file.name}...")
    
    df = pd.read_csv(input_file)
    parsed_rows = []

    for _, row in df.iterrows():
        block = str(row["raw_table_text"])
        base = {"station_code": row["station_code"], "page": row["page"]}
        parsed = parse_block(block)
        parsed_rows.append({**base, **parsed})

    final_df = pd.DataFrame(parsed_rows)

    # reorder columns nicely
    col_order = ["station_code","page"]
    for metric in ["max","min","avg","ltsnkm2","mm","mil_m3"]:
        for month in MONTHS:
            col_order.append(f"{month}_{metric}")
    col_order += ["annual_total_m3","annual_mm","annual_lt_sn_km2"]

    final_df = final_df[col_order]
    final_df.to_csv(output_file, index=False, encoding="utf-8")

    print(f"✓ Parsed {len(final_df)} stations → {output_file.name}")
    return len(final_df)


def main():
    """Process all year files."""
    base_dir = Path(__file__).parent
    
    # Find all full_flow_tables.csv files
    input_files = sorted(base_dir.glob("dsi_*_full_flow_tables.csv"))
    
    print(f"Found {len(input_files)} files to process:")
    for f in input_files:
        print(f"  - {f.name}")
    
    results = []
    for input_file in input_files:
        try:
            count = process_file(input_file)
            results.append((input_file.name, count, "SUCCESS"))
        except Exception as e:
            print(f"✗ ERROR processing {input_file.name}: {e}")
            results.append((input_file.name, 0, f"ERROR: {e}"))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    for filename, count, status in results:
        print(f"{filename:40} → {count:3} stations  [{status}]")
    
    total = sum(count for _, count, _ in results)
    successful = sum(1 for _, _, status in results if status == "SUCCESS")
    print(f"\nTotal: {len(results)} files processed, {successful} successful, {total} total stations parsed")


if __name__ == "__main__":
    main()

