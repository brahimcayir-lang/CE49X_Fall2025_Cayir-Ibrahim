#!/usr/bin/env python3
"""
Create stations comparison chart using the exact data from dsi_2000_2020_final_structured_STD_CORRECTED.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def create_stations_comparison_from_given_data():
    """Create comparison chart using the exact CSV file provided by user"""
    
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
    
    # Create the main comparison chart
    plt.figure(figsize=(16, 10))
    
    # Define colors for different stations
    colors = plt.cm.Set3(np.linspace(0, 1, len(stations)))
    
    # Plot each station
    for i, station in enumerate(stations):
        station_data = df_flow[df_flow['station_code'] == station].copy()
        station_data = station_data.sort_values('year')
        
        if len(station_data) >= 2:
            plt.plot(station_data['year'], station_data['annual_avg_flow_m3s'], 
                     marker='o', linewidth=2, markersize=6,
                     color=colors[i], label=f'{station} ({len(station_data)} pts)',
                     alpha=0.8, markerfacecolor=colors[i], 
                     markeredgecolor='white', markeredgewidth=1)
        else:
            plt.scatter(station_data['year'], station_data['annual_avg_flow_m3s'], 
                       color=colors[i], s=100, label=f'{station} ({len(station_data)} pt)',
                       alpha=0.8, marker='o', edgecolor='white', linewidth=2)
    
    # Customize the chart
    plt.title('All Stations - Annual Flow Changes Comparison\n(Data from dsi_2000_2020_final_structured_STD_CORRECTED.csv)', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
    
    # Add legend with better positioning
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9, 
               frameon=True, fancybox=True, shadow=True)
    
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
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the chart
    output_path = "stations_comparison_from_given_data.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nComparison chart saved to: {output_path}")
    
    # Show the chart
    plt.show()
    
    # Create summary statistics
    print("\n=== STATION SUMMARY STATISTICS ===")
    summary_stats = df_flow.groupby('station_code')['annual_avg_flow_m3s'].agg([
        'count', 'mean', 'std', 'min', 'max'
    ]).round(3)
    summary_stats.columns = ['Data_Points', 'Mean_Flow', 'Std_Dev', 'Min_Flow', 'Max_Flow']
    print(summary_stats.to_string())
    
    # Save summary statistics
    summary_stats.to_csv("station_summary_from_given_data.csv")
    print(f"\nSummary statistics saved to: station_summary_from_given_data.csv")
    
    # Create additional analysis chart
    create_flow_analysis_chart(df_flow)
    
    return summary_stats

def create_flow_analysis_chart(df_flow):
    """Create additional analysis chart showing flow ranges and data completeness"""
    
    # Calculate statistics for each station
    station_stats = df_flow.groupby('station_code')['annual_avg_flow_m3s'].agg([
        'count', 'mean', 'std', 'min', 'max'
    ]).reset_index()
    
    # Filter stations with at least 3 data points for better visualization
    station_stats = station_stats[station_stats['count'] >= 3]
    
    # Create the chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    
    # Chart 1: Flow ranges with error bars
    stations = station_stats['station_code']
    means = station_stats['mean']
    stds = station_stats['std']
    mins = station_stats['min']
    maxs = station_stats['max']
    
    x_pos = np.arange(len(stations))
    
    # Plot mean values with error bars
    bars = ax1.bar(x_pos, means, alpha=0.7, color='skyblue', edgecolor='navy', linewidth=1)
    ax1.errorbar(x_pos, means, yerr=stds, fmt='none', color='red', capsize=5, capthick=2)
    
    # Add min/max markers
    ax1.scatter(x_pos, mins, color='green', marker='v', s=50, label='Min', alpha=0.8)
    ax1.scatter(x_pos, maxs, color='orange', marker='^', s=50, label='Max', alpha=0.8)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{height:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    ax1.set_title('Station Flow Statistics - Mean ± Std Dev, Min/Max Values\n(From Given Data)', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.set_xlabel('Station Code', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(stations, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Chart 2: Data points count per station
    counts = station_stats['count']
    bars2 = ax2.bar(x_pos, counts, alpha=0.7, color='lightcoral', edgecolor='darkred', linewidth=1)
    
    # Add count labels on bars
    for i, bar in enumerate(bars2):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    ax2.set_title('Data Points Count per Station\n(From Given Data)', fontsize=14, fontweight='bold', pad=20)
    ax2.set_xlabel('Station Code', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Number of Records', fontsize=12, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(stations, rotation=45, ha='right')
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    # Clean spines
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#666666')
        ax.spines['bottom'].set_color('#666666')
    
    plt.tight_layout()
    
    # Save the chart
    output_path = "station_flow_analysis_from_given_data.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nFlow analysis chart saved to: {output_path}")
    
    plt.show()

if __name__ == "__main__":
    print("Creating stations comparison chart from the given data file...")
    print("Using: dsi_2000_2020_final_structured_STD_CORRECTED.csv")
    
    # Create main comparison chart
    summary_stats = create_stations_comparison_from_given_data()
    
    print("\n[SUCCESS] Stations comparison charts completed!")
    print("All charts created using the exact data from your provided CSV file.")
