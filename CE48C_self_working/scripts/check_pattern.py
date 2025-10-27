#!/usr/bin/env python3
"""
Check which columns actually have data
"""

import pandas as pd

def check_data_pattern():
    df = pd.read_csv('dsi_2000_2020_final_structured_UPDATED.csv')
    
    print('Row 0 - checking which columns have data:')
    months = ['oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep']
    for month in months:
        val = df.iloc[0][f'{month}_flow_max_m3']
        print(f'{month}: {val}')
    
    print('\nLooking for the first non-NaN value:')
    for i, month in enumerate(months):
        val = df.iloc[0][f'{month}_flow_max_m3']
        if not pd.isna(val):
            print(f'First non-NaN is {month} (index {i}): {val}')
            break

if __name__ == "__main__":
    check_data_pattern()
