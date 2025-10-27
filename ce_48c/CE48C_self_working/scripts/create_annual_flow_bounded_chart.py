#!/usr/bin/env python3
"""
Create chart showing annual_avg_flow_m3s changes by year
With averages and ±3 standard deviation bounds
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def create_annual_flow_bounded_chart():
    """Create chart with annual_avg_flow_m3s and ±3 std deviation bounds"""
    
    # Read the corrected CSV
    csv_file = "dsi_2000_2020_final_structured_STD_CORRECTED.csv"
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} records from corrected dataset")
    
    # Filter out records with missing annual_avg_flow_m3s
    df_flow = df[df['annual_avg_flow_m3s'].notna()]
    print(f"Records with valid annual_avg_flow_m3s: {len(df_flow)}")
    
    # Calculate yearly statistics
    yearly_stats = df_flow.groupby('year')['annual_avg_flow_m3s'].agg([
        'mean', 'std', 'median', 'min', 'max', 'count'
    ]).reset_index()
    
    # Calculate ±3 standard deviation bounds
    yearly_stats['upper_bound'] = yearly_stats['mean'] + (3 * yearly_stats['std'])
    yearly_stats['lower_bound'] = yearly_stats['mean'] - (3 * yearly_stats['std'])
    
    # Ensure lower bound doesn't go below 0 (flow can't be negative)
    yearly_stats['lower_bound'] = yearly_stats['lower_bound'].clip(lower=0)
    
    print("\nYearly statistics with ±3 std bounds:")
    print(yearly_stats.round(3).to_string(index=False))
    
    # Create the chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Clean styling
    plt.style.use('default')
    plt.rcParams['font.family'] = 'Arial'
    
    # Main chart with bounds
    ax1.plot(yearly_stats['year'], yearly_stats['mean'], 
             marker='o', linewidth=3, markersize=8,
             color='#1f77b4', markerfacecolor='#1f77b4', 
             markeredgecolor='white', markeredgewidth=2,
             label='Annual Average Flow (m³/s)')
    
    # Fill area between bounds
    ax1.fill_between(yearly_stats['year'], yearly_stats['lower_bound'], 
                     yearly_stats['upper_bound'], alpha=0.2, color='#1f77b4',
                     label='±3 Standard Deviations')
    
    # Add bound lines
    ax1.plot(yearly_stats['year'], yearly_stats['upper_bound'], 
             '--', color='#ff7f0e', linewidth=1.5, alpha=0.7,
             label='Upper Bound (+3σ)')
    ax1.plot(yearly_stats['year'], yearly_stats['lower_bound'], 
             '--', color='#ff7f0e', linewidth=1.5, alpha=0.7,
             label='Lower Bound (-3σ)')
    
    # Add trend line
    if len(yearly_stats) > 1:
        z = np.polyfit(yearly_stats['year'], yearly_stats['mean'], 1)
        p = np.poly1d(z)
        ax1.plot(yearly_stats['year'], p(yearly_stats['year']), 
                 "-", color='#d62728', linewidth=2, alpha=0.8,
                 label=f'Trend: {z[0]:.3f} m³/s/year')
    
    # Minimalist styling
    ax1.set_title('Annual Average Flow (m³/s) with ±3 Standard Deviation Bounds', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Flow (m³/s)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    ax1.set_facecolor('#fafafa')
    ax1.legend(fontsize=10, loc='upper left')
    
    # Add numerical values
    for i, row in yearly_stats.iterrows():
        ax1.annotate(f'{row["mean"]:.2f}', (row['year'], row["mean"]),
                    textcoords="offset points", xytext=(0,10), 
                    ha='center', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', 
                            alpha=0.8, edgecolor='#1f77b4', linewidth=0.5))
    
    # Statistics summary
    stats_text = f"""Statistical Summary:
Years: {len(yearly_stats)} | Stations: {len(df_flow['station_code'].unique())}
Mean Range: {yearly_stats['mean'].min():.2f} - {yearly_stats['mean'].max():.2f} m³/s
Overall Mean: {yearly_stats['mean'].mean():.2f} m³/s
Avg Std Dev: {yearly_stats['std'].mean():.2f} m³/s
Trend: {z[0]:.3f} m³/s/year"""
    
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
             verticalalignment='top', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, 
                      edgecolor='#666666', linewidth=0.5))
    
    # Secondary chart - Standard deviation over time
    ax2.plot(yearly_stats['year'], yearly_stats['std'], 
             marker='s', linewidth=2, markersize=6,
             color='#2ca02c', markerfacecolor='#2ca02c', 
             markeredgecolor='white', markeredgewidth=1)
    
    ax2.fill_between(yearly_stats['year'], 0, yearly_stats['std'], 
                     alpha=0.3, color='#2ca02c')
    
    ax2.set_title('Standard Deviation of Annual Flow Over Years', 
                  fontsize=12, fontweight='bold', pad=15)
    ax2.set_xlabel('Year', fontsize=10, fontweight='bold')
    ax2.set_ylabel('Standard Deviation (m³/s)', fontsize=10, fontweight='bold')
    ax2.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    ax2.set_facecolor('#fafafa')
    
    # Add std values
    for i, row in yearly_stats.iterrows():
        ax2.annotate(f'{row["std"]:.2f}', (row['year'], row["std"]),
                    textcoords="offset points", xytext=(0,8), 
                    ha='center', fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', 
                            alpha=0.8, edgecolor='#2ca02c', linewidth=0.5))
    
    # Clean spines
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#666666')
        ax.spines['bottom'].set_color('#666666')
    
    plt.tight_layout()
    
    # Save the chart
    output_path = "annual_flow_bounded_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nBounded chart saved to: {output_path}")
    
    plt.show()
    
    # Print detailed statistics
    print(f"\nDetailed Statistics:")
    print(f"Years covered: {yearly_stats['year'].min()} - {yearly_stats['year'].max()}")
    print(f"Number of years: {len(yearly_stats)}")
    print(f"Total stations: {len(df_flow['station_code'].unique())}")
    print(f"Mean flow range: {yearly_stats['mean'].min():.2f} - {yearly_stats['mean'].max():.2f} m³/s")
    print(f"Overall mean: {yearly_stats['mean'].mean():.2f} m³/s")
    print(f"Average std dev: {yearly_stats['std'].mean():.2f} m³/s")
    print(f"Max std dev: {yearly_stats['std'].max():.2f} m³/s (Year {yearly_stats.loc[yearly_stats['std'].idxmax(), 'year']})")
    print(f"Min std dev: {yearly_stats['std'].min():.2f} m³/s (Year {yearly_stats.loc[yearly_stats['std'].idxmin(), 'year']})")
    
    if len(yearly_stats) > 1:
        print(f"Trend: {z[0]:.3f} m³/s per year")
    
    return yearly_stats

if __name__ == "__main__":
    yearly_stats = create_annual_flow_bounded_chart()
    print("\n[SUCCESS] Annual flow bounded chart completed!")
