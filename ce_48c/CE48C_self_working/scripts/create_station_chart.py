#!/usr/bin/env python3
"""
Find station with most data and create annual flow chart for that station
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_station_flow_chart():
    # Read the updated CSV file
    csv_path = r"C:\Users\Asus\Desktop\CE 49X\CE49X_SELF_WORKING\dsi_2000_2020_final_structured_UPDATED.csv"
    
    df = pd.read_csv(csv_path)
    print(f"Successfully loaded {len(df)} records")
    
    # Filter out records with missing annual_avg_flow_m3s
    df_flow = df[df['annual_avg_flow_m3s'].notna()]
    print(f"Records with valid annual_avg_flow_m3s: {len(df_flow)}")
    
    # Count data points per station
    station_counts = df_flow.groupby('station_code').size().sort_values(ascending=False)
    print(f"\nData points per station:")
    print(station_counts.to_string())
    
    # Get the station with most data
    most_data_station = station_counts.index[0]
    most_data_count = station_counts.iloc[0]
    
    print(f"\nStation with most data: {most_data_station} ({most_data_count} records)")
    
    # Filter data for this station
    station_data = df_flow[df_flow['station_code'] == most_data_station].copy()
    station_data = station_data.sort_values('year')
    
    # Get station name
    station_name = station_data['station_name'].iloc[0]
    print(f"Station name: {station_name}")
    
    print(f"\nAnnual flow data for {most_data_station}:")
    print(station_data[['year', 'annual_avg_flow_m3s']].to_string(index=False))
    
    # Create the chart
    plt.figure(figsize=(12, 8))
    
    # Plot the line chart
    plt.plot(station_data['year'], station_data['annual_avg_flow_m3s'], 
             marker='o', 
             linewidth=3, 
             markersize=10,
             color='#2E86AB',
             alpha=0.8)
    
    # Fill area under the curve
    plt.fill_between(station_data['year'], station_data['annual_avg_flow_m3s'], 
                     alpha=0.3, color='#2E86AB')
    
    # Customize the chart
    plt.title(f'Annual Flow Variation for Station {most_data_station}\n{station_name}', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
    
    # Set axis limits and ticks
    plt.xlim(station_data['year'].min() - 0.5, station_data['year'].max() + 0.5)
    plt.xticks(station_data['year'], rotation=45)
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Add value labels on points
    for i, row in station_data.iterrows():
        plt.annotate(f'{row["annual_avg_flow_m3s"]:.2f}', 
                    (row['year'], row['annual_avg_flow_m3s']),
                    textcoords="offset points", 
                    xytext=(0,15), 
                    ha='center',
                    fontsize=9,
                    fontweight='bold')
    
    # Add statistics text box
    stats_text = f"""Station Statistics:
Station: {most_data_station}
Name: {station_name}
Years: {len(station_data)}
Flow Range: {station_data['annual_avg_flow_m3s'].min():.2f} - {station_data['annual_avg_flow_m3s'].max():.2f} m³/s
Average: {station_data['annual_avg_flow_m3s'].mean():.2f} m³/s
Std Dev: {station_data['annual_avg_flow_m3s'].std():.2f} m³/s"""
    
    plt.text(0.02, 0.98, stats_text, 
             transform=plt.gca().transAxes, 
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
             fontsize=10)
    
    # Add trend line
    z = np.polyfit(station_data['year'], station_data['annual_avg_flow_m3s'], 1)
    p = np.poly1d(z)
    plt.plot(station_data['year'], p(station_data['year']), 
             "--", color='red', alpha=0.7, linewidth=2, label=f'Trend (slope: {z[0]:.3f})')
    plt.legend()
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the chart
    output_path = r"C:\Users\Asus\Desktop\CE 49X\CE49X_SELF_WORKING\station_flow_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nChart saved to: {output_path}")
    
    # Show the chart
    plt.show()
    
    # Print summary
    print(f"\nSummary for {most_data_station}:")
    print(f"Years covered: {station_data['year'].min()} - {station_data['year'].max()}")
    print(f"Number of years: {len(station_data)}")
    print(f"Flow range: {station_data['annual_avg_flow_m3s'].min():.2f} - {station_data['annual_avg_flow_m3s'].max():.2f} m³/s")
    print(f"Average flow: {station_data['annual_avg_flow_m3s'].mean():.2f} m³/s")
    print(f"Standard deviation: {station_data['annual_avg_flow_m3s'].std():.2f} m³/s")
    
    # Calculate trend
    if len(station_data) > 1:
        trend_slope = z[0]
        if trend_slope > 0:
            trend_direction = "increasing"
        elif trend_slope < 0:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        print(f"Trend: {trend_direction} ({trend_slope:.4f} m³/s per year)")

if __name__ == "__main__":
    create_station_flow_chart()
