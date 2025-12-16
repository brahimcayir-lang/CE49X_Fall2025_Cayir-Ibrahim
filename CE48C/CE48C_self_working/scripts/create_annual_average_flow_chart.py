#!/usr/bin/env python3
"""
Create annual average flow chart showing annual_average_flow_avg_m3 trends over years
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats
from matplotlib.patches import Rectangle

# Set style for better-looking plots
plt.style.use('default')
sns.set_palette("husl")

def load_and_prepare_data(csv_file):
    """Load CSV data and prepare annual flow data"""
    df = pd.read_csv(csv_file)
    
    print(f"Data loaded: {len(df)} records")
    print(f"Years available: {sorted(df['year'].unique())}")
    print(f"Stations: {df['station_code'].nunique()}")
    
    return df

def create_annual_flow_chart(df):
    """Create comprehensive annual average flow chart"""
    
    # Group by year and calculate statistics
    yearly_stats = df.groupby('year')['annual_average_flow_avg_m3'].agg([
        'mean', 'median', 'std', 'min', 'max', 'count'
    ]).reset_index()
    
    # Calculate percentiles
    yearly_percentiles = df.groupby('year')['annual_average_flow_avg_m3'].quantile([0.25, 0.75]).reset_index()
    yearly_percentiles = yearly_percentiles.pivot(index='year', columns='level_1', values='annual_average_flow_avg_m3').reset_index()
    yearly_percentiles.columns = ['year', 'q25', 'q75']
    
    # Merge statistics
    yearly_data = yearly_stats.merge(yearly_percentiles, on='year')
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))
    
    # Main trend chart
    ax1 = plt.subplot(2, 2, 1)
    
    # Plot mean with error bars
    years = yearly_data['year']
    means = yearly_data['mean']
    stds = yearly_data['std']
    
    ax1.plot(years, means, 'o-', linewidth=3, markersize=8, 
             color='#2E86AB', label='Annual Mean', alpha=0.8)
    ax1.fill_between(years, means - stds, means + stds, 
                    alpha=0.3, color='#2E86AB', label='±1 Std Dev')
    
    # Add median line
    ax1.plot(years, yearly_data['median'], 's--', linewidth=2, markersize=6,
             color='#A23B72', label='Annual Median', alpha=0.8)
    
    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
    ax1.set_title('Annual Average Flow Trends (2005-2020)', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add trend line
    slope, intercept, r_value, p_value, std_err = stats.linregress(years, means)
    trend_line = slope * years + intercept
    ax1.plot(years, trend_line, 'r--', linewidth=2, alpha=0.7,
             label=f'Trend (R²={r_value**2:.3f})')
    ax1.legend()
    
    # Box plot by year
    ax2 = plt.subplot(2, 2, 2)
    
    # Prepare data for box plot
    box_data = []
    box_labels = []
    for year in sorted(df['year'].unique()):
        year_data = df[df['year'] == year]['annual_average_flow_avg_m3'].dropna()
        if len(year_data) > 0:
            box_data.append(year_data)
            box_labels.append(str(year))
    
    bp = ax2.boxplot(box_data, tick_labels=box_labels, patch_artist=True)
    
    # Color the boxes
    colors = plt.cm.viridis(np.linspace(0, 1, len(box_data)))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
    ax2.set_title('Annual Flow Distribution by Year', fontsize=14, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # Min-Max range chart
    ax3 = plt.subplot(2, 2, 3)
    
    ax3.fill_between(years, yearly_data['min'], yearly_data['max'], 
                    alpha=0.3, color='#F18F01', label='Min-Max Range')
    ax3.plot(years, yearly_data['min'], 'o-', color='#C73E1D', 
             linewidth=2, markersize=6, label='Minimum')
    ax3.plot(years, yearly_data['max'], 'o-', color='#2E86AB', 
             linewidth=2, markersize=6, label='Maximum')
    ax3.plot(years, means, 's-', color='#A23B72', 
             linewidth=3, markersize=8, label='Mean')
    
    ax3.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
    ax3.set_title('Annual Flow Range Analysis', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Statistics summary
    ax4 = plt.subplot(2, 2, 4)
    ax4.axis('off')
    
    # Calculate overall statistics
    overall_mean = df['annual_average_flow_avg_m3'].mean()
    overall_std = df['annual_average_flow_avg_m3'].std()
    overall_min = df['annual_average_flow_avg_m3'].min()
    overall_max = df['annual_average_flow_avg_m3'].max()
    cv = (overall_std / overall_mean) * 100
    
    # Trend analysis
    trend_direction = "Increasing" if slope > 0 else "Decreasing"
    trend_strength = "Strong" if abs(r_value) > 0.7 else "Moderate" if abs(r_value) > 0.4 else "Weak"
    
    stats_text = f"""STATISTICS SUMMARY (2005-2020)

