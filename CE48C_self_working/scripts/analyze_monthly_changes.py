#!/usr/bin/env python3
"""
Analyze monthly changes for all 6 metrics
Calculate average for each month across all years to show seasonal patterns
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_monthly_changes():
    # Read the CSV
    csv_file = "dsi_2000_2020_final_structured_UPDATED_CORRECTED_ROUNDED_WITH_ANNUAL_AVG.csv"
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} records")
    
    # Define all monthly metric columns (6 metrics x 12 months)
    monthly_metrics = [
        'flow_max_m3', 'flow_min_m3', 'flow_avg_m3', 
        'ltsnkm2_m3', 'akim_mm_m3', 'milm3_m3'
    ]
    
    months = ['oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep']
    month_names = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
    
    # Create results dictionary
    monthly_averages = {}
    
    print("\n=== MONTHLY AVERAGES ACROSS ALL YEARS ===\n")
    
    # Calculate monthly averages for each metric
    for metric in monthly_metrics:
        print(f"--- {metric.upper()} ---")
        monthly_vals = []
        
        for month in months:
            col = f"{month}_{metric}"
            # Calculate average of this month across all years
            month_avg = df[col].mean()
            monthly_vals.append(month_avg)
            print(f"{month.upper()}: {month_avg:.2f}")
        
        monthly_averages[metric] = monthly_vals
        print()
    
    # Create visualization
    create_monthly_charts(monthly_averages, month_names)
    
    # Create summary table
    create_summary_table(monthly_averages, month_names)
    
    return monthly_averages

def create_monthly_charts(monthly_averages, month_names):
    """Create charts showing monthly patterns"""
    
    # Create subplots for all 6 metrics
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Monthly Changes in Hydrological Metrics (Average Across All Years)', fontsize=16, fontweight='bold')
    
    metrics = list(monthly_averages.keys())
    metric_titles = [
        'Flow Max (m³/s)', 'Flow Min (m³/s)', 'Flow Avg (m³/s)',
        'LT/SN/Km²', 'AKIM mm', 'MIL M³'
    ]
    
    for i, (metric, title) in enumerate(zip(metrics, metric_titles)):
        row = i // 3
        col = i % 3
        ax = axes[row, col]
        
        values = monthly_averages[metric]
        
        # Create line plot
        ax.plot(range(12), values, marker='o', linewidth=2, markersize=8, color='#2E86AB')
        ax.fill_between(range(12), values, alpha=0.3, color='#2E86AB')
        
        # Customize the plot
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Month', fontsize=10)
        ax.set_ylabel('Average Value', fontsize=10)
        ax.set_xticks(range(12))
        ax.set_xticklabels(month_names, rotation=45)
        ax.grid(True, alpha=0.3)
        
        # Add value labels
        for j, val in enumerate(values):
            if not np.isnan(val):
                ax.annotate(f'{val:.2f}', (j, val), textcoords="offset points", 
                           xytext=(0,10), ha='center', fontsize=8)
    
    plt.tight_layout()
    
    # Save the chart
    output_path = "monthly_changes_analysis.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to: {output_path}")
    
    plt.show()

def create_summary_table(monthly_averages, month_names):
    """Create a summary table of monthly averages"""
    
    # Create DataFrame for summary
    summary_data = {}
    for metric, values in monthly_averages.items():
        summary_data[metric] = values
    
    summary_df = pd.DataFrame(summary_data, index=month_names)
    
    print("\n=== SUMMARY TABLE: MONTHLY AVERAGES ===\n")
    print(summary_df.round(2).to_string())
    
    # Save summary to CSV
    summary_file = "monthly_averages_summary.csv"
    summary_df.to_csv(summary_file)
    print(f"\nSummary table saved to: {summary_file}")
    
    # Calculate seasonal statistics
    print("\n=== SEASONAL STATISTICS ===\n")
    for metric in monthly_averages.keys():
        values = monthly_averages[metric]
        valid_values = [v for v in values if not np.isnan(v)]
        
        if valid_values:
            min_val = min(valid_values)
            max_val = max(valid_values)
            min_month = month_names[values.index(min_val)]
            max_month = month_names[values.index(max_val)]
            
            print(f"{metric.upper()}:")
            print(f"  Minimum: {min_val:.2f} ({min_month})")
            print(f"  Maximum: {max_val:.2f} ({max_month})")
            print(f"  Range: {max_val - min_val:.2f}")
            print()

if __name__ == "__main__":
    monthly_averages = analyze_monthly_changes()
    print("\n[SUCCESS] Monthly analysis completed!")
