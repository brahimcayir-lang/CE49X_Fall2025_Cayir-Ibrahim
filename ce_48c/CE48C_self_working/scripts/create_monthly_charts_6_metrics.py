#!/usr/bin/env python3
"""
Create monthly charts for 6 hydrological metrics from DSI data
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import seaborn as sns

# Set style for better-looking plots
plt.style.use('default')
sns.set_palette("husl")

def load_and_prepare_data(csv_file):
    """Load CSV data and prepare monthly data"""
    df = pd.read_csv(csv_file)
    
    # Define the 6 metrics and their monthly columns
    metrics = {
        'Flow Max (m³/s)': {
            'columns': ['oct_flow_max_m3', 'nov_flow_max_m3', 'dec_flow_max_m3', 
                       'jan_flow_max_m3', 'feb_flow_max_m3', 'mar_flow_max_m3',
                       'apr_flow_max_m3', 'may_flow_max_m3', 'jun_flow_max_m3',
                       'jul_flow_max_m3', 'aug_flow_max_m3', 'sep_flow_max_m3'],
            'color': '#FF6B6B',
            'unit': 'm³/s'
        },
        'Flow Min (m³/s)': {
            'columns': ['oct_flow_min_m3', 'nov_flow_min_m3', 'dec_flow_min_m3',
                       'jan_flow_min_m3', 'feb_flow_min_m3', 'mar_flow_min_m3',
                       'apr_flow_min_m3', 'may_flow_min_m3', 'jun_flow_min_m3',
                       'jul_flow_min_m3', 'aug_flow_min_m3', 'sep_flow_min_m3'],
            'color': '#4ECDC4',
            'unit': 'm³/s'
        },
        'Flow Average (m³/s)': {
            'columns': ['oct_flow_avg_m3', 'nov_flow_avg_m3', 'dec_flow_avg_m3',
                       'jan_flow_avg_m3', 'feb_flow_avg_m3', 'mar_flow_avg_m3',
                       'apr_flow_avg_m3', 'may_flow_avg_m3', 'jun_flow_avg_m3',
                       'jul_flow_avg_m3', 'aug_flow_avg_m3', 'sep_flow_avg_m3'],
            'color': '#45B7D1',
            'unit': 'm³/s'
        },
        'Flow per km² (l/s/km²)': {
            'columns': ['oct_ltsnkm2_m3', 'nov_ltsnkm2_m3', 'dec_ltsnkm2_m3',
                       'jan_ltsnkm2_m3', 'feb_ltsnkm2_m3', 'mar_ltsnkm2_m3',
                       'apr_ltsnkm2_m3', 'may_ltsnkm2_m3', 'jun_ltsnkm2_m3',
                       'jul_ltsnkm2_m3', 'aug_ltsnkm2_m3', 'sep_ltsnkm2_m3'],
            'color': '#96CEB4',
            'unit': 'l/s/km²'
        },
        'Flow in mm': {
            'columns': ['oct_akim_mm_m3', 'nov_akim_mm_m3', 'dec_akim_mm_m3',
                       'jan_akim_mm_m3', 'feb_akim_mm_m3', 'mar_akim_mm_m3',
                       'apr_akim_mm_m3', 'may_akim_mm_m3', 'jun_akim_mm_m3',
                       'jul_akim_mm_m3', 'aug_akim_mm_m3', 'sep_akim_mm_m3'],
            'color': '#FFEAA7',
            'unit': 'mm'
        },
        'Flow in million m³': {
            'columns': ['oct_milm3_m3', 'nov_milm3_m3', 'dec_milm3_m3',
                       'jan_milm3_m3', 'feb_milm3_m3', 'mar_milm3_m3',
                       'apr_milm3_m3', 'may_milm3_m3', 'jun_milm3_m3',
                       'jul_milm3_m3', 'aug_milm3_m3', 'sep_milm3_m3'],
            'color': '#DDA0DD',
            'unit': 'million m³'
        }
    }
    
    # Month names for display (starting from October)
    month_names = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 
                   'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
    
    return df, metrics, month_names

def create_monthly_chart(df, metrics, month_names, metric_name, metric_info):
    """Create a monthly chart for a specific metric"""
    
    # Extract monthly data for this metric
    monthly_data = df[metric_info['columns']].copy()
    
    # Calculate statistics
    monthly_mean = monthly_data.mean()
    monthly_std = monthly_data.std()
    monthly_median = monthly_data.median()
    monthly_q25 = monthly_data.quantile(0.25)
    monthly_q75 = monthly_data.quantile(0.75)
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Plot 1: Monthly averages with error bars
    x_pos = np.arange(len(month_names))
    
    ax1.bar(x_pos, monthly_mean, yerr=monthly_std, 
            color=metric_info['color'], alpha=0.7, 
            capsize=5, edgecolor='black', linewidth=0.5)
    
    ax1.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax1.set_ylabel(f'{metric_name} ({metric_info["unit"]})', fontsize=12, fontweight='bold')
    ax1.set_title(f'Monthly {metric_name} - Average Values with Standard Deviation', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(month_names)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, (mean_val, std_val) in enumerate(zip(monthly_mean, monthly_std)):
        ax1.text(i, mean_val + std_val + 0.05 * max(monthly_mean), 
                f'{mean_val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Plot 2: Box plot for distribution
    box_data = [monthly_data[col].dropna() for col in metric_info['columns']]
    
    bp = ax2.boxplot(box_data, tick_labels=month_names, patch_artist=True)
    
    # Color the boxes
    for patch in bp['boxes']:
        patch.set_facecolor(metric_info['color'])
        patch.set_alpha(0.7)
    
    ax2.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax2.set_ylabel(f'{metric_name} ({metric_info["unit"]})', fontsize=12, fontweight='bold')
    ax2.set_title(f'Monthly {metric_name} - Distribution Analysis', 
                  fontsize=14, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3)
    
    # Add statistics text
    stats_text = f"""Statistics Summary:
    Mean: {monthly_mean.mean():.3f} {metric_info['unit']}
    Std Dev: {monthly_std.mean():.3f} {metric_info['unit']}
    Min Monthly Avg: {monthly_mean.min():.3f} {metric_info['unit']}
    Max Monthly Avg: {monthly_mean.max():.3f} {metric_info['unit']}
    CV: {(monthly_std.mean() / monthly_mean.mean() * 100):.1f}%"""
    
    ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes, 
             verticalalignment='top', fontsize=10, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the chart
    filename = f'monthly_{metric_name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_per_")}_chart.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig

def create_comparison_chart(df, metrics, month_names):
    """Create a comparison chart showing all 6 metrics"""
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    x_pos = np.arange(len(month_names))
    width = 0.12  # Width of bars
    
    for i, (metric_name, metric_info) in enumerate(metrics.items()):
        monthly_data = df[metric_info['columns']].copy()
        monthly_mean = monthly_data.mean()
        
        # Normalize data for comparison (z-score normalization)
        normalized_data = (monthly_mean - monthly_mean.mean()) / monthly_mean.std()
        
        ax.bar(x_pos + i * width, normalized_data, width, 
               label=metric_name, color=metric_info['color'], alpha=0.8)
    
    ax.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax.set_ylabel('Normalized Values (Z-score)', fontsize=12, fontweight='bold')
    ax.set_title('Monthly Comparison of All 6 Hydrological Metrics (Normalized)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x_pos + width * 2.5)
    ax.set_xticklabels(month_names)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('monthly_all_metrics_comparison_chart.png', dpi=300, bbox_inches='tight')
    print("Created comparison chart: monthly_all_metrics_comparison_chart.png")
    
    return fig

def create_seasonal_analysis_chart(df, metrics, month_names):
    """Create seasonal analysis chart"""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    # Define seasons
    seasons = {
        'Autumn': ['Oct', 'Nov', 'Dec'],
        'Winter': ['Jan', 'Feb', 'Mar'],
        'Spring': ['Apr', 'May', 'Jun'],
        'Summer': ['Jul', 'Aug', 'Sep']
    }
    
    for i, (metric_name, metric_info) in enumerate(metrics.items()):
        ax = axes[i]
        
        monthly_data = df[metric_info['columns']].copy()
        monthly_mean = monthly_data.mean()
        
        # Calculate seasonal averages
        seasonal_means = {}
        for season, months in seasons.items():
            season_indices = [month_names.index(month) for month in months]
            seasonal_means[season] = monthly_mean.iloc[season_indices].mean()
        
        # Create pie chart for seasonal distribution
        colors = ['#FF9999', '#66B3FF', '#99FF99', '#FFCC99']
        wedges, texts, autotexts = ax.pie(seasonal_means.values(), 
                                        labels=seasonal_means.keys(),
                                        colors=colors,
                                        autopct='%1.1f%%',
                                        startangle=90)
        
        ax.set_title(f'{metric_name}\nSeasonal Distribution', 
                    fontsize=12, fontweight='bold')
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
    
    plt.suptitle('Seasonal Analysis of Hydrological Metrics', 
                 fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig('monthly_seasonal_analysis_chart.png', dpi=300, bbox_inches='tight')
    print("Created seasonal analysis chart: monthly_seasonal_analysis_chart.png")
    
    return fig

def main():
    """Main function to create all monthly charts"""
    
    csv_file = 'dsi_2000_2020_final_structured_STD_CORRECTED_FILLED_BY_STATION_ROUNDED_FILLED_VALUES.csv'
    
    print("Loading data...")
    df, metrics, month_names = load_and_prepare_data(csv_file)
    
    print(f"Data loaded: {len(df)} stations, {len(df.columns)} columns")
    print(f"Creating charts for {len(metrics)} metrics...")
    
    # Create individual charts for each metric
    charts = []
    for metric_name, metric_info in metrics.items():
        print(f"\nCreating chart for {metric_name}...")
        fig = create_monthly_chart(df, metrics, month_names, metric_name, metric_info)
        charts.append(fig)
        plt.close(fig)
    
    # Create comparison chart
    print(f"\nCreating comparison chart...")
    fig_comparison = create_comparison_chart(df, metrics, month_names)
    plt.close(fig_comparison)
    
    # Create seasonal analysis chart
    print(f"\nCreating seasonal analysis chart...")
    fig_seasonal = create_seasonal_analysis_chart(df, metrics, month_names)
    plt.close(fig_seasonal)
    
    print(f"\n[SUCCESS] All charts created successfully!")
    print(f"[CHARTS] Generated {len(metrics)} individual metric charts")
    print(f"[COMPARISON] Generated 1 comparison chart")
    print(f"[SEASONAL] Generated 1 seasonal analysis chart")
    print(f"[TOTAL] Total: {len(metrics) + 2} chart files")

if __name__ == "__main__":
    main()
