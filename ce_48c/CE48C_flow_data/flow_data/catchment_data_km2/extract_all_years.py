# -*- coding: utf-8 -*-
"""
Batch extract catchment areas for all years (2005-2019)
---------------------------------------------------------------
Runs catchment_data_km2.py for each year from 2005 to 2019
"""

import subprocess
import sys
from pathlib import Path

def extract_all_years():
    """Extract catchment areas for all available years"""
    years = [str(year) for year in range(2005, 2020)]  # 2005 to 2019
    script_path = Path(__file__).parent / "catchment_data_km2.py"
    
    successful = 0
    failed = []
    
    print("=" * 60)
    print("Batch Processing Catchment Areas Extraction")
    print("=" * 60)
    
    for year in years:
        print(f"\n[{year}] Processing...")
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), year],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            if result.returncode == 0:
                # Check if we found stations
                if "[DONE]" in result.stdout:
                    successful += 1
                    print(f"[{year}] OK Success")
                    # Print the summary line
                    for line in result.stdout.split('\n'):
                        if "[DONE]" in line:
                            print(f"       {line.strip()}")
                else:
                    print(f"[{year}] WARN No data found")
                    failed.append(year)
            else:
                print(f"[{year}] ERROR")
                print(f"       {result.stderr.strip()}")
                failed.append(year)
                
        except Exception as e:
            print(f"[{year}] EXCEPTION: {str(e)}")
            failed.append(year)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Summary: {successful} years processed successfully")
    if failed:
        print(f"Failed years: {', '.join(failed)}")
    print("=" * 60)


if __name__ == "__main__":
    extract_all_years()

