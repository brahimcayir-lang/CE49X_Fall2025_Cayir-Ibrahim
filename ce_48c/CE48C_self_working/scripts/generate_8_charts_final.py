#!/usr/bin/env python3
"""
Generate 8 Comprehensive Hydrological Charts from DSİ Data
Using the updated CSV file with filled year column
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import warnings
import sys
import os

# Set encoding for Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('default')
sns.set_style("whitegrid")
sns.set_palette("husl")

def load_and_prepare_data():
    """Load and prepare the hydrological dataset"""
    print("Loading hydrological data...")
    
    # Load the dataset
    df = pd.read_csv('dsi_2000_2020_final_with_years.csv', encoding='utf-8-sig')
    
    # Filter for the main station (D14A162 - Yeşilırmak Kozlu)
    main_station = df[df['station_code'] == 'D14A162'].copy()
    
    if len(main_station) == 0:
        print("No data found for D14A162. Using all stations for analysis...")
        main_station = df.copy()
    else:
        print(f"Found {len(main_station)} records for D14A162 station")
    
    # Convert flow data to numeric
    flow_columns = [
        'flow_october_m3s', 'flow_november_m3s', 'flow_december_m3s',
        'flow_january_m3s', 'flow_february_m3s', 'flow_march_m3s',
        'flow_april_m3s', 'flow_may_m3s', 'flow_june_m3s',
        'flow_july_m3s', 'flow_august_m3s', 'flow_september_m3s'
    ]
    
    for col in flow_columns:
        if col in main_station.columns:
            main_station[col] = pd.to_numeric(main_station[col], errors='coerce')
    
    # Convert other numeric columns
    numeric_columns = [
        'annual_total_m3_million', 'annual_mm', 'annual_lps_km2',
        'ltsnkm2_average', 'mm_akim_annual_average', 'mil_m3_annual_average'
    ]
    
    for col in numeric_columns:
        if col in main_station.columns:
            main_station[col] = pd.to_numeric(main_station[col], errors='coerce')
    
    return main_station

def create_chart1_flow_monthly_avg(df):
    """Chart 1: Monthly Average Flow (m³/s)"""
    print("Creating Chart 1: Monthly Average Flow...")
    
    # Calculate monthly averages
    monthly_columns = [
        'flow_october_m3s', 'flow_november_m3s', 'flow_december_m3s',
        'flow_january_m3s', 'flow_february_m3s', 'flow_march_m3s',
        'flow_april_m3s', 'flow_may_m3s', 'flow_june_m3s',
        'flow_july_m3s', 'flow_august_m3s', 'flow_september_m3s'
    ]
    
    monthly_avg = []
    for col in monthly_columns:
        if col in df.columns:
            monthly_avg.append(df[col].mean())
        else:
            monthly_avg.append(0)
    
    months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 
              'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
    
    plt.figure(figsize=(12, 8))
    bars = plt.bar(months, monthly_avg, color='steelblue', alpha=0.7)
    
    # Add value labels on bars
    for bar, value in zip(bars, monthly_avg):
        if value > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.title('Monthly Average Flow Rate (m³/s)\nD14A162 - Yeşilırmak Kozlu (2005-2020)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Average Flow Rate (m³/s)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save chart
    plt.savefig('chart1_flow_monthly_avg_final.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Chart 1 saved as: chart1_flow_monthly_avg_final.png")

def create_chart2_ltsnkm2_monthly_avg(df):
    """Chart 2: Monthly Average Specific Flow (lt/sn/km²)"""
    print("Creating Chart 2: Monthly Average Specific Flow...")
    
    # Turkish month columns for specific flow
    ltsnkm2_columns = [
        'ltsnkm2_Ekim', 'ltsnkm2_Kasım', 'ltsnkm2_Aralık', 'ltsnkm2_Ocak',
        'ltsnkm2_Şubat', 'ltsnkm2_Mart', 'ltsnkm2_Nisan', 'ltsnkm2_Mayıs',
        'ltsnkm2_Haziran', 'ltsnkm2_Temmuz', 'ltsnkm2_Ağustos', 'ltsnkm2_Eylül'
    ]
    
    monthly_avg = []
    for col in ltsnkm2_columns:
        if col in df.columns:
            monthly_avg.append(df[col].mean())
        else:
            monthly_avg.append(0)
    
    months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 
              'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
    
    plt.figure(figsize=(12, 8))
    bars = plt.bar(months, monthly_avg, color='forestgreen', alpha=0.7)
    
    # Add value labels on bars
    for bar, value in zip(bars, monthly_avg):
        if value > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.title('Monthly Average Specific Flow (lt/sn/km²)\nD14A162 - Yeşilırmak Kozlu (2005-2020)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Specific Flow (lt/sn/km²)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save chart
    plt.savefig('chart2_ltsnkm2_monthly_avg_final.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Chart 2 saved as: chart2_ltsnkm2_monthly_avg_final.png")

def create_chart3_mm_akim_monthly_avg(df):
    """Chart 3: Monthly Average Flow Depth (mm)"""
    print("Creating Chart 3: Monthly Average Flow Depth...")
    
    # Turkish month columns for flow depth
    mm_columns = [
        'mm_akim_Ekim', 'mm_akim_Kasım', 'mm_akim_Aralık', 'mm_akim_Ocak',
        'mm_akim_Şubat', 'mm_akim_Mart', 'mm_akim_Nisan', 'mm_akim_Mayıs',
        'mm_akim_Haziran', 'mm_akim_Temmuz', 'mm_akim_Ağustos', 'mm_akim_Eylül'
    ]
    
    monthly_avg = []
    for col in mm_columns:
        if col in df.columns:
            monthly_avg.append(df[col].mean())
        else:
            monthly_avg.append(0)
    
    months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 
              'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
    
    plt.figure(figsize=(12, 8))
    bars = plt.bar(months, monthly_avg, color='darkorange', alpha=0.7)
    
    # Add value labels on bars
    for bar, value in zip(bars, monthly_avg):
        if value > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.title('Monthly Average Flow Depth (mm)\nD14A162 - Yeşilırmak Kozlu (2005-2020)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Flow Depth (mm)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save chart
    plt.savefig('chart3_mm_akim_monthly_avg_final.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Chart 3 saved as: chart3_mm_akim_monthly_avg_final.png")

def create_chart4_mil_m3_monthly_avg(df):
    """Chart 4: Monthly Average Volume (million m³)"""
    print("Creating Chart 4: Monthly Average Volume...")
    
    # Turkish month columns for volume
    mil_m3_columns = [
        'mil_m3_Ekim', 'mil_m3_Kasım', 'mil_m3_Aralık', 'mil_m3_Ocak',
        'mil_m3_Şubat', 'mil_m3_Mart', 'mil_m3_Nisan', 'mil_m3_Mayıs',
        'mil_m3_Haziran', 'mil_m3_Temmuz', 'mil_m3_Ağustos', 'mil_m3_Eylül'
    ]
    
    monthly_avg = []
    for col in mil_m3_columns:
        if col in df.columns:
            monthly_avg.append(df[col].mean())
        else:
            monthly_avg.append(0)
    
    months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 
              'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
    
    plt.figure(figsize=(12, 8))
    bars = plt.bar(months, monthly_avg, color='purple', alpha=0.7)
    
    # Add value labels on bars
    for bar, value in zip(bars, monthly_avg):
        if value > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.title('Monthly Average Volume (million m³)\nD14A162 - Yeşilırmak Kozlu (2005-2020)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Volume (million m³)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save chart
    plt.savefig('chart4_mil_m3_monthly_avg_final.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Chart 4 saved as: chart4_mil_m3_monthly_avg_final.png")

def create_chart5_flow_annual_avg(df):
    """Chart 5: Annual Average Flow (m³/s)"""
    print("Creating Chart 5: Annual Average Flow...")
    
    # Calculate annual averages
    annual_flow = df.groupby('year')['flow_avg_annual_m3s'].mean()
    
    plt.figure(figsize=(14, 8))
    bars = plt.bar(annual_flow.index, annual_flow.values, color='steelblue', alpha=0.7)
    
    # Add value labels on bars
    for bar, value in zip(bars, annual_flow.values):
        if value > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.title('Annual Average Flow Rate (m³/s)\nD14A162 - Yeşilırmak Kozlu (2005-2020)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Average Flow Rate (m³/s)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save chart
    plt.savefig('chart5_flow_annual_avg_final.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Chart 5 saved as: chart5_flow_annual_avg_final.png")

def create_chart6_ltsnkm2_annual_avg(df):
    """Chart 6: Annual Average Specific Flow (lt/sn/km²)"""
    print("Creating Chart 6: Annual Average Specific Flow...")
    
    # Calculate annual averages
    annual_specific = df.groupby('year')['ltsnkm2_average'].mean()
    
    plt.figure(figsize=(14, 8))
    bars = plt.bar(annual_specific.index, annual_specific.values, color='forestgreen', alpha=0.7)
    
    # Add value labels on bars
    for bar, value in zip(bars, annual_specific.values):
        if value > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.title('Annual Average Specific Flow (lt/sn/km²)\nD14A162 - Yeşilırmak Kozlu (2005-2020)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Specific Flow (lt/sn/km²)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save chart
    plt.savefig('chart6_ltsnkm2_annual_avg_final.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Chart 6 saved as: chart6_ltsnkm2_annual_avg_final.png")

def create_chart7_mm_akim_annual_avg(df):
    """Chart 7: Annual Average Flow Depth (mm)"""
    print("Creating Chart 7: Annual Average Flow Depth...")
    
    # Calculate annual averages
    annual_mm = df.groupby('year')['mm_akim_annual_average'].mean()
    
    plt.figure(figsize=(14, 8))
    bars = plt.bar(annual_mm.index, annual_mm.values, color='darkorange', alpha=0.7)
    
    # Add value labels on bars
    for bar, value in zip(bars, annual_mm.values):
        if value > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.title('Annual Average Flow Depth (mm)\nD14A162 - Yeşilırmak Kozlu (2005-2020)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Flow Depth (mm)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save chart
    plt.savefig('chart7_mm_akim_annual_avg_final.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Chart 7 saved as: chart7_mm_akim_annual_avg_final.png")

def create_chart8_mil_m3_annual_avg(df):
    """Chart 8: Annual Average Volume (million m³)"""
    print("Creating Chart 8: Annual Average Volume...")
    
    # Calculate annual averages
    annual_volume = df.groupby('year')['mil_m3_annual_average'].mean()
    
    plt.figure(figsize=(14, 8))
    bars = plt.bar(annual_volume.index, annual_volume.values, color='purple', alpha=0.7)
    
    # Add value labels on bars
    for bar, value in zip(bars, annual_volume.values):
        if value > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.title('Annual Average Volume (million m³)\nD14A162 - Yeşilırmak Kozlu (2005-2020)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Volume (million m³)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save chart
    plt.savefig('chart8_mil_m3_annual_avg_final.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Chart 8 saved as: chart8_mil_m3_annual_avg_final.png")

def main():
    """Main function to generate all 8 charts"""
    print("="*60)
    print("GENERATING 8 HYDROLOGICAL CHARTS")
    print("="*60)
    
    # Load data
    df = load_and_prepare_data()
    
    if df.empty:
        print("Error: No data loaded!")
        return
    
    print(f"Data loaded successfully: {len(df)} records")
    print(f"Years range: {df['year'].min()} - {df['year'].max()}")
    
    # Generate all 8 charts
    create_chart1_flow_monthly_avg(df)
    create_chart2_ltsnkm2_monthly_avg(df)
    create_chart3_mm_akim_monthly_avg(df)
    create_chart4_mil_m3_monthly_avg(df)
    create_chart5_flow_annual_avg(df)
    create_chart6_ltsnkm2_annual_avg(df)
    create_chart7_mm_akim_annual_avg(df)
    create_chart8_mil_m3_annual_avg(df)
    
    print("\n" + "="*60)
    print("ALL 8 CHARTS GENERATED SUCCESSFULLY!")
    print("="*60)
    print("Chart files saved:")
    print("1. chart1_flow_monthly_avg_final.png")
    print("2. chart2_ltsnkm2_monthly_avg_final.png")
    print("3. chart3_mm_akim_monthly_avg_final.png")
    print("4. chart4_mil_m3_monthly_avg_final.png")
    print("5. chart5_flow_annual_avg_final.png")
    print("6. chart6_ltsnkm2_annual_avg_final.png")
    print("7. chart7_mm_akim_annual_avg_final.png")
    print("8. chart8_mil_m3_annual_avg_final.png")

if __name__ == "__main__":
    main()



