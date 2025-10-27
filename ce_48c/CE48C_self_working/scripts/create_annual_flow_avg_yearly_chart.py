#!/usr/bin/env python3
"""
Create chart showing annual_average_flow_avg_m3 changes over years
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_annual_flow_avg_chart():
    # Read the CSV
    csv_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED_ROUNDED_WITH_ANNUAL_AVG.csv"
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} records")
    
    # Filter out records with missing annual_average_flow_avg_m3
    df_flow = df[df['annual_average_flow_avg_m3'].notna()]
    print(f"Records with valid annual_average_flow_avg_m3: {len(df_flow)}")
    
    # Calculate yearly average and statistics
    yearly_stats = df_flow.groupby('year')['annual_average_flow_avg_m3'].agg(['mean', 'std', 'count']).reset_index()
    yearly_stats.columns = ['year', 'mean_flow_avg', 'std_flow_avg', 'count']
    
    print("\nYearly statistics for annual_average_flow_avg_m3:")
    print(yearly_stats.to_string(index=False))
    
    # Create the chart
    plt.figure(figsize=(14, 8))
    
    # Plot the line chart with error bars
    plt.errorbar(yearly_stats['year'], yearly_stats['mean_flow_avg'], 
                 yerr=yearly_stats['std_flow_avg'], 
                 marker='o', 
                 linewidth=3, 
                 markersize=10,
                 color='#2E86AB',
                 capsize=5,
                 capthick=2,
                 alpha=0.8,
                 label='Annual Average Flow (m³/s)')
    
    # Fill area under the curve
    plt.fill_between(yearly_stats['year'], yearly_stats['mean_flow_avg'], 
                     alpha=0.3, color='#2E86AB')
    
    # Customize the chart
    plt.title('Annual Average Flow (m³/s) Changes Over Years', 
              fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=14, fontweight='bold')
    plt.ylabel('Annual Average Flow (m³/s)', fontsize=14, fontweight='bold')
    
    # Set axis limits and ticks
    plt.xlim(yearly_stats['year'].min() - 0.5, yearly_stats['year'].max() + 0.5)
    plt.xticks(yearly_stats['year'], rotation=45)
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Add value labels on points
    for i, row in yearly_stats.iterrows():
        plt.annotate(f'{row["mean_flow_avg"]:.2f}', 
                    (row['year'], row['mean_flow_avg']),
                    textcoords="offset points", 
                    xytext=(0,15), 
                    ha='center',
                    fontsize=10,
                    fontweight='bold')
    
    # Add trend line
    if len(yearly_stats) > 1:
        z = np.polyfit(yearly_stats['year'], yearly_stats['mean_flow_avg'], 1)
        p = np.poly1d(z)
        plt.plot(yearly_stats['year'], p(yearly_stats['year']), 
                 "--", color='red', alpha=0.7, linewidth=2, 
                 label=f'Trend (slope: {z[0]:.4f})')
    
    # Add legend
    plt.legend(fontsize=12)
    
    # Add statistics text box
    stats_text = f"""Statistics:
Years: {len(yearly_stats)}
Flow Range: {yearly_stats['mean_flow_avg'].min():.2f} - {yearly_stats['mean_flow_avg'].max():.2f} m³/s
Overall Average: {yearly_stats['mean_flow_avg'].mean():.2f} m³/s
Total Stations: {len(df_flow['station_code'].unique())}"""
    
    plt.text(0.02, 0.98, stats_text, 
             transform=plt.gca().transAxes, 
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
             fontsize=11)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the chart
    output_path = "annual_average_flow_avg_yearly_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nChart saved to: {output_path}")
    
    # Show the chart
    plt.show()
    
    # Print summary statistics
    print(f"\nSummary Statistics:")
    print(f"Years covered: {yearly_stats['year'].min()} - {yearly_stats['year'].max()}")
    print(f"Number of years: {len(yearly_stats)}")
    print(f"Total stations: {len(df_flow['station_code'].unique())}")
    print(f"Flow range: {yearly_stats['mean_flow_avg'].min():.2f} - {yearly_stats['mean_flow_avg'].max():.2f} m³/s")
    print(f"Overall average: {yearly_stats['mean_flow_avg'].mean():.2f} m³/s")
    
    # Calculate trend
    if len(yearly_stats) > 1:
        trend_slope = z[0]
        if trend_slope > 0.001:
            trend_direction = "increasing"
        elif trend_slope < -0.001:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        print(f"Trend: {trend_direction} ({trend_slope:.4f} m³/s per year)")
    
    return yearly_stats

if __name__ == "__main__":
    yearly_stats = create_annual_flow_avg_chart()
    print("\n[SUCCESS] Annual average flow chart completed!")
