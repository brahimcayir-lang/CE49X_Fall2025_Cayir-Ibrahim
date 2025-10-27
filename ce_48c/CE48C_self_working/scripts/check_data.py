#!/usr/bin/env python3
"""
Check the original data structure
"""

import pandas as pd

def check_data():
    df = pd.read_csv('dsi_2000_2020_final_structured_UPDATED.csv')
    
    print('Original data for row 0:')
    months = ['oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep']
    for month in months:
        print(f'{month}_flow_max_m3: {df.iloc[0][f"{month}_flow_max_m3"]}')
    
    print('\nChecking if October is really empty for all metrics:')
    metrics = ['flow_max_m3', 'flow_min_m3', 'flow_avg_m3', 'ltsnkm2_m3', 'akim_mm_m3', 'milm3_m3']
    for metric in metrics:
        oct_val = df.iloc[0][f'oct_{metric}']
        nov_val = df.iloc[0][f'nov_{metric}']
        print(f'oct_{metric}: {oct_val}, nov_{metric}: {nov_val}')

if __name__ == "__main__":
    check_data()
