#!/usr/bin/env python3
"""
Simple test to verify the shifting logic
"""

import pandas as pd
import numpy as np

def test_shift_logic():
    # Read the CSV
    df = pd.read_csv('dsi_2000_2020_final_structured_UPDATED.csv')
    
    print("Before shifting - Row 0:")
    print(f"oct_flow_max_m3: {df.iloc[0]['oct_flow_max_m3']}")
    print(f"nov_flow_max_m3: {df.iloc[0]['nov_flow_max_m3']}")
    print(f"dec_flow_max_m3: {df.iloc[0]['dec_flow_max_m3']}")
    print(f"sep_flow_max_m3: {df.iloc[0]['sep_flow_max_m3']}")
    
    # Test the shifting logic
    row = df.iloc[0]
    metric = 'flow_max_m3'
    months = ['oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep']
    
    # Get current values
    current_values = [row[f"{month}_{metric}"] for month in months]
    print(f"\nCurrent values: {current_values}")
    
    # Shift right
    shifted_values = [np.nan] + current_values[:-1]
    print(f"Shifted values: {shifted_values}")
    
    # Fill September with average of October and December
    oct_val = shifted_values[0]  # November data
    dec_val = shifted_values[2]  # January data
    if not pd.isna(oct_val) and not pd.isna(dec_val):
        shifted_values[-1] = (oct_val + dec_val) / 2
    print(f"After filling September: {shifted_values}")
    
    print(f"\nExpected result:")
    print(f"October should have: {current_values[1]} (November data)")
    print(f"November should have: {current_values[2]} (December data)")
    print(f"September should have: {(current_values[1] + current_values[2]) / 2} (average)")

if __name__ == "__main__":
    test_shift_logic()
