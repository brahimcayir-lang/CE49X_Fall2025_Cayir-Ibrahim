#!/usr/bin/env python3
"""
Create annual flow change chart by years using the latest filled and rounded dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def create_annual_flow_change_chart():
    """Create annual flow change chart using the latest dataset"""
    
    # Use the latest dataset with filled and rounded values
    csv_file = "dsi_2000_2020_final_structured_STD_CORRECTED_FILLED_BY_STATION_ROUNDED_FILLED_VALUES.csv"
    
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
    
    # Calculate yearly statistics
    yearly_stats = df_flow.groupby('year')['annual_avg_flow_m3s'].agg([
        'count', 'mean', 'std', 'min', 'max', 'median'
    ]).reset_index()
    
    yearly_stats = yearly_stats.sort_values('year')
    
    print(f"\nYearly statistics calculated for {len(yearly_stats)} years")
    print("Year | Count | Mean | Std Dev | Min | Max | Median")
    print("---------------------------------------------------")
    for _, row in yearly_stats.iterrows():
        print(f"{row['year']:.0f} | {row['count']:>5} | {row['mean']:.3f} | {row['std']:.3f} | {row['min']:.3f} | {row['max']:.3f} | {row['median']:.3f}")
    
    # Create the main chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # Chart 1: Annual flow changes with trend
    ax1.plot(yearly_stats['year'], yearly_stats['mean'], 
             marker='o', linewidth=3, markersize=8,
             color='#1f77b4', label='Annual Average Flow',
             markerfacecolor='#1f77b4', markeredgecolor='white', 
             markeredgewidth=2)
    
    # Add trend line
    if len(yearly_stats) > 1:
        z = np.polyfit(yearly_stats['year'], yearly_stats['mean'], 1)
        p = np.poly1d(z)
        ax1.plot(yearly_stats['year'], p(yearly_stats['year']), 
                 "--", color='#ff7f0e', linewidth=3, alpha=0.8,
                 label=f'Linear Trend: {z[0]:.4f} m³/s/year')
    
    # Add value labels
    for i, row in yearly_stats.iterrows():
        ax1.annotate(f'{row["mean"]:.2f}', 
                    (row['year'], row['mean']),
                    textcoords="offset points", xytext=(0,15), 
                    ha='center', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                            alpha=0.8, edgecolor='#1f77b4', linewidth=1))
    
    ax1.set_title('Annual Flow Changes by Year\n(Using Latest Filled and Rounded Dataset)', 
                  fontsize=16, fontweight='bold', pad=20)
    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Chart 2: Number of stations contributing to each year
    bars = ax2.bar(yearly_stats['year'], yearly_stats['count'], 
                   alpha=0.7, color='#2ca02c', edgecolor='darkgreen', linewidth=1)
    
    # Add count labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{int(height)}', 
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax2.set_title('Number of Stations Contributing to Each Year', 
                  fontsize=16, fontweight='bold', pad=20)
    ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Number of Stations', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    # Clean spines for both charts
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#666666')
        ax.spines['bottom'].set_color('#666666')
    
    plt.tight_layout()
    
    # Save the chart
    output_path = "annual_flow_change_latest_dataset.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nAnnual flow change chart saved to: {output_path}")
    
    plt.show()
    
    # Create additional analysis chart
    create_flow_analysis_chart(yearly_stats, df_flow)
    
    # Create summary statistics
    print("\n=== OVERALL STATISTICS ===")
    overall_stats = df_flow['annual_avg_flow_m3s'].describe()
    print(overall_stats.to_string())
    
    # Save yearly statistics
    yearly_stats.to_csv("yearly_flow_statistics_latest.csv", index=False)
    print(f"\nYearly statistics saved to: yearly_flow_statistics_latest.csv")
    
    return yearly_stats

def create_flow_analysis_chart(yearly_stats, df_flow):
    """Create additional analysis chart showing flow variability"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Chart 1: Flow variability (std dev)
    ax1.plot(yearly_stats['year'], yearly_stats['std'], 
             marker='s', linewidth=2, markersize=6,
             color='#d62728', label='Standard Deviation',
             markerfacecolor='#d62728', markeredgecolor='white', 
             markeredgewidth=1)
    
    ax1.set_title('Flow Variability (Standard Deviation) by Year', 
                  fontsize=14, fontweight='bold', pad=15)
    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Standard Deviation (m³/s)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Chart 2: Flow range (max - min)
    flow_range = yearly_stats['max'] - yearly_stats['min']
    ax2.plot(yearly_stats['year'], flow_range, 
             marker='^', linewidth=2, markersize=6,
             color='#9467bd', label='Flow Range (Max - Min)',
             markerfacecolor='#9467bd', markeredgecolor='white', 
             markeredgewidth=1)
    
    ax2.set_title('Flow Range (Max - Min) by Year', 
                  fontsize=14, fontweight='bold', pad=15)
    ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Flow Range (m³/s)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    # Clean spines
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#666666')
        ax.spines['bottom'].set_color('#666666')
    
    plt.tight_layout()
    
    # Save the chart
    output_path = "flow_variability_analysis_latest.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nFlow variability analysis chart saved to: {output_path}")
    
    plt.show()

if __name__ == "__main__":
    print("Creating annual flow change chart using latest dataset...")
    print("Using: dsi_2000_2020_final_structured_STD_CORRECTED_FILLED_BY_STATION_ROUNDED_FILLED_VALUES.csv")
    
    # Create annual flow change chart
    yearly_stats = create_annual_flow_change_chart()
    
    print("\n[SUCCESS] Annual flow change chart completed!")
    print("Chart shows flow changes using the latest filled and rounded dataset.")
