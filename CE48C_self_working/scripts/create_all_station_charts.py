#!/usr/bin/env python3
"""
Create annual flow charts for all stations with significant data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def create_all_station_charts():
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
    
    # Create output directory for charts
    output_dir = r"C:\Users\Asus\Desktop\CE 49X\CE49X_SELF_WORKING\station_charts"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create charts for stations with at least 5 data points
    stations_to_plot = station_counts[station_counts >= 5]
    print(f"\nCreating charts for {len(stations_to_plot)} stations with >=5 data points...")
    
    for station_code in stations_to_plot.index:
        print(f"\nProcessing station: {station_code}")
        
        # Filter data for this station
        station_data = df_flow[df_flow['station_code'] == station_code].copy()
        station_data = station_data.sort_values('year')
        
        # Get station name
        station_name = station_data['station_name'].iloc[0]
        data_count = len(station_data)
        
        print(f"  Station name: {station_name}")
        print(f"  Data points: {data_count}")
        print(f"  Years: {station_data['year'].min()} - {station_data['year'].max()}")
        print(f"  Flow range: {station_data['annual_avg_flow_m3s'].min():.3f} - {station_data['annual_avg_flow_m3s'].max():.3f} m³/s")
        
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
        plt.title(f'Annual Flow Variation for Station {station_code}\n{station_name}', 
                  fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Year', fontsize=12, fontweight='bold')
        plt.ylabel('Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
        
        # Set axis limits and ticks
        plt.xlim(station_data['year'].min() - 0.5, station_data['year'].max() + 0.5)
        plt.xticks(station_data['year'], rotation=45)
        plt.grid(True, alpha=0.3, linestyle='--')
        
        # Add value labels on points (only if not too many)
        if len(station_data) <= 15:
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
Station: {station_code}
Name: {station_name}
Years: {len(station_data)}
Flow Range: {station_data['annual_avg_flow_m3s'].min():.3f} - {station_data['annual_avg_flow_m3s'].max():.3f} m³/s
Average: {station_data['annual_avg_flow_m3s'].mean():.3f} m³/s
Std Dev: {station_data['annual_avg_flow_m3s'].std():.3f} m³/s"""
        
        plt.text(0.02, 0.98, stats_text, 
                 transform=plt.gca().transAxes, 
                 verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                 fontsize=10)
        
        # Add trend line (only if more than 2 data points)
        if len(station_data) > 2:
            z = np.polyfit(station_data['year'], station_data['annual_avg_flow_m3s'], 1)
            p = np.poly1d(z)
            plt.plot(station_data['year'], p(station_data['year']), 
                     "--", color='red', alpha=0.7, linewidth=2, 
                     label=f'Trend (slope: {z[0]:.4f})')
            plt.legend()
            
            # Calculate trend direction
            if z[0] > 0.001:
                trend_direction = "increasing"
            elif z[0] < -0.001:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
            print(f"  Trend: {trend_direction} ({z[0]:.4f} m³/s per year)")
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the chart
        output_path = os.path.join(output_dir, f"{station_code}_flow_chart.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"  Chart saved to: {output_path}")
        
        # Close the figure to free memory
        plt.close()
    
    print(f"\n[SUCCESS] All charts created successfully!")
    print(f"[FOLDER] Charts saved in: {output_dir}")
    print(f"[COUNT] Total charts created: {len(stations_to_plot)}")
    
    # Create a summary chart showing all stations
    create_summary_chart(df_flow, output_dir)

def create_summary_chart(df_flow, output_dir):
    """Create a summary chart showing all stations"""
    print(f"\nCreating summary chart...")
    
    plt.figure(figsize=(16, 10))
    
    # Get stations with at least 5 data points
    station_counts = df_flow.groupby('station_code').size()
    stations_to_plot = station_counts[station_counts >= 5].index
    
    # Define colors for different stations
    colors = plt.cm.Set3(np.linspace(0, 1, len(stations_to_plot)))
    
    for i, station_code in enumerate(stations_to_plot):
        station_data = df_flow[df_flow['station_code'] == station_code].copy()
        station_data = station_data.sort_values('year')
        
        plt.plot(station_data['year'], station_data['annual_avg_flow_m3s'], 
                 marker='o', 
                 linewidth=2, 
                 markersize=6,
                 color=colors[i],
                 label=f'{station_code} ({len(station_data)} pts)',
                 alpha=0.8)
    
    plt.title('Annual Flow Variation - All Stations Comparison', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    # Save summary chart
    summary_path = os.path.join(output_dir, "all_stations_summary.png")
    plt.savefig(summary_path, dpi=300, bbox_inches='tight')
    print(f"[SUMMARY] Summary chart saved to: {summary_path}")
    
    plt.close()

if __name__ == "__main__":
    create_all_station_charts()
