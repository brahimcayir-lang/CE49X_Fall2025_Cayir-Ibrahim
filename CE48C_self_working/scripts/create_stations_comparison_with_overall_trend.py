#!/usr/bin/env python3
"""
Create stations comparison chart with overall trend line showing average flow change
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def create_stations_comparison_with_overall_trend():
    """Create comparison chart with overall trend line"""
    
    # Use the exact file path provided by user
    csv_file = "dsi_2000_2020_final_structured_STD_CORRECTED.csv"
    
    try:
        df = pd.read_csv(csv_file)
        print(f"Successfully loaded {len(df)} records from {csv_file}")
    except FileNotFoundError:
        print(f"Error: File {csv_file} not found!")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Filter out records with missing annual_avg_flow_m3s
    df_flow = df[df['annual_avg_flow_m3s'].notna()]
    print(f"Records with valid annual_avg_flow_m3s: {len(df_flow)}")
    
    # Get unique stations and their data counts
    stations = df_flow['station_code'].unique()
    print(f"Found {len(stations)} unique stations")
    
    # Count data points per station
    station_counts = df_flow['station_code'].value_counts()
    print("\nData points per station:")
    for station, count in station_counts.items():
        print(f"  {station}: {count} records")
    
    # Calculate overall yearly averages
    yearly_avg = df_flow.groupby('year')['annual_avg_flow_m3s'].agg(['mean', 'std', 'count']).reset_index()
    yearly_avg = yearly_avg.sort_values('year')
    
    print(f"\nOverall yearly averages calculated for {len(yearly_avg)} years")
    print("Year | Mean Flow | Std Dev | Count")
    print("----------------------------------")
    for _, row in yearly_avg.iterrows():
        print(f"{row['year']:.0f} | {row['mean']:.3f} | {row['std']:.3f} | {row['count']:>5}")
    
    # Create the main comparison chart
    plt.figure(figsize=(18, 12))
    
    # Define colors for different stations
    colors = plt.cm.Set3(np.linspace(0, 1, len(stations)))
    
    # Plot each station (lighter colors)
    for i, station in enumerate(stations):
        station_data = df_flow[df_flow['station_code'] == station].copy()
        station_data = station_data.sort_values('year')
        
        if len(station_data) >= 2:
            plt.plot(station_data['year'], station_data['annual_avg_flow_m3s'], 
                     marker='o', linewidth=1.5, markersize=4,
                     color=colors[i], alpha=0.6, 
                     markerfacecolor=colors[i], 
                     markeredgecolor='white', markeredgewidth=0.5)
        else:
            plt.scatter(station_data['year'], station_data['annual_avg_flow_m3s'], 
                       color=colors[i], s=60, alpha=0.6, marker='o', 
                       edgecolor='white', linewidth=0.5)
    
    # Plot overall trend line (bold and prominent)
    plt.plot(yearly_avg['year'], yearly_avg['mean'], 
             marker='s', linewidth=4, markersize=8,
             color='red', label='Overall Average Trend',
             markerfacecolor='red', markeredgecolor='white', 
             markeredgewidth=2, alpha=0.9)
    
    # Add error bars for overall trend
    plt.errorbar(yearly_avg['year'], yearly_avg['mean'], 
                yerr=yearly_avg['std'], fmt='none', 
                color='red', capsize=5, capthick=2, alpha=0.7)
    
    # Add trend line for overall average
    if len(yearly_avg) > 1:
        z = np.polyfit(yearly_avg['year'], yearly_avg['mean'], 1)
        p = np.poly1d(z)
        plt.plot(yearly_avg['year'], p(yearly_avg['year']), 
                 "--", color='darkred', linewidth=3, alpha=0.8,
                 label=f'Linear Trend: {z[0]:.4f} m³/s/year')
    
    # Customize the chart
    plt.title('All Stations - Annual Flow Changes Comparison\nWith Overall Average Trend Line', 
              fontsize=18, fontweight='bold', pad=25)
    plt.xlabel('Year', fontsize=14, fontweight='bold')
    plt.ylabel('Annual Average Flow (m³/s)', fontsize=14, fontweight='bold')
    
    # Add legend with better positioning
    legend_elements = []
    for i, station in enumerate(stations):
        count = station_counts[station]
        legend_elements.append(plt.Line2D([0], [0], color=colors[i], lw=2, 
                                        label=f'{station} ({count} pts)'))
    
    # Add overall trend to legend
    legend_elements.append(plt.Line2D([0], [0], color='red', lw=4, 
                                    label='Overall Average Trend'))
    
    plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), 
               loc='upper left', fontsize=9, frameon=True, 
               fancybox=True, shadow=True)
    
    # Add grid
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Set background color
    plt.gca().set_facecolor('#fafafa')
    
    # Clean spines
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#666666')
    ax.spines['bottom'].set_color('#666666')
    
    # Add text box with overall statistics
    overall_stats = f"""Overall Statistics:
