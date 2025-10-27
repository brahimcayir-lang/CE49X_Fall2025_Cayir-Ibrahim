#!/usr/bin/env python3
"""
Create a chart showing average annual flow values vs years
from DSİ hydrological data
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def create_annual_flow_chart():
    # Read the CSV file
    csv_path = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_final_structured.csv"
    
    try:
        df = pd.read_csv(csv_path)
        print(f"Successfully loaded {len(df)} records")
        
        # Filter out rows with missing annual_avg_flow_m3s values
        df_filtered = df.dropna(subset=['annual_avg_flow_m3s'])
        print(f"Records with valid annual_avg_flow_m3s: {len(df_filtered)}")
        
        # Group by year and calculate average annual flow
        yearly_avg = df_filtered.groupby('year')['annual_avg_flow_m3s'].agg(['mean', 'std', 'count']).reset_index()
        
        # Sort by year
        yearly_avg = yearly_avg.sort_values('year')
        
        print("\nYearly average flow data:")
        print(yearly_avg)
        
        # Create the chart
        plt.figure(figsize=(12, 8))
        
        # Plot the average values
        plt.plot(yearly_avg['year'], yearly_avg['mean'], 
                marker='o', linewidth=2, markersize=8, 
                color='#2E86AB', label='Average Annual Flow')
        
        # Add error bars showing standard deviation
        plt.errorbar(yearly_avg['year'], yearly_avg['mean'], 
                    yerr=yearly_avg['std'], 
                    fmt='none', color='#A23B72', alpha=0.7, capsize=5)
        
        # Customize the chart
        plt.title('Average Annual Flow (m³/s) vs Years\nDSİ Hydrological Stations (2005-2020)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Year', fontsize=14, fontweight='bold')
        plt.ylabel('Average Annual Flow (m³/s)', fontsize=14, fontweight='bold')
        
        # Add grid
        plt.grid(True, alpha=0.3, linestyle='--')
        
        # Set x-axis ticks to show all years
        plt.xticks(yearly_avg['year'], rotation=45)
        
        # Add some statistics as text
        overall_mean = yearly_avg['mean'].mean()
        overall_std = yearly_avg['mean'].std()
        
        stats_text = f'Overall Average: {overall_mean:.2f} m³/s\nStd Dev: {overall_std:.2f} m³/s\nStations: {df_filtered["station_code"].nunique()}'
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                fontsize=10)
        
        # Add legend
        plt.legend(fontsize=12)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save the chart
        output_path = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\annual_flow_chart.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\nChart saved to: {output_path}")
        
        # Show the chart
        plt.show()
        
        # Print summary statistics
        print(f"\nSummary Statistics:")
        print(f"Years covered: {yearly_avg['year'].min()} - {yearly_avg['year'].max()}")
        print(f"Number of years: {len(yearly_avg)}")
        print(f"Total stations: {df_filtered['station_code'].nunique()}")
        print(f"Average flow range: {yearly_avg['mean'].min():.2f} - {yearly_avg['mean'].max():.2f} m³/s")
        
        # Show stations with data
        stations_with_data = df_filtered['station_code'].unique()
        print(f"\nStations with annual flow data: {sorted(stations_with_data)}")
        
    except FileNotFoundError:
        print(f"Error: Could not find file at {csv_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_annual_flow_chart()
