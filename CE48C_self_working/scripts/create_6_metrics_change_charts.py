#!/usr/bin/env python3
"""
Create charts showing changes in 6 annual average metrics over time
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('default')
sns.set_palette("husl")

def load_and_prepare_data(csv_file):
    """Load CSV data and prepare annual metrics data"""
    df = pd.read_csv(csv_file)
    
    # Define the 6 annual average metrics
    metrics = {
        'Flow Max (m³/s)': {
            'column': 'annual_average_flow_max_m3',
            'color': '#FF6B6B',
            'unit': 'm³/s'
        },
        'Flow Min (m³/s)': {
            'column': 'annual_average_flow_min_m3',
            'color': '#4ECDC4',
            'unit': 'm³/s'
        },
        'Flow Average (m³/s)': {
            'column': 'annual_average_flow_avg_m3',
            'color': '#45B7D1',
            'unit': 'm³/s'
        },
        'Flow per km² (l/s/km²)': {
            'column': 'annual_average_ltsnkm2_m3',
            'color': '#96CEB4',
            'unit': 'l/s/km²'
        },
        'Flow in mm': {
            'column': 'annual_average_akim_mm_m3',
            'color': '#FFEAA7',
            'unit': 'mm'
        },
        'Flow in million m³': {
            'column': 'annual_average_milm3_m3',
            'color': '#DDA0DD',
            'unit': 'million m³'
        }
    }
    
    print(f"Data loaded: {len(df)} records")
    print(f"Years available: {sorted(df['year'].unique())}")
    print(f"Stations: {df['station_code'].nunique()}")
    
    return df, metrics

def create_metrics_trends_chart(df, metrics):
    """Create comprehensive trends chart for all 6 metrics"""
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    axes = axes.flatten()
    
    yearly_stats = {}
    
    for i, (metric_name, metric_info) in enumerate(metrics.items()):
        ax = axes[i]
        
        # Calculate yearly statistics
        yearly_data = df.groupby('year')[metric_info['column']].agg([
            'mean', 'median', 'std', 'min', 'max', 'count'
        ]).reset_index()
        
        yearly_stats[metric_name] = yearly_data
        
        years = yearly_data['year']
        means = yearly_data['mean']
        stds = yearly_data['std']
        
        # Plot mean with error bars
        ax.plot(years, means, 'o-', linewidth=3, markersize=8, 
                color=metric_info['color'], label='Mean', alpha=0.8)
        ax.fill_between(years, means - stds, means + stds, 
                       alpha=0.3, color=metric_info['color'], label='±1 Std Dev')
        
        # Add median line
        ax.plot(years, yearly_data['median'], 's--', linewidth=2, markersize=6,
                color='darkred', label='Median', alpha=0.8)
        
        # Add trend line
        slope, intercept, r_value, p_value, std_err = stats.linregress(years, means)
        trend_line = slope * years + intercept
        ax.plot(years, trend_line, 'r--', linewidth=2, alpha=0.7,
                label=f'Trend (R²={r_value**2:.3f})')
        
        ax.set_xlabel('Year', fontsize=10, fontweight='bold')
        ax.set_ylabel(f'{metric_name} ({metric_info["unit"]})', fontsize=10, fontweight='bold')
        ax.set_title(f'{metric_name} Trends', fontsize=12, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        
        # Add trend direction annotation
        trend_direction = "↗" if slope > 0 else "↘"
        ax.text(0.02, 0.98, f'Trend: {trend_direction}', transform=ax.transAxes, 
                verticalalignment='top', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.suptitle('Annual Average Metrics Trends (2005-2020)', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    filename = 'annual_metrics_trends_chart.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig, yearly_stats

def create_metrics_change_analysis(df, metrics):
    """Create change analysis chart showing percentage changes"""
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    axes = axes.flatten()
    
    for i, (metric_name, metric_info) in enumerate(metrics.items()):
        ax = axes[i]
        
        # Calculate yearly means
        yearly_means = df.groupby('year')[metric_info['column']].mean()
        
        # Calculate percentage change from first year
        first_year_value = yearly_means.iloc[0]
        percentage_changes = ((yearly_means - first_year_value) / first_year_value) * 100
        
        # Calculate year-to-year changes
        year_to_year_changes = yearly_means.pct_change() * 100
        
        years = yearly_means.index
        
        # Plot cumulative percentage change
        ax.plot(years, percentage_changes, 'o-', linewidth=3, markersize=8,
                color=metric_info['color'], label='Cumulative Change (%)', alpha=0.8)
        
        # Add zero line
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # Fill positive and negative areas
        ax.fill_between(years, percentage_changes, 0, 
                       where=(percentage_changes >= 0), 
                       color='green', alpha=0.2, label='Positive Change')
        ax.fill_between(years, percentage_changes, 0, 
                       where=(percentage_changes < 0), 
                       color='red', alpha=0.2, label='Negative Change')
        
        ax.set_xlabel('Year', fontsize=10, fontweight='bold')
        ax.set_ylabel('Change from 2005 (%)', fontsize=10, fontweight='bold')
        ax.set_title(f'{metric_name} - Change Analysis', fontsize=12, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        
        # Add final change annotation
        final_change = percentage_changes.iloc[-1]
        ax.text(0.02, 0.98, f'Total Change: {final_change:.1f}%', 
                transform=ax.transAxes, verticalalignment='top', 
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.suptitle('Annual Metrics Change Analysis (2005-2020)', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    filename = 'annual_metrics_change_analysis.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig

def create_metrics_comparison_chart(df, metrics):
    """Create normalized comparison chart of all metrics"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # Calculate yearly means for all metrics
    yearly_data = {}
    for metric_name, metric_info in metrics.items():
        yearly_data[metric_name] = df.groupby('year')[metric_info['column']].mean()
    
    years = list(yearly_data.values())[0].index
    
    # Plot 1: Normalized trends (z-score)
    for metric_name, metric_info in metrics.items():
        values = yearly_data[metric_name]
        normalized_values = (values - values.mean()) / values.std()
        ax1.plot(years, normalized_values, 'o-', linewidth=2, markersize=6,
                color=metric_info['color'], label=metric_name, alpha=0.8)
    
    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Normalized Values (Z-score)', fontsize=12, fontweight='bold')
    ax1.set_title('Normalized Comparison of All Metrics', fontsize=14, fontweight='bold')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # Plot 2: Correlation heatmap
    # Create correlation matrix
    metrics_df = pd.DataFrame(yearly_data)
    correlation_matrix = metrics_df.corr()
    
    im = ax2.imshow(correlation_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
    
    # Add correlation values as text
    for i in range(len(correlation_matrix.columns)):
        for j in range(len(correlation_matrix.index)):
            text = ax2.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                           ha="center", va="center", color="black", fontweight='bold')
    
    ax2.set_xticks(range(len(correlation_matrix.columns)))
    ax2.set_yticks(range(len(correlation_matrix.index)))
    ax2.set_xticklabels(correlation_matrix.columns, rotation=45, ha='right')
    ax2.set_yticklabels(correlation_matrix.index)
    ax2.set_title('Correlation Matrix Between Metrics', fontsize=14, fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax2)
    cbar.set_label('Correlation Coefficient', fontsize=10)
    
    plt.tight_layout()
    
    filename = 'annual_metrics_comparison_chart.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig

