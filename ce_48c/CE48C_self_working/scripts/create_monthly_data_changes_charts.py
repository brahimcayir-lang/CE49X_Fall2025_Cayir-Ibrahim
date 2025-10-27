#!/usr/bin/env python3
"""
Create monthly data changes charts showing how monthly values change over time
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
    
    print(f"Data loaded: {len(df)} records")
    print(f"Years available: {sorted(df['year'].unique())}")
    print(f"Stations: {df['station_code'].nunique()}")
    
    return df, metrics, month_names

def create_monthly_trends_chart(df, metrics, month_names):
    """Create monthly trends chart showing changes over years"""
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    axes = axes.flatten()
    
    for i, (metric_name, metric_info) in enumerate(metrics.items()):
        ax = axes[i]
        
        # Calculate yearly averages for each month
        monthly_trends = {}
        for j, month_col in enumerate(metric_info['columns']):
            monthly_trends[month_names[j]] = df.groupby('year')[month_col].mean()
        
        # Plot trends for each month
        years = list(monthly_trends.values())[0].index
        colors = plt.cm.tab20(np.linspace(0, 1, len(month_names)))
        
        for j, (month, values) in enumerate(monthly_trends.items()):
            ax.plot(years, values, 'o-', linewidth=2, markersize=4,
                   color=colors[j], label=month, alpha=0.8)
        
        ax.set_xlabel('Year', fontsize=10, fontweight='bold')
        ax.set_ylabel(f'{metric_name} ({metric_info["unit"]})', fontsize=10, fontweight='bold')
        ax.set_title(f'{metric_name} - Monthly Trends Over Years', fontsize=12, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Monthly Data Trends Over Years (2005-2020)', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    filename = 'monthly_data_trends_chart.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig

def create_monthly_change_analysis(df, metrics, month_names):
    """Create monthly change analysis chart"""
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    axes = axes.flatten()
    
    for i, (metric_name, metric_info) in enumerate(metrics.items()):
        ax = axes[i]
        
        # Calculate percentage change from first year for each month
        monthly_changes = {}
        first_year = df['year'].min()
        
        for j, month_col in enumerate(metric_info['columns']):
            yearly_means = df.groupby('year')[month_col].mean()
            first_year_value = yearly_means.iloc[0]
            percentage_changes = ((yearly_means - first_year_value) / first_year_value) * 100
            monthly_changes[month_names[j]] = percentage_changes
        
        # Plot changes for each month
        years = list(monthly_changes.values())[0].index
        colors = plt.cm.tab20(np.linspace(0, 1, len(month_names)))
        
        for j, (month, changes) in enumerate(monthly_changes.items()):
            ax.plot(years, changes, 'o-', linewidth=2, markersize=4,
                   color=colors[j], label=month, alpha=0.8)
        
        # Add zero line
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        ax.set_xlabel('Year', fontsize=10, fontweight='bold')
        ax.set_ylabel('Change from 2005 (%)', fontsize=10, fontweight='bold')
        ax.set_title(f'{metric_name} - Monthly Change Analysis', fontsize=12, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Monthly Data Change Analysis (2005-2020)', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    filename = 'monthly_data_change_analysis.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig

def create_seasonal_patterns_chart(df, metrics, month_names):
    """Create seasonal patterns chart"""
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
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
        
        # Calculate seasonal averages over years
        seasonal_data = {}
        for season, months in seasons.items():
            season_values = []
            for month in months:
                month_idx = month_names.index(month)
                month_col = metric_info['columns'][month_idx]
                season_values.extend(df[month_col].dropna().tolist())
            seasonal_data[season] = season_values
        
        # Create box plot for seasonal distribution
        box_data = [seasonal_data[season] for season in seasons.keys()]
        bp = ax.boxplot(box_data, tick_labels=list(seasons.keys()), patch_artist=True)
        
        # Color the boxes
        colors = ['#FF9999', '#66B3FF', '#99FF99', '#FFCC99']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_xlabel('Season', fontsize=10, fontweight='bold')
        ax.set_ylabel(f'{metric_name} ({metric_info["unit"]})', fontsize=10, fontweight='bold')
        ax.set_title(f'{metric_name} - Seasonal Patterns', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Seasonal Patterns in Monthly Data', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    filename = 'monthly_seasonal_patterns_chart.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig

def create_monthly_correlation_chart(df, metrics, month_names):
    """Create monthly correlation analysis chart"""
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    axes = axes.flatten()
    
    for i, (metric_name, metric_info) in enumerate(metrics.items()):
        ax = axes[i]
        
        # Create correlation matrix for months
        monthly_data = df[metric_info['columns']].copy()
        monthly_data.columns = month_names
        correlation_matrix = monthly_data.corr()
        
        # Create heatmap
        im = ax.imshow(correlation_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        
        # Add correlation values as text
        for j in range(len(correlation_matrix.columns)):
            for k in range(len(correlation_matrix.index)):
                text = ax.text(k, j, f'{correlation_matrix.iloc[j, k]:.2f}',
                             ha="center", va="center", color="black", fontweight='bold')
        
        ax.set_xticks(range(len(correlation_matrix.columns)))
        ax.set_yticks(range(len(correlation_matrix.index)))
        ax.set_xticklabels(correlation_matrix.columns, rotation=45)
        ax.set_yticklabels(correlation_matrix.index)
        ax.set_title(f'{metric_name} - Monthly Correlations', fontsize=12, fontweight='bold')
    
    plt.suptitle('Monthly Correlations Within Each Metric', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    filename = 'monthly_correlation_analysis.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig

def create_monthly_variability_chart(df, metrics, month_names):
    """Create monthly variability analysis chart"""
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    axes = axes.flatten()
    
    for i, (metric_name, metric_info) in enumerate(metrics.items()):
        ax = axes[i]
        
        # Calculate coefficient of variation for each month
        monthly_cv = []
        monthly_means = []
        monthly_stds = []
        
        for month_col in metric_info['columns']:
            values = df[month_col].dropna()
            mean_val = values.mean()
            std_val = values.std()
            cv_val = (std_val / mean_val) * 100 if mean_val > 0 else 0
            
            monthly_cv.append(cv_val)
            monthly_means.append(mean_val)
            monthly_stds.append(std_val)
        
        # Create bar chart for coefficient of variation
        x_pos = np.arange(len(month_names))
        bars = ax.bar(x_pos, monthly_cv, color=metric_info['color'], alpha=0.7)
        
        ax.set_xlabel('Month', fontsize=10, fontweight='bold')
        ax.set_ylabel('Coefficient of Variation (%)', fontsize=10, fontweight='bold')
        ax.set_title(f'{metric_name} - Monthly Variability', fontsize=12, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(month_names)
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, cv in zip(bars, monthly_cv):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                   f'{cv:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.suptitle('Monthly Variability Analysis (Coefficient of Variation)', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    filename = 'monthly_variability_analysis.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig

def create_monthly_summary_chart(df, metrics, month_names):
    """Create monthly summary statistics chart"""
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Calculate overall statistics for each metric
    stats_data = []
    for metric_name, metric_info in metrics.items():
        all_values = []
        for col in metric_info['columns']:
            all_values.extend(df[col].dropna().tolist())
        
        values_array = np.array(all_values)
        stats_data.append({
            'Metric': metric_name,
            'Mean': values_array.mean(),
            'Std': values_array.std(),
            'Min': values_array.min(),
            'Max': values_array.max(),
            'CV': (values_array.std() / values_array.mean()) * 100 if values_array.mean() > 0 else 0
        })
    
    stats_df = pd.DataFrame(stats_data)
    
    # Create horizontal bar chart for coefficient of variation
    y_pos = np.arange(len(stats_df))
    colors = [metrics[metric]['color'] for metric in stats_df['Metric']]
    bars = ax.barh(y_pos, stats_df['CV'], color=colors, alpha=0.7)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(stats_df['Metric'])
    ax.set_xlabel('Coefficient of Variation (%)', fontsize=12, fontweight='bold')
    ax.set_title('Monthly Data Variability Summary', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Add value labels
    for i, (bar, cv) in enumerate(zip(bars, stats_df['CV'])):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
               f'{cv:.1f}%', ha='left', va='center', fontweight='bold')
    
    # Add statistics text box
    stats_text = f"""Monthly Data Summary:
    