Overall Statistics:
• Mean: {overall_mean:.3f} m³/s
• Std Dev: {overall_std:.3f} m³/s
• Min: {overall_min:.3f} m³/s
• Max: {overall_max:.3f} m³/s
• CV: {cv:.1f}%

Trend Analysis:
• Direction: {trend_direction}
• Strength: {trend_strength}
• R²: {r_value**2:.3f}
• Slope: {slope:.4f} m³/s/year
• P-value: {p_value:.4f}

Data Coverage:
• Years: {len(years)} years
• Stations: {df['station_code'].nunique()} stations
• Total Records: {len(df)} records
• Avg Records/Year: {len(df)/len(years):.1f}"""
    
    ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes, 
             verticalalignment='top', fontsize=11, fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the chart
    filename = 'annual_average_flow_trends_chart.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig, yearly_data

def create_station_comparison_chart(df):
    """Create chart comparing different stations over years"""
    
    # Get top 10 stations by average flow
    station_avg = df.groupby('station_code')['annual_average_flow_avg_m3'].mean().sort_values(ascending=False)
    top_stations = station_avg.head(10).index.tolist()
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(top_stations)))
    
    for i, station in enumerate(top_stations):
        station_data = df[df['station_code'] == station].sort_values('year')
        if len(station_data) > 1:  # Only plot stations with multiple years
            ax.plot(station_data['year'], station_data['annual_average_flow_avg_m3'], 
                   'o-', linewidth=2, markersize=6, color=colors[i], 
                   label=f'{station}', alpha=0.8)
    
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Stations - Annual Average Flow Trends', fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    filename = 'annual_flow_top_stations_comparison.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig

def create_decade_analysis_chart(df):
    """Create decade-based analysis chart"""
    
    # Define decades
    df['decade'] = df['year'].apply(lambda x: f"{x//10*10}s")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Decade comparison box plot
    decade_data = []
    decade_labels = []
    for decade in sorted(df['decade'].unique()):
        decade_flow = df[df['decade'] == decade]['annual_average_flow_avg_m3'].dropna()
        if len(decade_flow) > 0:
            decade_data.append(decade_flow)
            decade_labels.append(decade)
    
    bp = ax1.boxplot(decade_data, tick_labels=decade_labels, patch_artist=True)
    colors = ['#FF6B6B', '#4ECDC4']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax1.set_xlabel('Decade', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
    ax1.set_title('Decade Comparison of Annual Average Flow', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Decade statistics
    decade_stats = df.groupby('decade')['annual_average_flow_avg_m3'].agg(['mean', 'std', 'count']).reset_index()
    
    x_pos = np.arange(len(decade_stats))
    bars = ax2.bar(x_pos, decade_stats['mean'], yerr=decade_stats['std'], 
                   color=['#FF6B6B', '#4ECDC4'], alpha=0.7, capsize=5)
    
    ax2.set_xlabel('Decade', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Mean Annual Average Flow (m³/s)', fontsize=12, fontweight='bold')
    ax2.set_title('Decade Mean Comparison with Error Bars', fontsize=14, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(decade_stats['decade'])
    ax2.grid(True, alpha=0.3)
    
    # Add count labels on bars
    for i, (bar, count) in enumerate(zip(bars, decade_stats['count'])):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + decade_stats['std'].iloc[i],
                f'n={count}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    filename = 'annual_flow_decade_analysis.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig

def main():
    """Main function to create all annual flow charts"""
    
    csv_file = 'dsi_2000_2020_all_completed.csv'
    
    print("Loading data...")
    df = load_and_prepare_data(csv_file)
    
    print("\nCreating annual average flow trend chart...")
    fig1, yearly_data = create_annual_flow_chart(df)
    plt.close(fig1)
    
    print("\nCreating top stations comparison chart...")
    fig2 = create_station_comparison_chart(df)
    plt.close(fig2)
    
    print("\nCreating decade analysis chart...")
    fig3 = create_decade_analysis_chart(df)
    plt.close(fig3)
    
    print(f"\n[SUCCESS] All annual flow charts created successfully!")
    print(f"[CHARTS] Generated 3 comprehensive charts:")
    print(f"  - Annual average flow trends chart")
    print(f"  - Top stations comparison chart") 
    print(f"  - Decade analysis chart")
    print(f"[DATA] Analysis covers {len(df['year'].unique())} years ({min(df['year'])}-{max(df['year'])})")
    print(f"[STATIONS] {df['station_code'].nunique()} unique stations analyzed")

if __name__ == "__main__":
    main()
