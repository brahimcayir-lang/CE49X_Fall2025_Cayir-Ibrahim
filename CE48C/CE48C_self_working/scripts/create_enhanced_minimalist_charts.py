#!/usr/bin/env python3
"""
Create enhanced charts with numerical values and statistical details
Maintaining minimalist appearance with clean design
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def create_enhanced_monthly_chart():
    """Create enhanced monthly chart with statistical details"""
    
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
    
    # Create results dictionary with statistics
    monthly_stats = {}
    
    print("\n=== MONTHLY STATISTICS (CORRECTED DATA) ===")
    
    # Calculate monthly statistics for each metric
    for metric in monthly_metrics:
        print(f"\n--- {metric.upper()} ---")
        monthly_data = []
        
        for month in months:
            col = f"{month}_{metric}"
            # Get all values for this month
            values = df[col].dropna()
            if len(values) > 0:
                mean_val = values.mean()
                std_val = values.std()
                median_val = values.median()
                min_val = values.min()
                max_val = values.max()
                count_val = len(values)
                
                monthly_data.append({
                    'month': month,
                    'mean': mean_val,
                    'std': std_val,
                    'median': median_val,
                    'min': min_val,
                    'max': max_val,
                    'count': count_val
                })
                
                print(f"{month.upper()}: Mean={mean_val:.2f}, Std={std_val:.2f}, Count={count_val}")
        
        monthly_stats[metric] = monthly_data
    
    # Create enhanced visualization
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    
    # Clean, minimalist styling
    plt.style.use('default')
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = 10
    
    # Adjust spacing
    plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.92, bottom=0.08, left=0.08, right=0.95)
    
    metrics = list(monthly_stats.keys())
    metric_titles = [
        'Flow Max (m³/s)', 'Flow Min (m³/s)', 'Flow Avg (m³/s)',
        'LT/SN/Km²', 'AKIM mm', 'MIL M³'
    ]
    
    # Clean color palette
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    for i, (metric, title, color) in enumerate(zip(metrics, metric_titles, colors)):
        row = i // 3
        col = i % 3
        ax = axes[row, col]
        
        data = monthly_stats[metric]
        means = [d['mean'] for d in data]
        stds = [d['std'] for d in data]
        
        # Create clean line plot
        ax.plot(range(len(means)), means, marker='o', linewidth=2, markersize=6, 
                color=color, markerfacecolor=color, markeredgecolor='white', markeredgewidth=1)
        
        # Add error bars for standard deviation
        ax.errorbar(range(len(means)), means, yerr=stds, 
                   fmt='none', color=color, alpha=0.6, capsize=3, capthick=1)
        
        # Minimalist styling
        ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel('Month', fontsize=10, fontweight='bold')
        ax.set_ylabel('Value', fontsize=10, fontweight='bold')
        ax.set_xticks(range(len(month_names)))
        ax.set_xticklabels(month_names, fontsize=9)
        ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
        
        # Add numerical values as text
        for j, (mean_val, std_val) in enumerate(zip(means, stds)):
            ax.annotate(f'{mean_val:.1f}', (j, mean_val), 
                       textcoords="offset points", xytext=(0,8), 
                       ha='center', fontsize=8, fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.2", facecolor='white', 
                               alpha=0.8, edgecolor=color, linewidth=0.5))
        
        # Set clean background
        ax.set_facecolor('#fafafa')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#666666')
        ax.spines['bottom'].set_color('#666666')
    
    # Save the chart
    output_path = "monthly_changes_enhanced_minimalist.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nEnhanced monthly chart saved to: {output_path}")
    
    plt.show()
    
    return monthly_stats

def create_enhanced_yearly_chart():
    """Create enhanced yearly chart with statistical details"""
    
    # Read the corrected CSV
    csv_file = "dsi_2000_2020_final_structured_STD_CORRECTED.csv"
    df = pd.read_csv(csv_file)
    print(f"\nLoaded {len(df)} records from corrected dataset")
    
    # Filter out records with missing annual_average_flow_avg_m3
    df_flow = df[df['annual_average_flow_avg_m3'].notna()]
    print(f"Records with valid annual_average_flow_avg_m3: {len(df_flow)}")
    
    # Calculate detailed yearly statistics
    yearly_stats = df_flow.groupby('year')['annual_average_flow_avg_m3'].agg([
        'mean', 'std', 'median', 'min', 'max', 'count'
    ]).reset_index()
    
    print("\nDetailed yearly statistics:")
    print(yearly_stats.round(3).to_string(index=False))
    
    # Create enhanced chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Clean styling
    plt.style.use('default')
    plt.rcParams['font.family'] = 'Arial'
    
    # Main chart
    ax1.errorbar(yearly_stats['year'], yearly_stats['mean'], 
                 yerr=yearly_stats['std'], 
                 marker='o', linewidth=2, markersize=8,
                 color='#1f77b4', capsize=4, capthick=1.5,
                 markerfacecolor='#1f77b4', markeredgecolor='white', markeredgewidth=1)
    
    # Add trend line
    if len(yearly_stats) > 1:
        z = np.polyfit(yearly_stats['year'], yearly_stats['mean'], 1)
        p = np.poly1d(z)
        ax1.plot(yearly_stats['year'], p(yearly_stats['year']), 
                 "--", color='#ff7f0e', linewidth=2, alpha=0.8,
                 label=f'Trend: {z[0]:.3f} m³/s/year')
        ax1.legend(fontsize=10)
    
    # Minimalist styling
    ax1.set_title('Annual Average Flow Changes Over Years', fontsize=14, fontweight='bold', pad=20)
    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Average Flow (m³/s)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    ax1.set_facecolor('#fafafa')
    
    # Add numerical values
    for i, row in yearly_stats.iterrows():
        ax1.annotate(f'{row["mean"]:.2f}', (row['year'], row['mean']),
                    textcoords="offset points", xytext=(0,10), 
                    ha='center', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', 
                            alpha=0.8, edgecolor='#1f77b4', linewidth=0.5))
    
    # Statistics summary
    stats_text = f"""Statistical Summary:
