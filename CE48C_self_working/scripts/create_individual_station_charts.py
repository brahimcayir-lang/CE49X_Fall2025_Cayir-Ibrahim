#!/usr/bin/env python3
"""
Create individual charts showing average flow changes for each station separately
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def create_individual_station_charts():
    """Create separate charts for each station's flow changes"""
    
    # Read the corrected CSV
    csv_file = "dsi_2000_2020_final_structured_STD_CORRECTED.csv"
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} records from corrected dataset")
    
    # Filter out records with missing annual_avg_flow_m3s
    df_flow = df[df['annual_avg_flow_m3s'].notna()]
    print(f"Records with valid annual_avg_flow_m3s: {len(df_flow)}")
    
    # Get unique stations
    stations = df_flow['station_code'].unique()
    print(f"Found {len(stations)} unique stations")
    
    # Create individual charts for each station
    for i, station in enumerate(stations):
        print(f"\nProcessing station {i+1}/{len(stations)}: {station}")
        
        # Filter data for this station
        station_data = df_flow[df_flow['station_code'] == station].copy()
        station_data = station_data.sort_values('year')
        
        if len(station_data) < 2:
            print(f"  Skipping {station} - insufficient data ({len(station_data)} records)")
            continue
        
        # Get station name
        station_name = station_data['station_name'].iloc[0]
        
        # Create chart for this station
        create_station_flow_chart(station_data, station, station_name)

def create_station_flow_chart(station_data, station_code, station_name):
    """Create flow chart for individual station"""
    
    # Create the chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Clean styling
    plt.style.use('default')
    plt.rcParams['font.family'] = 'Arial'
    
    # Main flow chart
    ax1.plot(station_data['year'], station_data['annual_avg_flow_m3s'], 
             marker='o', linewidth=3, markersize=8,
             color='#1f77b4', markerfacecolor='#1f77b4', 
             markeredgecolor='white', markeredgewidth=2)
    
    # Fill area under the curve
    ax1.fill_between(station_data['year'], station_data['annual_avg_flow_m3s'], 
                     alpha=0.3, color='#1f77b4')
    
    # Add trend line
    if len(station_data) > 1:
        z = np.polyfit(station_data['year'], station_data['annual_avg_flow_m3s'], 1)
        p = np.poly1d(z)
        ax1.plot(station_data['year'], p(station_data['year']), 
                 "--", color='#ff7f0e', linewidth=2, alpha=0.8,
                 label=f'Trend: {z[0]:.3f} m³/s/year')
        ax1.legend(fontsize=10)
    
    # Customize main chart
    ax1.set_title(f'Annual Flow Changes - Station {station_code}\n{station_name}', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_facecolor('#fafafa')
    
    # Add value labels
    for i, row in station_data.iterrows():
        ax1.annotate(f'{row["annual_avg_flow_m3s"]:.2f}', 
                    (row['year'], row['annual_avg_flow_m3s']),
                    textcoords="offset points", xytext=(0,10), 
                    ha='center', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', 
                            alpha=0.8, edgecolor='#1f77b4', linewidth=0.5))
    
    # Statistics summary
    stats_text = f"""Station Statistics:
Years: {len(station_data)} ({station_data['year'].min():.0f}-{station_data['year'].max():.0f})
Flow Range: {station_data['annual_avg_flow_m3s'].min():.2f} - {station_data['annual_avg_flow_m3s'].max():.2f} m³/s
Mean: {station_data['annual_avg_flow_m3s'].mean():.2f} m³/s
Std Dev: {station_data['annual_avg_flow_m3s'].std():.2f} m³/s"""
    
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
             verticalalignment='top', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, 
                      edgecolor='#666666', linewidth=0.5))
    
    # Secondary chart - Monthly averages if available
    if 'annual_average_flow_avg_m3' in station_data.columns:
        monthly_data = station_data[station_data['annual_average_flow_avg_m3'].notna()]
        
        if len(monthly_data) > 0:
            ax2.plot(monthly_data['year'], monthly_data['annual_average_flow_avg_m3'], 
                     marker='s', linewidth=2, markersize=6,
                     color='#2ca02c', markerfacecolor='#2ca02c', 
                     markeredgecolor='white', markeredgewidth=1)
            
            ax2.fill_between(monthly_data['year'], monthly_data['annual_average_flow_avg_m3'], 
                             alpha=0.3, color='#2ca02c')
            
            ax2.set_title('Monthly Average Flow Over Years', fontsize=12, fontweight='bold', pad=15)
            ax2.set_xlabel('Year', fontsize=10, fontweight='bold')
            ax2.set_ylabel('Monthly Average Flow (m³/s)', fontsize=10, fontweight='bold')
            
            # Add value labels for monthly data
            for i, row in monthly_data.iterrows():
                ax2.annotate(f'{row["annual_average_flow_avg_m3"]:.2f}', 
                            (row['year'], row['annual_average_flow_avg_m3']),
                            textcoords="offset points", xytext=(0,8), 
                            ha='center', fontsize=8, fontweight='bold',
                            bbox=dict(boxstyle="round,pad=0.2", facecolor='white', 
                                    alpha=0.8, edgecolor='#2ca02c', linewidth=0.5))
        else:
            ax2.text(0.5, 0.5, 'No monthly average data available', 
                    transform=ax2.transAxes, ha='center', va='center', fontsize=12)
            ax2.set_title('Monthly Average Flow Over Years', fontsize=12, fontweight='bold', pad=15)
    else:
        ax2.text(0.5, 0.5, 'No monthly average data available', 
                transform=ax2.transAxes, ha='center', va='center', fontsize=12)
        ax2.set_title('Monthly Average Flow Over Years', fontsize=12, fontweight='bold', pad=15)
    
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_facecolor('#fafafa')
    
    # Clean spines
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#666666')
        ax.spines['bottom'].set_color('#666666')
    
    plt.tight_layout()
    
    # Save the chart
    output_path = f"station_{station_code}_flow_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"  Chart saved to: {output_path}")
    
    plt.close()  # Close to free memory

def create_station_summary():
    """Create a summary chart showing all stations"""
    
    # Read the corrected CSV
    csv_file = "dsi_2000_2020_final_structured_STD_CORRECTED.csv"
    df = pd.read_csv(csv_file)
    
    # Filter out records with missing annual_avg_flow_m3s
    df_flow = df[df['annual_avg_flow_m3s'].notna()]
    
    # Get unique stations
    stations = df_flow['station_code'].unique()
    
    # Create summary chart
    plt.figure(figsize=(16, 10))
    
    # Define colors for different stations
    colors = plt.cm.Set3(np.linspace(0, 1, len(stations)))
    
    for i, station in enumerate(stations):
        station_data = df_flow[df_flow['station_code'] == station].copy()
        station_data = station_data.sort_values('year')
        
        if len(station_data) >= 2:
            plt.plot(station_data['year'], station_data['annual_avg_flow_m3s'], 
                     marker='o', linewidth=2, markersize=4,
                     color=colors[i], label=f'{station} ({len(station_data)} pts)',
                     alpha=0.8)
    
    plt.title('All Stations - Annual Flow Changes Comparison', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    # Save summary chart
    output_path = "all_stations_summary_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nSummary chart saved to: {output_path}")
    
    plt.show()

if __name__ == "__main__":
    print("Creating individual station flow charts...")
    
    # Create individual charts for each station
    create_individual_station_charts()
    
    # Create summary chart
    create_station_summary()
    
    print("\n[SUCCESS] Individual station charts completed!")