Total Records: {len(df_flow)}
Years Covered: {df_flow['year'].min():.0f} - {df_flow['year'].max():.0f}
Overall Mean: {df_flow['annual_avg_flow_m3s'].mean():.3f} m³/s
Overall Std Dev: {df_flow['annual_avg_flow_m3s'].std():.3f} m³/s
Flow Range: {df_flow['annual_avg_flow_m3s'].min():.3f} - {df_flow['annual_avg_flow_m3s'].max():.3f} m³/s"""
    
    plt.text(0.02, 0.98, overall_stats, transform=ax.transAxes, 
             verticalalignment='top', fontsize=11,
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, 
                      edgecolor='red', linewidth=2))
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the chart
    output_path = "stations_comparison_with_overall_trend.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nComparison chart with overall trend saved to: {output_path}")
    
    # Show the chart
    plt.show()
    
    # Create additional analysis chart showing overall trend more clearly
    create_overall_trend_analysis_chart(yearly_avg, df_flow)
    
    # Create summary statistics
    print("\n=== STATION SUMMARY STATISTICS ===")
    summary_stats = df_flow.groupby('station_code')['annual_avg_flow_m3s'].agg([
        'count', 'mean', 'std', 'min', 'max'
    ]).round(3)
    summary_stats.columns = ['Data_Points', 'Mean_Flow', 'Std_Dev', 'Min_Flow', 'Max_Flow']
    print(summary_stats.to_string())
    
    # Save summary statistics
    summary_stats.to_csv("station_summary_with_overall_trend.csv")
    print(f"\nSummary statistics saved to: station_summary_with_overall_trend.csv")
    
    return summary_stats, yearly_avg

def create_overall_trend_analysis_chart(yearly_avg, df_flow):
    """Create a focused chart showing the overall trend analysis"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # Chart 1: Overall trend with confidence interval
    ax1.plot(yearly_avg['year'], yearly_avg['mean'], 
             marker='o', linewidth=3, markersize=8,
             color='red', label='Overall Average',
             markerfacecolor='red', markeredgecolor='white', 
             markeredgewidth=2)
    
    # Add confidence interval (mean ± std)
    ax1.fill_between(yearly_avg['year'], 
                    yearly_avg['mean'] - yearly_avg['std'],
                    yearly_avg['mean'] + yearly_avg['std'],
                    alpha=0.3, color='red', label='±1 Standard Deviation')
    
    # Add trend line
    if len(yearly_avg) > 1:
        z = np.polyfit(yearly_avg['year'], yearly_avg['mean'], 1)
        p = np.poly1d(z)
        ax1.plot(yearly_avg['year'], p(yearly_avg['year']), 
                 "--", color='darkred', linewidth=3, alpha=0.8,
                 label=f'Linear Trend: {z[0]:.4f} m³/s/year')
    
    ax1.set_title('Overall Flow Trend Analysis\n(All Stations Combined)', 
                  fontsize=16, fontweight='bold', pad=20)
    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, row in yearly_avg.iterrows():
        ax1.annotate(f'{row["mean"]:.2f}', 
                    (row['year'], row['mean']),
                    textcoords="offset points", xytext=(0,15), 
                    ha='center', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                            alpha=0.8, edgecolor='red', linewidth=1))
    
    # Chart 2: Number of stations contributing to each year
    ax2.bar(yearly_avg['year'], yearly_avg['count'], 
            alpha=0.7, color='skyblue', edgecolor='navy', linewidth=1)
    
    ax2.set_title('Number of Stations Contributing to Each Year', 
                  fontsize=16, fontweight='bold', pad=20)
    ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Number of Stations', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    # Add count labels on bars
    for i, row in yearly_avg.iterrows():
        ax2.text(row['year'], row['count'] + 0.1, f'{int(row["count"])}', 
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Clean spines
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#666666')
        ax.spines['bottom'].set_color('#666666')
    
    plt.tight_layout()
    
    # Save the chart
    output_path = "overall_trend_analysis.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nOverall trend analysis chart saved to: {output_path}")
    
    plt.show()

if __name__ == "__main__":
    print("Creating stations comparison chart with overall trend...")
    print("Using: dsi_2000_2020_final_structured_STD_CORRECTED.csv")
    
    # Create main comparison chart with overall trend
    summary_stats, yearly_avg = create_stations_comparison_with_overall_trend()
    
    print("\n[SUCCESS] Stations comparison charts with overall trend completed!")
    print("Charts now show both individual station patterns and overall average trend.")