Years: {len(yearly_stats)} | Stations: {len(df_flow['station_code'].unique())}
Range: {yearly_stats['mean'].min():.2f} - {yearly_stats['mean'].max():.2f} m³/s
Overall Mean: {yearly_stats['mean'].mean():.2f} m³/s
Std Dev: {yearly_stats['mean'].std():.2f} m³/s
Trend: {z[0]:.3f} m³/s/year"""
    
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
             verticalalignment='top', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, 
                      edgecolor='#666666', linewidth=0.5))
    
    # Secondary chart - Data count per year
    ax2.bar(yearly_stats['year'], yearly_stats['count'], 
            color='#2ca02c', alpha=0.7, edgecolor='white', linewidth=1)
    
    ax2.set_title('Data Points per Year', fontsize=12, fontweight='bold', pad=15)
    ax2.set_xlabel('Year', fontsize=10, fontweight='bold')
    ax2.set_ylabel('Number of Stations', fontsize=10, fontweight='bold')
    ax2.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    ax2.set_facecolor('#fafafa')
    
    # Add count values on bars
    for i, count in enumerate(yearly_stats['count']):
        ax2.annotate(f'{count}', (yearly_stats['year'].iloc[i], count),
                    textcoords="offset points", xytext=(0,3), 
                    ha='center', fontsize=9, fontweight='bold')
    
    # Clean spines
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#666666')
        ax.spines['bottom'].set_color('#666666')
    
    plt.tight_layout()
    
    # Save the chart
    output_path = "yearly_changes_enhanced_minimalist.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nEnhanced yearly chart saved to: {output_path}")
    
    plt.show()
    
    return yearly_stats

if __name__ == "__main__":
    print("Creating enhanced charts with statistical details...")
    
    # Create enhanced monthly chart
    monthly_stats = create_enhanced_monthly_chart()
    
    # Create enhanced yearly chart
    yearly_stats = create_enhanced_yearly_chart()
    
    print("\n[SUCCESS] Enhanced minimalist charts created!")
