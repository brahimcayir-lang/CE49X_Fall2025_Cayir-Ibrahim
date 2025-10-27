"""
Hydrological Analysis for Kuzey I-II Regulator and Hydroelectric Power Plant Project
Ordu, Türkiye - Streamflow Data Analysis (2000-2020)

This script analyzes 20 years of streamflow data to provide insights for hydropower design and operation.
Each visualization is saved as a separate PNG file with numerical values displayed.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import warnings
import sys
import os

# Set encoding for Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('default')
sns.set_style("whitegrid")
sns.set_palette("husl")

def load_and_prepare_data():
    """Load and prepare the hydrological dataset"""
    print("Loading hydrological data...")
    
    # Load the dataset
    df = pd.read_csv('dsi_2000_2020_final.csv', encoding='utf-8-sig')
    
    # Filter for the main station (D14A162 - Yeşilırmak Kozlu)
    main_station = df[df['station_code'] == 'D14A162'].copy()
    
    if len(main_station) == 0:
        print("No data found for D14A162. Using all stations for analysis...")
        main_station = df.copy()
    else:
        print(f"Found {len(main_station)} records for D14A162 station")
    
    # Extract year from filename since year column is empty
    main_station['year'] = main_station['file'].str.extract(r'dsi_(\d{4})\.pdf')[0].astype(int)
    main_station = main_station.dropna(subset=['year'])
    
    # Convert flow data to numeric
    flow_columns = ['annual_total_m3_million', 'annual_lps_km2', 'annual_mm']
    for col in flow_columns:
        main_station[col] = pd.to_numeric(main_station[col], errors='coerce')
    
    # Convert monthly data to numeric
    monthly_cols = ['Ekim', 'Kasım', 'Aralık', 'Ocak', 'Şubat', 'Mart', 
                   'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül']
    for col in monthly_cols:
        main_station[col] = pd.to_numeric(main_station[col], errors='coerce')
    
    print(f"Dataset loaded: {len(main_station)} years of data")
    if len(main_station) > 0:
        station_name = main_station['station_name'].iloc[0]
        print(f"Station: {station_name}")
        print(f"Catchment Area: {main_station['catchment_area_km2'].iloc[0]:.2f} km²")
    
    return main_station

def create_annual_trend_analysis(df):
    """Create long-term annual flow trend analysis"""
    print("\n1. Creating Annual Flow Trend Analysis...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Annual Total Flow Volume
    df_sorted = df.sort_values('year')
    
    # Filter out NaN values for plotting
    valid_data = df_sorted.dropna(subset=['annual_total_m3_million'])
    
    if len(valid_data) > 0:
        ax1.plot(valid_data['year'], valid_data['annual_total_m3_million'], 
                 'o-', alpha=0.7, linewidth=2, markersize=8, label='Annual Volume', color='blue')
        
        # Add numerical values on points
        for i, (year, volume) in enumerate(zip(valid_data['year'], valid_data['annual_total_m3_million'])):
            ax1.annotate(f'{volume:.1f}', (year, volume), 
                        textcoords="offset points", xytext=(0,15), ha='center', fontsize=9, fontweight='bold')
        
        # Rolling mean (5-year window) if enough data
        if len(valid_data) >= 5:
            rolling_mean = valid_data['annual_total_m3_million'].rolling(window=min(5, len(valid_data)), center=True).mean()
            ax1.plot(valid_data['year'], rolling_mean, 
                     'r-', linewidth=3, label=f'{min(5, len(valid_data))}-Year Rolling Mean')
    
    ax1.set_title('Long-term Annual Flow Volume Trend\nKuzey I-II Hydroelectric Project (2000-2020)', 
                  fontsize=16, fontweight='bold')
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Annual Flow Volume (Million m³)', fontsize=12)
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # Annual Specific Discharge
    valid_spec_data = df_sorted.dropna(subset=['annual_lps_km2'])
    
    if len(valid_spec_data) > 0:
        ax2.plot(valid_spec_data['year'], valid_spec_data['annual_lps_km2'], 
                 'o-', alpha=0.7, linewidth=2, markersize=8, label='Specific Discharge', color='green')
        
        # Add numerical values on points
        for i, (year, spec_discharge) in enumerate(zip(valid_spec_data['year'], valid_spec_data['annual_lps_km2'])):
            ax2.annotate(f'{spec_discharge:.2f}', (year, spec_discharge), 
                        textcoords="offset points", xytext=(0,15), ha='center', fontsize=9, fontweight='bold')
        
        if len(valid_spec_data) >= 5:
            rolling_mean_spec = valid_spec_data['annual_lps_km2'].rolling(window=min(5, len(valid_spec_data)), center=True).mean()
            ax2.plot(valid_spec_data['year'], rolling_mean_spec, 
                     'r-', linewidth=3, label=f'{min(5, len(valid_spec_data))}-Year Rolling Mean')
    
    ax2.set_title('Long-term Specific Discharge Trend\nKuzey I-II Hydroelectric Project (2000-2020)', 
                  fontsize=16, fontweight='bold')
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('Specific Discharge (l/s/km²)', fontsize=12)
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('1_annual_trend_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Statistical analysis
    if len(valid_data) > 1:
        slope_vol, intercept_vol, r_value_vol, p_value_vol, std_err_vol = stats.linregress(valid_data['year'], valid_data['annual_total_m3_million'])
        print(f"Volume Trend: {slope_vol:.2f} million m³/year (R² = {r_value_vol**2:.3f}, p = {p_value_vol:.3f})")
        
        if p_value_vol < 0.05:
            trend_vol = "significant" if slope_vol > 0 else "significant decreasing"
        else:
            trend_vol = "no significant"
        print(f"Volume shows {trend_vol} trend")
    
    if len(valid_spec_data) > 1:
        slope_spec, intercept_spec, r_value_spec, p_value_spec, std_err_spec = stats.linregress(valid_spec_data['year'], valid_spec_data['annual_lps_km2'])
        print(f"Specific Discharge Trend: {slope_spec:.3f} l/s/km²/year (R² = {r_value_spec**2:.3f}, p = {p_value_spec:.3f})")

def create_monthly_regime_analysis(df):
    """Create monthly flow regime analysis"""
    print("\n2. Creating Monthly Flow Regime Analysis...")
    
    # Prepare monthly data
    months = ['Ekim', 'Kasım', 'Aralık', 'Ocak', 'Şubat', 'Mart', 
              'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül']
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Calculate monthly statistics
    monthly_means = []
    monthly_std = []
    
    for month in months:
        month_data = df[month].dropna()
        if len(month_data) > 0:
            monthly_means.append(month_data.mean())
            monthly_std.append(month_data.std())
        else:
            monthly_means.append(0)
            monthly_std.append(0)
    
    # Mean monthly hydrograph
    ax1.plot(range(12), monthly_means, 'o-', linewidth=3, markersize=10, color='darkblue')
    ax1.fill_between(range(12), 
                     np.array(monthly_means) - np.array(monthly_std), 
                     np.array(monthly_means) + np.array(monthly_std), 
                     alpha=0.3, color='lightblue', label='±1 Standard Deviation')
    
    # Add numerical values on points
    for i, (mean_val, std_val) in enumerate(zip(monthly_means, monthly_std)):
        ax1.annotate(f'{mean_val:.1f}', (i, mean_val), 
                    textcoords="offset points", xytext=(0,15), ha='center', fontsize=9, fontweight='bold')
    
    ax1.set_title('Mean Monthly Flow Regime\nKuzey I-II Hydroelectric Project', 
                  fontsize=16, fontweight='bold')
    ax1.set_xlabel('Month', fontsize=12)
    ax1.set_ylabel('Mean Discharge (m³/s)', fontsize=12)
    ax1.set_xticks(range(12))
    ax1.set_xticklabels(months, rotation=45)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Boxplot for monthly variability
    monthly_data_for_box = []
    for month in months:
        month_data = df[month].dropna().tolist()
        monthly_data_for_box.append(month_data)
    
    bp = ax2.boxplot(monthly_data_for_box, labels=months, patch_artist=True)
    
    # Color the boxes
    colors = plt.cm.Set3(np.linspace(0, 1, 12))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax2.set_title('Monthly Flow Variability (Boxplots)\nKuzey I-II Hydroelectric Project', 
                  fontsize=16, fontweight='bold')
    ax2.set_xlabel('Month', fontsize=12)
    ax2.set_ylabel('Discharge (m³/s)', fontsize=12)
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('2_monthly_regime_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Seasonal analysis
    wet_season = ['Mart', 'Nisan', 'Mayıs', 'Haziran']  # Spring months
    dry_season = ['Temmuz', 'Ağustos', 'Eylül', 'Ekim']  # Summer/early autumn
    
    wet_data = []
    dry_data = []
    
    for month in wet_season:
        wet_data.extend(df[month].dropna().tolist())
    for month in dry_season:
        dry_data.extend(df[month].dropna().tolist())
    
    if wet_data and dry_data:
        wet_avg = np.mean(wet_data)
        dry_avg = np.mean(dry_data)
        
        print(f"Wet Season Average (Mar-Jun): {wet_avg:.2f} m³/s")
        print(f"Dry Season Average (Jul-Oct): {dry_avg:.2f} m³/s")
        print(f"Seasonal Ratio (Wet/Dry): {wet_avg/dry_avg:.2f}")

def create_flow_duration_curve(df):
    """Create Flow Duration Curve (FDC)"""
    print("\n3. Creating Flow Duration Curve...")
    
    # Combine all monthly data
    all_flows = []
    months = ['Ekim', 'Kasım', 'Aralık', 'Ocak', 'Şubat', 'Mart', 
              'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül']
    
    for month in months:
        month_data = df[month].dropna().tolist()
        all_flows.extend(month_data)
    
    if not all_flows:
        print("No flow data available for FDC")
        return
    
    # Sort flows in descending order
    sorted_flows = np.sort(all_flows)[::-1]
    
    # Calculate exceedance probabilities
    n = len(sorted_flows)
    exceedance_prob = np.arange(1, n + 1) / (n + 1) * 100
    
    plt.figure(figsize=(12, 8))
    plt.semilogy(exceedance_prob, sorted_flows, linewidth=2, color='darkred')
    
    # Add key percentiles with numerical values
    percentiles = [10, 25, 50, 75, 90, 95]
    for p in percentiles:
        flow_value = np.percentile(sorted_flows, 100-p)
        plt.axhline(y=flow_value, color='gray', linestyle='--', alpha=0.7)
        plt.text(100-p, flow_value, f'P{p}: {flow_value:.1f}', 
                verticalalignment='bottom', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    plt.title('Flow Duration Curve\nKuzey I-II Hydroelectric Project (2000-2020)', 
              fontsize=16, fontweight='bold')
    plt.xlabel('Exceedance Probability (%)', fontsize=12)
    plt.ylabel('Discharge (m³/s)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 100)
    
    plt.tight_layout()
    plt.savefig('3_flow_duration_curve.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Key statistics for hydropower design
    q10 = np.percentile(sorted_flows, 90)  # 10% exceedance
    q50 = np.percentile(sorted_flows, 50)  # 50% exceedance
    q90 = np.percentile(sorted_flows, 10)  # 90% exceedance
    
    print(f"Q10 (10% exceedance): {q10:.2f} m³/s - High flow conditions")
    print(f"Q50 (50% exceedance): {q50:.2f} m³/s - Median flow")
    print(f"Q90 (90% exceedance): {q90:.2f} m³/s - Low flow conditions")
    print(f"Reliability Factor (Q90/Q50): {q90/q50:.2f}")

def create_correlation_analysis(df):
    """Create correlation analysis between annual volume and specific discharge"""
    print("\n4. Creating Correlation Analysis...")
    
    # Filter valid data
    valid_data = df.dropna(subset=['annual_lps_km2', 'annual_total_m3_million'])
    
    if len(valid_data) < 2:
        print("Insufficient data for correlation analysis")
        return
    
    plt.figure(figsize=(10, 8))
    
    # Scatter plot
    scatter = plt.scatter(valid_data['annual_lps_km2'], valid_data['annual_total_m3_million'], 
               s=120, alpha=0.7, c=valid_data['year'], cmap='viridis', edgecolors='black', linewidth=1)
    
    # Add numerical values on points
    for i, (spec_discharge, volume, year) in enumerate(zip(valid_data['annual_lps_km2'], 
                                                          valid_data['annual_total_m3_million'], 
                                                          valid_data['year'])):
        plt.annotate(f'{volume:.1f}', (spec_discharge, volume), 
                    textcoords="offset points", xytext=(0,15), ha='center', fontsize=8, fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(scatter)
    cbar.set_label('Year', fontsize=12)
    
    # Add trend line
    slope, intercept, r_value, p_value, std_err = stats.linregress(valid_data['annual_lps_km2'], valid_data['annual_total_m3_million'])
    line = slope * valid_data['annual_lps_km2'] + intercept
    plt.plot(valid_data['annual_lps_km2'], line, 'r--', linewidth=2, 
             label=f'Trend (R² = {r_value**2:.3f})')
    
    plt.title('Annual Volume vs Specific Discharge Correlation\nKuzey I-II Hydroelectric Project', 
              fontsize=16, fontweight='bold')
    plt.xlabel('Specific Discharge (l/s/km²)', fontsize=12)
    plt.ylabel('Annual Flow Volume (Million m³)', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('4_correlation_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Correlation Coefficient: {r_value:.3f}")
    print(f"R² Value: {r_value**2:.3f}")
    print(f"P-value: {p_value:.3f}")

def create_extreme_flow_analysis(df):
    """Create extreme flow analysis"""
    print("\n5. Creating Extreme Flow Analysis...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Annual maximum flows
    months = ['Ekim', 'Kasım', 'Aralık', 'Ocak', 'Şubat', 'Mart', 
              'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül']
    
    annual_max = []
    annual_min = []
    years = []
    
    for _, row in df.iterrows():
        year_flows = [row[month] for month in months if pd.notna(row[month])]
        if year_flows:
            annual_max.append(max(year_flows))
            annual_min.append(min(year_flows))
            years.append(row['year'])
    
    if annual_max:
        ax1.plot(years, annual_max, 'o-', linewidth=2, markersize=8, color='red', label='Annual Maximum')
        ax1.fill_between(years, annual_max, alpha=0.3, color='red')
        
        # Add numerical values on points
        for year, max_flow in zip(years, annual_max):
            ax1.annotate(f'{max_flow:.1f}', (year, max_flow), 
                        textcoords="offset points", xytext=(0,15), ha='center', fontsize=9, fontweight='bold')
    
    ax1.set_title('Annual Maximum Flow Analysis\nKuzey I-II Hydroelectric Project', 
                 fontsize=16, fontweight='bold')
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Maximum Monthly Discharge (m³/s)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Annual minimum flows
    if annual_min:
        ax2.plot(years, annual_min, 'o-', linewidth=2, markersize=8, color='blue', label='Annual Minimum')
        ax2.fill_between(years, annual_min, alpha=0.3, color='blue')
        
        # Add numerical values on points
        for year, min_flow in zip(years, annual_min):
            ax2.annotate(f'{min_flow:.2f}', (year, min_flow), 
                        textcoords="offset points", xytext=(0,15), ha='center', fontsize=9, fontweight='bold')
    
    ax2.set_title('Annual Minimum Flow Analysis\nKuzey I-II Hydroelectric Project', 
                  fontsize=16, fontweight='bold')
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('Minimum Monthly Discharge (m³/s)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('5_extreme_flow_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Extreme flow statistics
    if annual_max and annual_min:
        max_flow = max(annual_max)
        min_flow = min(annual_min)
        avg_max = np.mean(annual_max)
        avg_min = np.mean(annual_min)
        
        print(f"Maximum recorded flow: {max_flow:.2f} m³/s")
        print(f"Minimum recorded flow: {min_flow:.2f} m³/s")
        print(f"Average annual maximum: {avg_max:.2f} m³/s")
        print(f"Average annual minimum: {avg_min:.2f} m³/s")
        print(f"Flow variability ratio (Max/Min): {max_flow/min_flow:.1f}")

def create_summary_statistics_table(df):
    """Create a summary statistics table"""
    print("\n6. Creating Summary Statistics Table...")
    
    months = ['Ekim', 'Kasım', 'Aralık', 'Ocak', 'Şubat', 'Mart', 
              'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül']
    
    # Calculate statistics for each month
    monthly_stats = []
    for month in months:
        month_data = df[month].dropna()
        if len(month_data) > 0:
            stats_dict = {
                'Month': month,
                'Mean (m³/s)': f"{month_data.mean():.2f}",
                'Median (m³/s)': f"{month_data.median():.2f}",
                'Std Dev (m³/s)': f"{month_data.std():.2f}",
                'Min (m³/s)': f"{month_data.min():.2f}",
                'Max (m³/s)': f"{month_data.max():.2f}",
                'Count': len(month_data)
            }
        else:
            stats_dict = {
                'Month': month,
                'Mean (m³/s)': "N/A",
                'Median (m³/s)': "N/A",
                'Std Dev (m³/s)': "N/A",
                'Min (m³/s)': "N/A",
                'Max (m³/s)': "N/A",
                'Count': 0
            }
        monthly_stats.append(stats_dict)
    
    # Create DataFrame and save as CSV
    stats_df = pd.DataFrame(monthly_stats)
    stats_df.to_csv('monthly_statistics_summary.csv', index=False)
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Create table
    table_data = []
    headers = ['Month', 'Mean (m³/s)', 'Median (m³/s)', 'Std Dev (m³/s)', 'Min (m³/s)', 'Max (m³/s)', 'Count']
    
    for stats_dict in monthly_stats:
        table_data.append([stats_dict[header] for header in headers])
    
    table = ax.table(cellText=table_data, colLabels=headers, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    
    # Style the table
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    plt.title('Monthly Flow Statistics Summary\nKuzey I-II Hydroelectric Project', 
              fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('6_summary_statistics_table.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Monthly statistics saved to 'monthly_statistics_summary.csv'")

def generate_hydropower_insights(df):
    """Generate insights for hydropower design and operation"""
    print("\n" + "="*60)
    print("HYDROPOWER DESIGN AND OPERATION INSIGHTS")
    print("="*60)
    
    # Key statistics
    avg_annual_volume = df['annual_total_m3_million'].mean()
    avg_specific_discharge = df['annual_lps_km2'].mean()
    catchment_area = df['catchment_area_km2'].iloc[0]
    
    print(f"\n1. PROJECT CHARACTERISTICS:")
    print(f"   • Catchment Area: {catchment_area:.1f} km²")
    print(f"   • Average Annual Volume: {avg_annual_volume:.1f} million m³")
    print(f"   • Average Specific Discharge: {avg_specific_discharge:.2f} l/s/km²")
    
    # Turbine sizing recommendations
    months = ['Ekim', 'Kasım', 'Aralık', 'Ocak', 'Şubat', 'Mart', 
              'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül']
    
    all_flows = []
    for month in months:
        month_data = df[month].dropna().tolist()
        all_flows.extend(month_data)
    
    if all_flows:
        q50 = np.percentile(all_flows, 50)  # 50% exceedance
        q90 = np.percentile(all_flows, 10)  # 90% exceedance
        
        print(f"\n2. TURBINE SIZING RECOMMENDATIONS:")
        print(f"   • Q50 (Design Flow): {q50:.1f} m³/s")
        print(f"   • Q90 (Reliability Flow): {q90:.1f} m³/s")
        print(f"   • Recommended turbine capacity: {q50*0.8:.1f} - {q50:.1f} m³/s")
        print(f"   • Minimum flow for operation: {q90:.1f} m³/s")
    
    # Seasonal generation potential
    wet_months = ['Mart', 'Nisan', 'Mayıs', 'Haziran']
    dry_months = ['Temmuz', 'Ağustos', 'Eylül', 'Ekim']
    
    wet_data = []
    dry_data = []
    
    for month in wet_months:
        wet_data.extend(df[month].dropna().tolist())
    for month in dry_months:
        dry_data.extend(df[month].dropna().tolist())
    
    if wet_data and dry_data:
        wet_avg = np.mean(wet_data)
        dry_avg = np.mean(dry_data)
        
        print(f"\n3. SEASONAL GENERATION POTENTIAL:")
        print(f"   • Wet Season (Mar-Jun) Average: {wet_avg:.1f} m³/s")
        print(f"   • Dry Season (Jul-Oct) Average: {dry_avg:.1f} m³/s")
        print(f"   • Seasonal Generation Ratio: {wet_avg/dry_avg:.1f}:1")
        print(f"   • Peak generation period: March-June")
    
    # Flood safety considerations
    if all_flows:
        q10 = np.percentile(all_flows, 90)  # 10% exceedance
        max_flow = max(all_flows)
        
        print(f"\n4. FLOOD SAFETY CONSIDERATIONS:")
        print(f"   • Q10 (10% exceedance): {q10:.1f} m³/s")
        print(f"   • Maximum recorded flow: {max_flow:.1f} m³/s")
        print(f"   • Spillway design capacity: ≥ {max_flow*1.2:.1f} m³/s")
        print(f"   • Flood frequency: High flows occur mainly in spring")
    
    # Energy potential estimation
    if all_flows:
        head_estimate = 50  # meters (typical for this region)
        efficiency = 0.85
        power_density = 9.81 * head_estimate * efficiency / 1000  # kW per m³/s
        
        print(f"\n5. ENERGY POTENTIAL ESTIMATION:")
        print(f"   • Assumed head: {head_estimate} m")
        print(f"   • Turbine efficiency: {efficiency*100:.0f}%")
        print(f"   • Power density: {power_density:.1f} kW per m³/s")
        print(f"   • Average power potential: {q50 * power_density:.0f} kW")
        print(f"   • Annual energy potential: {avg_annual_volume * 1000 * power_density / 8760:.0f} MWh")

def main():
    """Main analysis function"""
    print("HYDROLOGICAL ANALYSIS FOR KUZEY I-II REGULATOR AND HYDROELECTRIC POWER PLANT")
    print("Ordu, Türkiye - Streamflow Data Analysis (2000-2020)")
    print("="*80)
    
    # Load and prepare data
    df = load_and_prepare_data()
    
    if len(df) == 0:
        print("No data available for analysis")
        return
    
    # Create visualizations
    create_annual_trend_analysis(df)
    create_monthly_regime_analysis(df)
    create_flow_duration_curve(df)
    create_correlation_analysis(df)
    create_extreme_flow_analysis(df)
    create_summary_statistics_table(df)
    
    # Generate hydropower insights
    generate_hydropower_insights(df)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nGenerated PNG files:")
    print("1. 1_annual_trend_analysis.png")
    print("2. 2_monthly_regime_analysis.png")
    print("3. 3_flow_duration_curve.png")
    print("4. 4_correlation_analysis.png")
    print("5. 5_extreme_flow_analysis.png")
    print("6. 6_summary_statistics_table.png")
    print("\nGenerated CSV file:")
    print("• monthly_statistics_summary.csv")

if __name__ == "__main__":
    main()