def create_decade_comparison_chart(df, metrics):
    """Create decade-based comparison chart"""
    
    # Define decades
    df['decade'] = df['year'].apply(lambda x: f"{x//10*10}s")
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    axes = axes.flatten()
    
    for i, (metric_name, metric_info) in enumerate(metrics.items()):
        ax = axes[i]
        
        # Calculate decade statistics
        decade_stats = df.groupby('decade')[metric_info['column']].agg([
            'mean', 'std', 'count'
        ]).reset_index()
        
        decades = decade_stats['decade']
        means = decade_stats['mean']
        stds = decade_stats['std']
        
        # Create bar chart with error bars
        bars = ax.bar(decades, means, yerr=stds, color=[metric_info['color'], '#FF9999'], 
                     alpha=0.7, capsize=5, edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel('Decade', fontsize=10, fontweight='bold')
        ax.set_ylabel(f'{metric_name} ({metric_info["unit"]})', fontsize=10, fontweight='bold')
        ax.set_title(f'{metric_name} - Decade Comparison', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, mean_val, std_val in zip(bars, means, stds):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + std_val + 0.05 * max(means),
                   f'{mean_val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Add change percentage
        if len(means) == 2:
            change_pct = ((means.iloc[1] - means.iloc[0]) / means.iloc[0]) * 100
            ax.text(0.5, 0.95, f'Change: {change_pct:.1f}%', transform=ax.transAxes,
                   ha='center', va='top', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.suptitle('Decade Comparison of Annual Metrics (2000s vs 2010s)', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    filename = 'annual_metrics_decade_comparison.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig

def create_summary_statistics_chart(df, metrics):
    """Create summary statistics chart"""
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Calculate overall statistics for each metric
    stats_data = []
    for metric_name, metric_info in metrics.items():
        values = df[metric_info['column']].dropna()
        stats_data.append({
            'Metric': metric_name,
            'Mean': values.mean(),
            'Std': values.std(),
            'Min': values.min(),
            'Max': values.max(),
            'CV': (values.std() / values.mean()) * 100
        })
    
    stats_df = pd.DataFrame(stats_data)
    
    # Create horizontal bar chart for coefficient of variation
    y_pos = np.arange(len(stats_df))
    bars = ax.barh(y_pos, stats_df['CV'], color=[metrics[metric]['color'] for metric in stats_df['Metric']], alpha=0.7)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(stats_df['Metric'])
    ax.set_xlabel('Coefficient of Variation (%)', fontsize=12, fontweight='bold')
    ax.set_title('Variability Analysis of Annual Metrics', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Add value labels
    for i, (bar, cv) in enumerate(zip(bars, stats_df['CV'])):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
               f'{cv:.1f}%', ha='left', va='center', fontweight='bold')
    
    # Add statistics text box
    stats_text = f"""Overall Statistics Summary:
    
Total Records: {len(df)}
Years: {df['year'].min()}-{df['year'].max()} ({df['year'].nunique()} years)
Stations: {df['station_code'].nunique()}

Most Variable Metric: {stats_df.loc[stats_df['CV'].idxmax(), 'Metric']}
Least Variable Metric: {stats_df.loc[stats_df['CV'].idxmin(), 'Metric']}"""
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            verticalalignment='top', fontsize=10, fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    
    filename = 'annual_metrics_summary_statistics.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig

def main():
    """Main function to create all metrics change charts"""
    
    csv_file = 'dsi_2000_2020_final_structured_FILLED.csv'
    
    print("Loading data...")
    df, metrics = load_and_prepare_data(csv_file)
    
    print(f"\nCreating charts for {len(metrics)} annual metrics...")
    
    # Create all charts
    print("\n1. Creating metrics trends chart...")
    fig1, yearly_stats = create_metrics_trends_chart(df, metrics)
    plt.close(fig1)
    
    print("\n2. Creating change analysis chart...")
    fig2 = create_metrics_change_analysis(df, metrics)
    plt.close(fig2)
    
    print("\n3. Creating comparison chart...")
    fig3 = create_metrics_comparison_chart(df, metrics)
    plt.close(fig3)
    
    print("\n4. Creating decade comparison chart...")
    fig4 = create_decade_comparison_chart(df, metrics)
    plt.close(fig4)
    
    print("\n5. Creating summary statistics chart...")
    fig5 = create_summary_statistics_chart(df, metrics)
    plt.close(fig5)
    
    print(f"\n[SUCCESS] All metrics change charts created successfully!")
    print(f"[CHARTS] Generated 5 comprehensive charts:")
    print(f"  - Annual metrics trends chart")
    print(f"  - Change analysis chart")
    print(f"  - Metrics comparison chart")
    print(f"  - Decade comparison chart")
    print(f"  - Summary statistics chart")
    print(f"[DATA] Analysis covers {df['year'].nunique()} years ({df['year'].min()}-{df['year'].max()})")
    print(f"[METRICS] {len(metrics)} annual average metrics analyzed")

if __name__ == "__main__":
    main()
