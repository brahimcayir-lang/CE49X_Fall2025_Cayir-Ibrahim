import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from scipy.stats import linregress

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

# Create output directory
os.makedirs('station_charts', exist_ok=True)

# Load dataset
print("Loading data...")
df = pd.read_csv("dsi_final_excluding_extremes.csv")

# Clean data: filter invalid rainfall
df_clean = df[df["annual_mm"] >= 1].copy()

# Get unique stations
stations = df_clean['station_code'].unique()
print(f"Found {len(stations)} unique stations")
print("="*60)

for station_code in stations:
    print(f"\nProcessing station: {station_code}")
    
    # Filter data for this station
    station_data = df_clean[df_clean['station_code'] == station_code].copy()
    station_data = station_data.sort_values('year')
    
    print(f"  Data points: {len(station_data)}")
    print(f"  Year range: {station_data['year'].min()} - {station_data['year'].max()}")
    
    # Create station folder
    station_folder = os.path.join('station_charts', station_code)
    os.makedirs(station_folder, exist_ok=True)
    
    # ========================================================================
    # Chart 1: Annual Flow Trend
    # ========================================================================
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(station_data['year'], station_data['avg_annual_flow_m3s'], 
           marker='o', linewidth=2, markersize=6, color='steelblue', alpha=0.8, label='Annual Flow')
    
    # Add 5-year rolling mean if enough data
    if len(station_data) >= 5:
        station_data['rolling_mean'] = station_data['avg_annual_flow_m3s'].rolling(window=5, center=True).mean()
        ax.plot(station_data['year'], station_data['rolling_mean'], 
               linestyle='--', linewidth=2.5, color='red', alpha=0.7, label='5-Year Rolling Mean')
    
    # Fit linear trend
    if len(station_data) >= 3:
        x = station_data['year'].values
        y = station_data['avg_annual_flow_m3s'].values
        slope, intercept, r, p, se = linregress(x, y)
        y_trend = slope * x + intercept
        ax.plot(x, y_trend, 'g--', linewidth=2, alpha=0.6, label=f'Linear Trend (R²={r**2:.3f})')
    
    ax.set_xlabel("Year", fontsize=12, fontweight='bold')
    ax.set_ylabel("Average Annual Flow (m³/s)", fontsize=12, fontweight='bold')
    ax.set_title(f"Annual Average Flow Trend: {station_code}", fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(station_folder, 'trend.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # ========================================================================
    # Chart 2: Flow Anomalies (Z-Score)
    # ========================================================================
    fig, ax = plt.subplots(figsize=(14, 6))
    
    mean_flow = station_data['avg_annual_flow_m3s'].mean()
    std_flow = station_data['avg_annual_flow_m3s'].std()
    station_data['z_score'] = (station_data['avg_annual_flow_m3s'] - mean_flow) / std_flow
    
    colors = ['red' if z < 0 else 'blue' if z > 0 else 'gray' for z in station_data['z_score']]
    
    ax.bar(station_data['year'], station_data['z_score'], color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
    ax.axhline(y=1, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='1σ')
    ax.axhline(y=-1, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.axhline(y=2, color='gray', linestyle='--', linewidth=1, alpha=0.3)
    ax.axhline(y=-2, color='gray', linestyle='--', linewidth=1, alpha=0.3)
    
    ax.set_xlabel("Year", fontsize=12, fontweight='bold')
    ax.set_ylabel("Z-Score (Standard Deviations)", fontsize=12, fontweight='bold')
    ax.set_title(f"Flow Anomalies: {station_code}", fontsize=13, fontweight='bold')
    ax.legend(['Mean', '±1σ'], loc='best', fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(station_folder, 'anomaly.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # ========================================================================
    # Chart 3: Rainfall-Runoff Relationship
    # ========================================================================
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Filter to reasonable range
    mask = (station_data['annual_mm'] <= 400) & (station_data['avg_annual_flow_m3s'] <= 20)
    filtered_data = station_data[mask]
    
    if len(filtered_data) >= 3:
        x = filtered_data['annual_mm']
        y = filtered_data['avg_annual_flow_m3s']
        
        # Fit regression
        slope, intercept, r, p, se = linregress(x, y)
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = slope * x_line + intercept
        
        # Plot data points
        ax.scatter(x, y, color='skyblue', alpha=0.6, s=80, edgecolors='white', linewidth=0.5)
        
        # Plot regression line
        ax.plot(x_line, y_line, 'r--', linewidth=2.5, alpha=0.8, label=f'R² = {r**2:.3f}')
        
        # Highlight recent years if applicable
        if '2020' in station_data['year'].astype(str).values:
            recent_data = filtered_data[filtered_data['year'] == 2020]
            if len(recent_data) > 0:
                ax.scatter(recent_data['annual_mm'], recent_data['avg_annual_flow_m3s'],
                          color='red', s=200, edgecolors='black', linewidth=2, 
                          label='2020', zorder=10)
    else:
        ax.scatter(station_data['annual_mm'], station_data['avg_annual_flow_m3s'],
                  color='skyblue', alpha=0.6, s=80, edgecolors='white', linewidth=0.5)
    
    ax.set_xlabel("Annual Precipitation (mm)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Average Annual Flow (m³/s)", fontsize=12, fontweight='bold')
    ax.set_title(f"Rainfall-Runoff: {station_code}", fontsize=13, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(station_folder, 'rainfall_runoff.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # ========================================================================
    # Chart 4: Runoff Efficiency (Ratio)
    # ========================================================================
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Calculate runoff efficiency ratio
    if 'annual_lt_sn_km2' in station_data.columns:
        station_data['runoff_ratio'] = station_data['annual_lt_sn_km2'] / station_data['annual_mm']
        
        ax.plot(station_data['year'], station_data['runoff_ratio'], 
               marker='o', linewidth=2, markersize=6, color='green', alpha=0.8)
        
        # Add mean line
        mean_ratio = station_data['runoff_ratio'].mean()
        ax.axhline(y=mean_ratio, color='red', linestyle='--', linewidth=2, 
                  label=f'Mean: {mean_ratio:.3f}')
        
        ax.set_xlabel("Year", fontsize=12, fontweight='bold')
        ax.set_ylabel("Runoff Efficiency (Ratio)", fontsize=12, fontweight='bold')
        ax.set_title(f"Runoff Efficiency Over Time: {station_code}", fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(station_folder, 'ratio_trend.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    # ========================================================================
    # Chart 5: Monthly Hydrograph (if available)
    # ========================================================================
    monthly_cols = ['oct_avg', 'nov_avg', 'dec_avg', 'jan_avg', 'feb_avg', 'mar_avg',
                    'apr_avg', 'may_avg', 'jun_avg', 'jul_avg', 'aug_avg', 'sep_avg']
    
    if all(col in station_data.columns for col in monthly_cols):
        fig, ax = plt.subplots(figsize=(14, 6))
        
        months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
        
        # Calculate long-term monthly average
        monthly_means = [station_data[col].mean() for col in monthly_cols]
        
        # Plot long-term average
        ax.plot(range(12), monthly_means, marker='o', linewidth=2.5, 
               color='steelblue', label='Long-term Average', markersize=8)
        
        # Plot each year with thin lines
        for _, row in station_data.iterrows():
            monthly_values = [row[col] for col in monthly_cols]
            ax.plot(range(12), monthly_values, color='gray', alpha=0.2, linewidth=0.5)
        
        ax.set_xticks(range(12))
        ax.set_xticklabels(months, rotation=45, ha='right')
        ax.set_ylabel("Average Flow (m³/s)", fontsize=12, fontweight='bold')
        ax.set_title(f"Monthly Flow Regime: {station_code}", fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(station_folder, 'hydrograph.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    # ========================================================================
    # Chart 6: Correlation Heatmap (optional)
    # ========================================================================
    numeric_cols = ['catchment_area_km2', 'annual_mm', 'avg_annual_flow_m3s', 
                   'annual_lt_sn_km2']
    
    # Filter to columns that exist
    numeric_cols = [col for col in numeric_cols if col in station_data.columns]
    
    if len(numeric_cols) >= 2:
        corr_matrix = station_data[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
        ax.set_title(f"Intra-Station Correlation: {station_code}", 
                    fontsize=13, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(station_folder, 'correlation.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"  ✓ Generated charts for {station_code}")

print("\n" + "="*60)
print("All station-level analyses complete!")
print("="*60)
print(f"Generated charts for {len(stations)} stations in station_charts/")

