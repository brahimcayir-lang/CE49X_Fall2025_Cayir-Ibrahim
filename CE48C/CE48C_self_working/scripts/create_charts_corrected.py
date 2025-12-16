#!/usr/bin/env python3
"""
Create both charts using the corrected dataset:
1. 6 metric monthly changes chart
2. Annual average flow yearly changes chart
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def create_monthly_charts_corrected():
    """Create monthly changes chart using corrected data"""
    
    # Read the corrected CSV
    csv_file = "dsi_2000_2020_final_structured_STD_CORRECTED.csv"
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} records from corrected dataset")
    
    # Define all monthly metric columns (6 metrics x 12 months)
    monthly_metrics = [
        'flow_max_m3', 'flow_min_m3', 'flow_avg_m3', 
        'ltsnkm2_m3', 'akim_mm_m3', 'milm3_m3'
    ]
    
    # Reorder months to start from January
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Create results dictionary
    monthly_averages = {}
    
    print("\n=== MONTHLY AVERAGES (CORRECTED DATA) ===")
    
    # Calculate monthly averages for each metric
    for metric in monthly_metrics:
        print(f"\n--- {metric.upper()} ---")
        monthly_vals = []
        
        for month in months:
            col = f"{month}_{metric}"
            # Calculate average of this month across all years
            month_avg = df[col].mean()
            monthly_vals.append(month_avg)
            print(f"{month.upper()}: {month_avg:.2f}")
        
        monthly_averages[metric] = monthly_vals
    
    # Create visualization without main title
    fig, axes = plt.subplots(2, 3, figsize=(24, 16))
    
    # No main title - just use the space for charts
    plt.subplots_adjust(hspace=0.5, wspace=0.4, top=0.95, bottom=0.1, left=0.08, right=0.95)
    
    metrics = list(monthly_averages.keys())
    metric_titles = [
        'Flow Max (m³/s)', 'Flow Min (m³/s)', 'Flow Avg (m³/s)',
        'LT/SN/Km²', 'AKIM mm', 'MIL M³'
    ]
    
    # Define colors for each metric
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#7209B7', '#2D5016']
    
    for i, (metric, title, color) in enumerate(zip(metrics, metric_titles, colors)):
        row = i // 3
        col = i % 3
        ax = axes[row, col]
        
        values = monthly_averages[metric]
        
        # Create line plot with better styling
        ax.plot(range(12), values, marker='o', linewidth=3, markersize=12, 
                color=color, markerfacecolor=color, markeredgecolor='white', markeredgewidth=2)
        ax.fill_between(range(12), values, alpha=0.2, color=color)
        
        # Customize the plot with larger fonts
        ax.set_title(title, fontsize=18, fontweight='bold', pad=25)
        ax.set_xlabel('Month', fontsize=16, fontweight='bold', labelpad=20)
        ax.set_ylabel('Average Value', fontsize=16, fontweight='bold', labelpad=20)
        ax.set_xticks(range(12))
        ax.set_xticklabels(month_names, rotation=45, fontsize=14, ha='right')
        ax.tick_params(axis='y', labelsize=14)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add value labels with good spacing
        for j, val in enumerate(values):
            if not np.isnan(val):
                # Alternate label positions
                if j % 2 == 0:
                    y_offset = 25
                else:
                    y_offset = -30
                
                ax.annotate(f'{val:.1f}', (j, val), textcoords="offset points", 
                           xytext=(0, y_offset), ha='center', fontsize=12, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.95, 
                                   edgecolor=color, linewidth=2))
        
        # Set y-axis to start from 0 for better visualization
        ax.set_ylim(bottom=0)
        
        # Add subtle background color
        ax.set_facecolor('#f8f9fa')
        
        # Increase tick label spacing
        ax.tick_params(axis='x', pad=15)
        ax.tick_params(axis='y', pad=15)
    
    # Save the chart
    output_path = "monthly_changes_analysis_CORRECTED.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nMonthly chart saved to: {output_path}")
    
    plt.show()
    
    return monthly_averages

def create_yearly_chart_corrected():
    """Create yearly changes chart using corrected data"""
    
    # Read the corrected CSV
    csv_file = "dsi_2000_2020_final_structured_STD_CORRECTED.csv"
    df = pd.read_csv(csv_file)
    print(f"\nLoaded {len(df)} records from corrected dataset")
    
    # Filter out records with missing annual_average_flow_avg_m3
    df_flow = df[df['annual_average_flow_avg_m3'].notna()]
    print(f"Records with valid annual_average_flow_avg_m3: {len(df_flow)}")
    
    # Calculate yearly average and statistics
    yearly_stats = df_flow.groupby('year')['annual_average_flow_avg_m3'].agg(['mean', 'std', 'count']).reset_index()
    yearly_stats.columns = ['year', 'mean_flow_avg', 'std_flow_avg', 'count']
    
    print("\nYearly statistics for annual_average_flow_avg_m3 (CORRECTED):")
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
    plt.title('Annual Average Flow (m³/s) Changes Over Years (CORRECTED DATA)', 
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
    stats_text = f"""Statistics (CORRECTED):
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
    output_path = "annual_average_flow_avg_yearly_chart_CORRECTED.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nYearly chart saved to: {output_path}")
    
    # Show the chart
    plt.show()
    
    # Print summary statistics
    print(f"\nSummary Statistics (CORRECTED):")
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
    print("Creating charts using CORRECTED dataset...")
    
    # Create monthly charts
    monthly_averages = create_monthly_charts_corrected()
    
    # Create yearly chart
    yearly_stats = create_yearly_chart_corrected()
    
    print("\n[SUCCESS] Both charts created using corrected data!")
