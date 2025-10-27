import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# Set style for better looking charts
plt.style.use('seaborn-v0_8-darkgrid')
matplotlib.rcParams['figure.figsize'] = (14, 8)

def load_data():
    """Load the merged flow data from CSV"""
    df = pd.read_csv('merged_flow_data.csv')
    # Convert year to integer for proper sorting
    df['year'] = df['year'].astype(int)
    return df

def create_all_stations_overview(df):
    """Create a chart showing all stations over time"""
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Group by station and plot each one
    for station in df['station_code'].unique():
        station_data = df[df['station_code'] == station].sort_values('year')
        if len(station_data) > 1:  # Only plot stations with multiple years
            ax.plot(station_data['year'], station_data['avg_annual_flow_m3s'], 
                   marker='o', label=station, alpha=0.7, linewidth=1.5, markersize=4)
    
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Annual Flow (m³/s)', fontsize=12, fontweight='bold')
    ax.set_title('Flow vs Years - All Stations', fontsize=16, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('chart_all_stations.png', dpi=300, bbox_inches='tight')
    print("✓ Created chart_all_stations.png")
    plt.close()

def create_top_stations_chart(df, top_n=10):
    """Create a chart showing the top N stations with highest flows"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Calculate average flow for each station
    avg_flows = df.groupby('station_code')['avg_annual_flow_m3s'].mean().sort_values(ascending=False)
    top_stations = avg_flows.head(top_n).index.tolist()
    
    # Plot each top station
    for station in top_stations:
        station_data = df[df['station_code'] == station].sort_values('year')
        ax.plot(station_data['year'], station_data['avg_annual_flow_m3s'], 
               marker='o', label=station, linewidth=2, markersize=6)
    
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Annual Flow (m³/s)', fontsize=12, fontweight='bold')
    ax.set_title(f'Flow vs Years - Top {top_n} Stations by Average Flow', 
                fontsize=16, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('chart_top_stations.png', dpi=300, bbox_inches='tight')
    print(f"✓ Created chart_top_stations.png (top {top_n} stations)")
    plt.close()

def create_subplot_grid(df, stations_per_plot=6):
    """Create multiple charts in a grid showing different station groups"""
    unique_stations = sorted(df['station_code'].unique())
    n_stations = len(unique_stations)
    n_plots = (n_stations + stations_per_plot - 1) // stations_per_plot
    
    # Create subplots grid
    rows = 2
    cols = 2
    fig, axes = plt.subplots(rows, cols, figsize=(16, 12))
    axes = axes.flatten()
    
    for idx in range(min(n_plots, len(axes))):
        ax = axes[idx]
        start_idx = idx * stations_per_plot
        end_idx = start_idx + stations_per_plot
        stations_group = unique_stations[start_idx:end_idx]
        
        for station in stations_group:
            station_data = df[df['station_code'] == station].sort_values('year')
            if len(station_data) > 1:
                ax.plot(station_data['year'], station_data['avg_annual_flow_m3s'], 
                       marker='o', label=station, linewidth=2)
        
        ax.set_xlabel('Year', fontsize=10)
        ax.set_ylabel('Average Annual Flow (m³/s)', fontsize=10)
        ax.set_title(f'Stations {start_idx+1}-{end_idx}', fontsize=12)
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for idx in range(n_plots, len(axes)):
        axes[idx].axis('off')
    
    plt.suptitle('Flow vs Years - Station Groups', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('chart_subplot_grid.png', dpi=300, bbox_inches='tight')
    print(f"✓ Created chart_subplot_grid.png ({n_plots} subplots)")
    plt.close()

def create_trend_analysis(df):
    """Create a chart showing trend analysis for stations with longest data"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Find stations with most years of data
    station_counts = df.groupby('station_code').size().sort_values(ascending=False)
    top_longest = station_counts.head(8).index.tolist()
    
    # Plot with trend lines
    for station in top_longest:
        station_data = df[df['station_code'] == station].sort_values('year')
        
        # Plot the data
        ax.plot(station_data['year'], station_data['avg_annual_flow_m3s'], 
               marker='o', label=station, linewidth=2, markersize=6)
        
        # Add trend line if enough points
        if len(station_data) >= 3:
            z = np.polyfit(station_data['year'], station_data['avg_annual_flow_m3s'], 1)
            p = np.poly1d(z)
            ax.plot(station_data['year'], p(station_data['year']), 
                   "--", alpha=0.5, linewidth=1)
    
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Annual Flow (m³/s)', fontsize=12, fontweight='bold')
    ax.set_title('Flow vs Years - Stations with Longest Data Records (with trend lines)', 
                fontsize=16, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('chart_trend_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Created chart_trend_analysis.png")
    plt.close()

def create_chart_excluding_extreme_stations(df, exclude_n=6):
    """Create a chart showing all stations except the top N with extraordinary flow values"""
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Calculate average flow for each station
    avg_flows = df.groupby('station_code')['avg_annual_flow_m3s'].mean().sort_values(ascending=False)
    top_stations = avg_flows.head(exclude_n).index.tolist()
    
    print(f"\nExcluding {exclude_n} stations with highest average flows:")
    for station in top_stations:
        print(f"  {station}: {avg_flows[station]:.3f} m³/s")
    
    # Filter out the top stations
    filtered_df = df[~df['station_code'].isin(top_stations)]
    
    # Plot remaining stations
    for station in filtered_df['station_code'].unique():
        station_data = filtered_df[filtered_df['station_code'] == station].sort_values('year')
        if len(station_data) > 1:  # Only plot stations with multiple years
            ax.plot(station_data['year'], station_data['avg_annual_flow_m3s'], 
                   marker='o', label=station, alpha=0.8, linewidth=2, markersize=5)
    
    # Calculate and plot overall average line for filtered stations
    yearly_avg_filtered = filtered_df.groupby('year')['avg_annual_flow_m3s'].mean()
    ax.plot(yearly_avg_filtered.index, yearly_avg_filtered.values, 
           marker='s', linewidth=4, markersize=10, color='red', 
           label='Overall Average', alpha=0.9, zorder=10, markeredgecolor='white', markeredgewidth=2)
    
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Annual Flow (m³/s)', fontsize=12, fontweight='bold')
    ax.set_title(f'Flow vs Years - All Stations (Excluding Top {exclude_n} Extreme Stations)', 
                fontsize=16, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('chart_excluding_extreme_stations.png', dpi=300, bbox_inches='tight')
    print("✓ Created chart_excluding_extreme_stations.png")
    plt.close()

def create_average_flow_chart(df):
    """Create a chart showing the average flow across all stations year by year"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Calculate average flow across all stations for each year
    yearly_average = df.groupby('year')['avg_annual_flow_m3s'].mean()
    
    # Plot the average flow
    ax.plot(yearly_average.index, yearly_average.values, 
           marker='o', linewidth=3, markersize=10, color='#2E86AB', 
           markerfacecolor='#A23B72', markeredgecolor='white', markeredgewidth=2)
    
    # Add value labels on points
    for year, value in zip(yearly_average.index, yearly_average.values):
        ax.annotate(f'{value:.2f}', (year, value), 
                   textcoords="offset points", xytext=(0,10), ha='center',
                   fontsize=9, fontweight='bold')
    
    ax.set_xlabel('Year', fontsize=14, fontweight='bold')
    ax.set_ylabel('Average Flow Across All Stations (m³/s)', fontsize=14, fontweight='bold')
    ax.set_title('Year-by-Year Average Flow Across All Stations', 
                fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_ylim(bottom=0)  # Start y-axis from 0
    
    # Add some styling
    plt.xticks(yearly_average.index, rotation=45)
    
    plt.tight_layout()
    plt.savefig('chart_average_flow_yearly.png', dpi=300, bbox_inches='tight')
    print("✓ Created chart_average_flow_yearly.png")
    plt.close()

def create_average_only_chart(df, exclude_n=6):
    """Create a chart showing only the average flow line for stations excluding extremes"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Calculate average flow for each station
    avg_flows = df.groupby('station_code')['avg_annual_flow_m3s'].mean().sort_values(ascending=False)
    top_stations = avg_flows.head(exclude_n).index.tolist()
    
    # Filter out the top stations
    filtered_df = df[~df['station_code'].isin(top_stations)]
    
    # Calculate and plot overall average line for filtered stations
    yearly_avg_filtered = filtered_df.groupby('year')['avg_annual_flow_m3s'].mean()
    
    # Plot only the average line
    ax.plot(yearly_avg_filtered.index, yearly_avg_filtered.values, 
           marker='o', linewidth=4, markersize=12, color='#E63946', 
           markerfacecolor='#F77F00', markeredgecolor='white', markeredgewidth=3,
           label='Average Flow (Excluding 6 Extreme Stations)', alpha=0.9)
    
    # Add value labels on points
    for year, value in zip(yearly_avg_filtered.index, yearly_avg_filtered.values):
        ax.annotate(f'{value:.2f}', (year, value), 
                   textcoords="offset points", xytext=(0,15), ha='center',
                   fontsize=11, fontweight='bold', color='#333333')
    
    ax.set_xlabel('Year', fontsize=14, fontweight='bold')
    ax.set_ylabel('Average Flow (m³/s)', fontsize=14, fontweight='bold')
    ax.set_title('Average Flow Trend (Excluding Top 6 Extreme Stations)', 
                fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_ylim(bottom=0)  # Start y-axis from 0
    ax.legend(loc='best', fontsize=12, framealpha=0.9)
    
    # Add some styling
    plt.xticks(yearly_avg_filtered.index, rotation=45)
    
    plt.tight_layout()
    plt.savefig('chart_average_only.png', dpi=300, bbox_inches='tight')
    print("✓ Created chart_average_only.png")
    plt.close()

def create_summary_stats():
    """Print summary statistics to console"""
    df = load_data()
    
    print("\n" + "="*60)
    print("DATA SUMMARY STATISTICS")
    print("="*60)
    print(f"Total records: {len(df)}")
    print(f"Total unique stations: {df['station_code'].nunique()}")
    print(f"Years covered: {df['year'].min()} - {df['year'].max()}")
    print(f"\nTop 10 stations by average flow:")
    avg_flows = df.groupby('station_code')['avg_annual_flow_m3s'].mean().sort_values(ascending=False).head(10)
    for station, flow in avg_flows.items():
        print(f"  {station}: {flow:.3f} m³/s")
    print("="*60 + "\n")

def main():
    """Main function to generate all charts"""
    print("\nGenerating flow vs years charts...")
    print("-" * 60)
    
    # Load data
    df = load_data()
    
    # Generate charts
    create_all_stations_overview(df)
    create_top_stations_chart(df, top_n=10)
    create_subplot_grid(df, stations_per_plot=6)
    create_trend_analysis(df)
    create_chart_excluding_extreme_stations(df, exclude_n=6)
    create_average_flow_chart(df)
    create_average_only_chart(df, exclude_n=6)
    
    # Print statistics
    create_summary_stats()
    
    print("All charts generated successfully! ✓")
    print("\nGenerated files:")
    print("  - chart_all_stations.png")
    print("  - chart_top_stations.png")
    print("  - chart_subplot_grid.png")
    print("  - chart_trend_analysis.png")
    print("  - chart_excluding_extreme_stations.png")
    print("  - chart_average_flow_yearly.png")
    print("  - chart_average_only.png")

if __name__ == "__main__":
    main()
