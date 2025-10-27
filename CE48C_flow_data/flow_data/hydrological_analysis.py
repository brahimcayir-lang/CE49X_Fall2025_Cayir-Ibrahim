"""
Hydrological Analysis and Derived Metrics
Computes various hydrological metrics and creates visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# Read data
df = pd.read_csv('dsi_final_excluding_extremes.csv')

print("Dataset loaded successfully!")
print(f"Total records: {len(df)}")
print(f"Stations: {df['station_code'].nunique()}")
print(f"Years: {df['year'].nunique()}")
print(f"Date range: {df['year'].min()} - {df['year'].max()}\n")

# ====================================================================
# 1. COMPUTE DERIVED METRICS
# ====================================================================

def compute_derived_metrics(df):
    """
    Compute hydrological derived metrics for each record
    """
    df_metrics = df.copy()
    
    # Define monthly columns
    months = ['oct', 'nov', 'dec', 'jan', 'feb', 'mar', 
              'apr', 'may', 'jun', 'jul', 'aug', 'sep']
    
    max_cols = [f'{month}_max' for month in months]
    min_cols = [f'{month}_min' for month in months]
    avg_cols = [f'{month}_avg' for month in months]
    mm_cols = [f'{month}_mm' for month in months]
    
    # 1. Flow Variability Index = max_flow / mean_flow
    print("Computing Flow Variability Index...")
    df_metrics['max_flow'] = df_metrics[max_cols].max(axis=1)
    df_metrics['min_flow'] = df_metrics[min_cols].min(axis=1)
    df_metrics['mean_flow'] = df_metrics[avg_cols].mean(axis=1)
    df_metrics['flow_variability_index'] = df_metrics['max_flow'] / df_metrics['mean_flow']
    
    # 2. Baseflow Index = min_flow / mean_flow (river permanence indicator)
    print("Computing Baseflow Index...")
    df_metrics['baseflow_index'] = df_metrics['min_flow'] / df_metrics['mean_flow']
    
    # 3. Hydrological Yield = annual_total_m3 / catchment_area_km2 (already computed as annual_mm)
    print("Hydrological Yield already in dataset as 'annual_mm'")
    
    # 4. Monthly Runoff Coefficients (each month's proportion of annual)
    print("Computing Monthly Runoff Coefficients...")
    for month in months:
        mm_col = f'{month}_mm'
        annual_mm_col = 'annual_mm'
        
        # Calculate coefficient: monthly_mm / annual_mm
        df_metrics[f'{month}_coefficient'] = df_metrics[mm_col] / df_metrics[annual_mm_col]
        # Replace inf and nan with 0
        df_metrics[f'{month}_coefficient'] = df_metrics[f'{month}_coefficient'].replace([np.inf, -np.inf], 0)
        df_metrics[f'{month}_coefficient'] = df_metrics[f'{month}_coefficient'].fillna(0)
    
    # 5. Flow Concentration Index (annual runoff / mean monthly runoff)
    print("Computing Flow Concentration Index...")
    df_metrics['mean_monthly_mm'] = df_metrics[mm_cols].mean(axis=1)
    df_metrics['flow_concentration_index'] = df_metrics['annual_mm'] / (df_metrics['mean_monthly_mm'] * 12)
    
    return df_metrics

# Compute metrics
df = compute_derived_metrics(df)

# Remove records with zero or invalid annual flow
df = df[df['annual_mm'] > 0]
df = df[df['flow_variability_index'] > 0]
df = df[df['flow_variability_index'] < 1000]  # Remove extreme outliers

print(f"Records after cleaning: {len(df)}\n")

# ====================================================================
# 2. ANNUAL TREND ANALYSIS
# ====================================================================

def plot_annual_trend(df):
    """Plot annual trends across all stations"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Group by year
    yearly_avg = df.groupby('year').agg({
        'avg_annual_flow_m3s': 'mean',
        'annual_mm': 'mean',
        'flow_variability_index': 'mean',
        'baseflow_index': 'mean'
    }).reset_index()
    
    # Plot 1: Average Annual Flow
    axes[0, 0].plot(yearly_avg['year'], yearly_avg['avg_annual_flow_m3s'], 
                    marker='o', linewidth=2, markersize=8, color='#2E86AB')
    axes[0, 0].fill_between(yearly_avg['year'], yearly_avg['avg_annual_flow_m3s'], 
                            alpha=0.3, color='#2E86AB')
    axes[0, 0].set_title('Annual Trend: Average Flow', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Year')
    axes[0, 0].set_ylabel('Average Flow (m³/s)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Annual Runoff Depth
    axes[0, 1].plot(yearly_avg['year'], yearly_avg['annual_mm'], 
                   marker='o', linewidth=2, markersize=8, color='#A23B72')
    axes[0, 1].fill_between(yearly_avg['year'], yearly_avg['annual_mm'], 
                            alpha=0.3, color='#A23B72')
    axes[0, 1].set_title('Annual Trend: Runoff Depth', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Year')
    axes[0, 1].set_ylabel('Average Annual Runoff (mm)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Flow Variability Index Trend
    axes[1, 0].plot(yearly_avg['year'], yearly_avg['flow_variability_index'], 
                   marker='s', linewidth=2, markersize=8, color='#F18F01')
    axes[1, 0].set_title('Annual Trend: Flow Variability Index', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Year')
    axes[1, 0].set_ylabel('Flow Variability Index')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Baseflow Index Trend
    axes[1, 1].plot(yearly_avg['year'], yearly_avg['baseflow_index'], 
                   marker='^', linewidth=2, markersize=8, color='#06A77D')
    axes[1, 1].set_title('Annual Trend: Baseflow Index', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Year')
    axes[1, 1].set_ylabel('Baseflow Index')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('charts/derived_annual_trends.png', dpi=300, bbox_inches='tight')
    print("Saved: charts/derived_annual_trends.png")
    plt.close()

# ====================================================================
# 3. FLOW SEASONALITY (Hydrograph)
# ====================================================================

def plot_seasonality(df):
    """Plot seasonal flow patterns"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 
              'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
    
    # Calculate average monthly flows
    month_avg_cols = ['oct_avg', 'nov_avg', 'dec_avg', 'jan_avg', 'feb_avg', 'mar_avg',
                       'apr_avg', 'may_avg', 'jun_avg', 'jul_avg', 'aug_avg', 'sep_avg']
    
    monthly_data = df[month_avg_cols].mean()
    
    # Plot 1: Average Monthly Flow (Hydrograph)
    axes[0, 0].bar(months, monthly_data.values, color='#4ECDC4', alpha=0.7, edgecolor='black')
    axes[0, 0].set_title('Hydrograph: Average Monthly Flow', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Month')
    axes[0, 0].set_ylabel('Average Flow (m³/s)')
    axes[0, 0].set_xticklabels(months, rotation=45)
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Seasonal Runoff Coefficients
    month_coef_cols = [col for col in df.columns if col.endswith('_coefficient')]
    coef_values = df[month_coef_cols].mean().values
    # Sort by month order
    coef_sorted = [coef_values[i] for i in range(len(months))]
    
    axes[0, 1].bar(months, coef_sorted, color='#95E1D3', alpha=0.7, edgecolor='black')
    axes[0, 1].axhline(y=1/12, color='red', linestyle='--', linewidth=2, 
                       label='Uniform Distribution (1/12)')
    axes[0, 1].set_title('Monthly Runoff Coefficients', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Month')
    axes[0, 1].set_ylabel('Coefficient (Proportion of Annual)')
    axes[0, 1].set_xticklabels(months, rotation=45)
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Boxplot of monthly flows
    monthly_long = []
    for idx, col in enumerate(month_avg_cols):
        monthly_long.extend([[idx, val] for val in df[col].dropna().tolist()])
    
    monthly_df = pd.DataFrame(monthly_long, columns=['Month', 'Flow'])
    monthly_df['Month'] = monthly_df['Month'].map(lambda x: months[int(x)])
    
    axes[1, 0].boxplot([df[col].dropna().tolist() for col in month_avg_cols], 
                       labels=months)
    axes[1, 0].set_title('Flow Distribution by Month', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Month')
    axes[1, 0].set_ylabel('Flow (m³/s)')
    axes[1, 0].tick_params(axis='x', rotation=45)
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # Plot 4: Seasonal Variability
    month_max_cols = ['oct_max', 'nov_max', 'dec_max', 'jan_max', 'feb_max', 'mar_max',
                      'apr_max', 'may_max', 'jun_max', 'jul_max', 'aug_max', 'sep_max']
    max_values = df[month_max_cols].mean().values
    
    month_min_cols = ['oct_min', 'nov_min', 'dec_min', 'jan_min', 'feb_min', 'mar_min',
                      'apr_min', 'may_min', 'jun_min', 'jul_min', 'aug_min', 'sep_min']
    min_values = df[month_min_cols].mean().values
    
    axes[1, 1].plot(months, max_values, marker='o', label='Max Flow', linewidth=2, color='#C73E1D')
    axes[1, 1].plot(months, monthly_data.values, marker='s', label='Mean Flow', linewidth=2, color='#2E86AB')
    axes[1, 1].plot(months, min_values, marker='^', label='Min Flow', linewidth=2, color='#06A77D')
    axes[1, 1].fill_between(months, min_values, max_values, alpha=0.2)
    axes[1, 1].set_title('Seasonal Flow Variability', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Month')
    axes[1, 1].set_ylabel('Flow (m³/s)')
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('charts/derived_seasonality.png', dpi=300, bbox_inches='tight')
    print("Saved: charts/derived_seasonality.png")
    plt.close()

# ====================================================================
# 4. FLOW DISTRIBUTION ANALYSIS
# ====================================================================

def plot_flow_distribution(df):
    """Plot flow distribution and variability"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: Distribution of Flow Variability Index
    axes[0, 0].hist(df['flow_variability_index'].dropna(), bins=50, 
                   color='#2E86AB', alpha=0.7, edgecolor='black')
    axes[0, 0].set_title('Distribution of Flow Variability Index', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Flow Variability Index')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].axvline(df['flow_variability_index'].median(), 
                       color='red', linestyle='--', linewidth=2, label='Median')
    axes[0, 0].axvline(df['flow_variability_index'].mean(), 
                       color='orange', linestyle='--', linewidth=2, label='Mean')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Distribution of Baseflow Index
    axes[0, 1].hist(df['baseflow_index'].dropna(), bins=50, 
                   color='#A23B72', alpha=0.7, edgecolor='black')
    axes[0, 1].set_title('Distribution of Baseflow Index', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Baseflow Index')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].axvline(df['baseflow_index'].median(), 
                      color='red', linestyle='--', linewidth=2, label='Median')
    axes[0, 1].axvline(df['baseflow_index'].mean(), 
                      color='orange', linestyle='--', linewidth=2, label='Mean')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Scatter plot - Baseflow Index vs Flow Variability
    axes[1, 0].scatter(df['baseflow_index'], df['flow_variability_index'], 
                      alpha=0.6, s=50, color='#F18F01', edgecolors='black', linewidth=0.5)
    axes[1, 0].set_title('Baseflow vs Variability Index', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Baseflow Index')
    axes[1, 0].set_ylabel('Flow Variability Index')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Boxplot by Basin
    if 'region' in df.columns:
        basin_order = df.groupby('region').size().sort_values(ascending=False).index[:10]
        df_filtered = df[df['region'].isin(basin_order)]
        
        box_data = [df_filtered[df_filtered['region'] == basin]['annual_mm'].dropna().tolist() 
                    for basin in basin_order]
        
        axes[1, 1].boxplot(box_data, labels=[basin[:20] + '...' if len(basin) > 20 else basin 
                                               for basin in basin_order])
        axes[1, 1].set_title('Annual Runoff by Basin', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('Basin')
        axes[1, 1].set_ylabel('Annual Runoff (mm)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('charts/derived_flow_distribution.png', dpi=300, bbox_inches='tight')
    print("Saved: charts/derived_flow_distribution.png")
    plt.close()

# ====================================================================
# 5. EXTREME EVENTS ANALYSIS
# ====================================================================

def plot_extreme_events(df):
    """Analyze and plot extreme flow events"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Group by year
    yearly_stats = df.groupby('year').agg({
        'max_flow': ['mean', 'max'],
        'min_flow': ['mean', 'min'],
        'annual_mm': 'mean'
    }).reset_index()
    
    yearly_stats.columns = ['year', 'avg_max', 'overall_max', 'avg_min', 'overall_min', 'avg_annual']
    
    # Plot 1: Annual Maximum Flows
    axes[0, 0].plot(yearly_stats['year'], yearly_stats['overall_max'], 
                   marker='o', linewidth=2, label='Absolute Max', color='#C73E1D')
    axes[0, 0].plot(yearly_stats['year'], yearly_stats['avg_max'], 
                   marker='s', linewidth=2, label='Average Max', color='#F18F01')
    axes[0, 0].fill_between(yearly_stats['year'], yearly_stats['overall_max'], 
                            alpha=0.2, color='#C73E1D')
    axes[0, 0].set_title('Annual Maximum Flows', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Year')
    axes[0, 0].set_ylabel('Flow (m³/s)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Annual Minimum Flows
    axes[0, 1].plot(yearly_stats['year'], yearly_stats['overall_min'], 
                   marker='o', linewidth=2, label='Absolute Min', color='#2E86AB')
    axes[0, 1].plot(yearly_stats['year'], yearly_stats['avg_min'], 
                   marker='s', linewidth=2, label='Average Min', color='#06A77D')
    axes[0, 1].fill_between(yearly_stats['year'], yearly_stats['overall_min'], 
                            alpha=0.2, color='#2E86AB')
    axes[0, 1].set_title('Annual Minimum Flows', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Year')
    axes[0, 1].set_ylabel('Flow (m³/s)')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Peak-to-Base Ratio over time
    yearly_stats['peak_base_ratio'] = yearly_stats['avg_max'] / yearly_stats['avg_min']
    axes[1, 0].plot(yearly_stats['year'], yearly_stats['peak_base_ratio'], 
                   marker='o', linewidth=2, markersize=8, color='#A23B72')
    axes[1, 0].fill_between(yearly_stats['year'], yearly_stats['peak_base_ratio'], 
                            alpha=0.3, color='#A23B72')
    axes[1, 0].set_title('Peak-to-Base Flow Ratio over Time', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Year')
    axes[1, 0].set_ylabel('Ratio')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Scatter - Max vs Mean Flow
    axes[1, 1].scatter(df['mean_flow'], df['max_flow'], alpha=0.6, s=50, 
                      color='#4ECDC4', edgecolors='black', linewidth=0.5)
    axes[1, 1].set_title('Maximum vs Mean Flow', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Mean Flow (m³/s)')
    axes[1, 1].set_ylabel('Maximum Flow (m³/s)')
    axes[1, 1].grid(True, alpha=0.3)
    
    # Add diagonal reference line
    max_val = max(df['mean_flow'].max(), df['max_flow'].max())
    axes[1, 1].plot([0, max_val], [0, max_val], 'r--', alpha=0.5, label='1:1 line')
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.savefig('charts/derived_extreme_events.png', dpi=300, bbox_inches='tight')
    print("Saved: charts/derived_extreme_events.png")
    plt.close()

# ====================================================================
# 6. STATION COMPARISON
# ====================================================================

def plot_station_comparison(df):
    """Compare different stations"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Get top stations by average annual flow
    station_stats = df.groupby('station_code').agg({
        'avg_annual_flow_m3s': 'mean',
        'annual_mm': 'mean',
        'catchment_area_km2': 'first'
    }).reset_index()
    
    top_stations = station_stats.nlargest(10, 'avg_annual_flow_m3s')
    
    # Plot 1: Top 10 Stations by Flow
    axes[0, 0].barh(top_stations['station_code'], top_stations['avg_annual_flow_m3s'], 
                    color='#2E86AB', alpha=0.8, edgecolor='black')
    axes[0, 0].set_title('Top 10 Stations by Average Annual Flow', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Average Annual Flow (m³/s)')
    axes[0, 0].set_ylabel('Station Code')
    axes[0, 0].grid(True, alpha=0.3, axis='x')
    
    # Plot 2: Hydrological Yield vs Catchment Area
    scatter = axes[0, 1].scatter(df['catchment_area_km2'], df['annual_mm'], 
                               c=df['flow_variability_index'], 
                               s=100, alpha=0.6, cmap='viridis', 
                               edgecolors='black', linewidth=0.5)
    axes[0, 1].set_title('Hydrological Yield vs Catchment Area', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Catchment Area (km²)')
    axes[0, 1].set_ylabel('Annual Runoff (mm)')
    axes[0, 1].set_xscale('log')
    plt.colorbar(scatter, ax=axes[0, 1], label='Flow Variability Index')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Station averages
    station_avg = df.groupby('station_code').agg({
        'baseflow_index': 'mean',
        'flow_variability_index': 'mean'
    }).reset_index()
    
    axes[1, 0].scatter(station_avg['baseflow_index'], station_avg['flow_variability_index'], 
                      alpha=0.7, s=100, color='#F18F01', edgecolors='black', linewidth=0.5)
    axes[1, 0].set_title('Station Characterization', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Baseflow Index (avg)')
    axes[1, 0].set_ylabel('Flow Variability Index (avg)')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Add quadrant labels
    x_median = station_avg['baseflow_index'].median()
    y_median = station_avg['flow_variability_index'].median()
    
    axes[1, 0].axvline(x_median, color='red', linestyle='--', alpha=0.5)
    axes[1, 0].axhline(y_median, color='red', linestyle='--', alpha=0.5)
    
    # Plot 4: Boxplot of annual runoff by top stations
    top_10_codes = top_stations['station_code'].tolist()
    df_top = df[df['station_code'].isin(top_10_codes)]
    
    box_data = [df_top[df_top['station_code'] == code]['annual_mm'].dropna().tolist() 
                for code in top_10_codes]
    
    axes[1, 1].boxplot(box_data, labels=top_10_codes)
    axes[1, 1].set_title('Annual Runoff Distribution: Top 10 Stations', 
                         fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Station Code')
    axes[1, 1].set_ylabel('Annual Runoff (mm)')
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('charts/derived_station_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved: charts/derived_station_comparison.png")
    plt.close()

# ====================================================================
# 7. SAVE ENHANCED DATASET
# ====================================================================

def save_enhanced_dataset(df):
    """Save the dataset with computed metrics"""
    output_file = 'dsi_final_with_derived_metrics.csv'
    df.to_csv(output_file, index=False)
    print(f"\nSaved enhanced dataset: {output_file}")
    print(f"Total columns: {len(df.columns)}")
    
    # Print summary statistics
    print("\n=== Summary Statistics ===")
    print("\nFlow Variability Index:")
    print(df['flow_variability_index'].describe())
    
    print("\nBaseflow Index:")
    print(df['baseflow_index'].describe())
    
    print("\nAnnual Runoff (mm):")
    print(df['annual_mm'].describe())
    
    print("\nFlow Concentration Index:")
    print(df['flow_concentration_index'].describe())

# ====================================================================
# MAIN EXECUTION
# ====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("HYDROLOGICAL ANALYSIS AND DERIVED METRICS")
    print("=" * 60 + "\n")
    
    # Create charts directory if it doesn't exist
    Path('charts').mkdir(exist_ok=True)
    
    # Generate all visualizations
    print("\n[1/5] Generating annual trend analysis...")
    plot_annual_trend(df)
    
    print("\n[2/5] Generating seasonality analysis...")
    plot_seasonality(df)
    
    print("\n[3/5] Generating flow distribution analysis...")
    plot_flow_distribution(df)
    
    print("\n[4/5] Generating extreme events analysis...")
    plot_extreme_events(df)
    
    print("\n[5/5] Generating station comparison...")
    plot_station_comparison(df)
    
    print("\nSaving enhanced dataset...")
    save_enhanced_dataset(df)
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - dsi_final_with_derived_metrics.csv")
    print("  - charts/derived_annual_trends.png")
    print("  - charts/derived_seasonality.png")
    print("  - charts/derived_flow_distribution.png")
    print("  - charts/derived_extreme_events.png")
    print("  - charts/derived_station_comparison.png")