Total Records: {len(df)}
Years: {df['year'].min()}-{df['year'].max()} ({df['year'].nunique()} years)
Stations: {df['station_code'].nunique()}
Months per Metric: 12

Most Variable Metric: {stats_df.loc[stats_df['CV'].idxmax(), 'Metric']}
Least Variable Metric: {stats_df.loc[stats_df['CV'].idxmin(), 'Metric']}"""
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            verticalalignment='top', fontsize=10, fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    
    filename = 'monthly_data_summary_statistics.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Created chart: {filename}")
    
    return fig

def main():
    """Main function to create all monthly data change charts"""
    
    csv_file = 'dsi_2000_2020_final_structured_FILLED.csv'
    
    print("Loading data...")
    df, metrics, month_names = load_and_prepare_data(csv_file)
    
    print(f"\nCreating charts for {len(metrics)} monthly metrics...")
    
    # Create all charts
    print("\n1. Creating monthly trends chart...")
    fig1 = create_monthly_trends_chart(df, metrics, month_names)
    plt.close(fig1)
    
    print("\n2. Creating monthly change analysis chart...")
    fig2 = create_monthly_change_analysis(df, metrics, month_names)
    plt.close(fig2)
    
    print("\n3. Creating seasonal patterns chart...")
    fig3 = create_seasonal_patterns_chart(df, metrics, month_names)
    plt.close(fig3)
    
    print("\n4. Creating monthly correlation chart...")
    fig4 = create_monthly_correlation_chart(df, metrics, month_names)
    plt.close(fig4)
    
    print("\n5. Creating monthly variability chart...")
    fig5 = create_monthly_variability_chart(df, metrics, month_names)
    plt.close(fig5)
    
    print("\n6. Creating monthly summary chart...")
    fig6 = create_monthly_summary_chart(df, metrics, month_names)
    plt.close(fig6)
    
    print(f"\n[SUCCESS] All monthly data change charts created successfully!")
    print(f"[CHARTS] Generated 6 comprehensive charts:")
    print(f"  - Monthly trends chart")
    print(f"  - Monthly change analysis chart")
    print(f"  - Seasonal patterns chart")
    print(f"  - Monthly correlation chart")
    print(f"  - Monthly variability chart")
    print(f"  - Monthly summary statistics chart")
    print(f"[DATA] Analysis covers {df['year'].nunique()} years ({df['year'].min()}-{df['year'].max()})")
    print(f"[METRICS] {len(metrics)} monthly metrics analyzed")

if __name__ == "__main__":
    main()

