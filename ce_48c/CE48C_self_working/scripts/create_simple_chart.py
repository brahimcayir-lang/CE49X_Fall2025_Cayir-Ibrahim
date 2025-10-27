#!/usr/bin/env python3
"""
Create a simple chart of average annual flow by year
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_simple_annual_flow_chart():
    # Read the updated CSV file
    csv_path = r"C:\Users\Asus\Desktop\CE 49X\CE49X_SELF_WORKING\dsi_2000_2020_final_structured_UPDATED.csv"
    
    df = pd.read_csv(csv_path)
    print(f"Successfully loaded {len(df)} records")
    
    # Filter out records with missing annual_avg_flow_m3s
    df_flow = df[df['annual_avg_flow_m3s'].notna()]
    print(f"Records with valid annual_avg_flow_m3s: {len(df_flow)}")
    
    # Calculate yearly averages
    yearly_avg = df_flow.groupby('year')['annual_avg_flow_m3s'].agg(['mean', 'std', 'count']).reset_index()
    yearly_avg.columns = ['year', 'mean_flow', 'std_flow', 'count']
    
    print(f"\nYearly average flow data:")
    print(yearly_avg.to_string(index=False))
    
    # Create the chart
    plt.figure(figsize=(12, 8))
    
    # Plot the line chart with error bars
    plt.errorbar(yearly_avg['year'], yearly_avg['mean_flow'], 
                yerr=yearly_avg['std_flow'], 
                marker='o', 
                linewidth=2, 
                markersize=8,
                capsize=5,
                capthick=2,
                color='#2E86AB',
                ecolor='#A23B72',
                alpha=0.8)
    
    # Customize the chart
    plt.title('Average Annual Flow by Year (2005-2020)', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('Average Annual Flow (m³/s)', fontsize=12, fontweight='bold')
    
    # Set axis limits and ticks
    plt.xlim(yearly_avg['year'].min() - 0.5, yearly_avg['year'].max() + 0.5)
    plt.xticks(yearly_avg['year'], rotation=45)
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Add value labels on points
    for i, row in yearly_avg.iterrows():
        plt.annotate(f'{row["mean_flow"]:.2f}', 
                    (row['year'], row['mean_flow']),
                    textcoords="offset points", 
                    xytext=(0,10), 
                    ha='center',
                    fontsize=9,
                    fontweight='bold')
    
    # Add statistics text box
    stats_text = f"""Statistics:
Years: {len(yearly_avg)}
Stations: {df_flow['station_code'].nunique()}
Total Records: {len(df_flow)}
Avg Range: {yearly_avg['mean_flow'].min():.2f} - {yearly_avg['mean_flow'].max():.2f} m³/s"""
    
    plt.text(0.02, 0.98, stats_text, 
             transform=plt.gca().transAxes, 
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
             fontsize=10)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the chart
    output_path = r"C:\Users\Asus\Desktop\CE 49X\CE49X_SELF_WORKING\simple_annual_flow_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nChart saved to: {output_path}")
    
    # Show the chart
    plt.show()
    
    # Print summary
    print(f"\nSummary Statistics:")
    print(f"Years covered: {yearly_avg['year'].min()} - {yearly_avg['year'].max()}")
    print(f"Number of years: {len(yearly_avg)}")
    print(f"Total stations: {df_flow['station_code'].nunique()}")
    print(f"Average flow range: {yearly_avg['mean_flow'].min():.2f} - {yearly_avg['mean_flow'].max():.2f} m³/s")
    
    # Show stations with data
    stations_with_data = df_flow['station_code'].unique()
    print(f"\nStations with annual flow data: {sorted(stations_with_data)}")

if __name__ == "__main__":
    create_simple_annual_flow_chart()
