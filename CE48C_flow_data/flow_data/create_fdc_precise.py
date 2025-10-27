"""
Create a precise Flow Duration Curve (FDC) from flow data
Generates a high-resolution FDC with detailed values at 90% exceedance
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11

# Create charts directory if it doesn't exist
Path('charts').mkdir(exist_ok=True)

print("Loading data...")
df = pd.read_csv('dsi_final_excluding_extremes.csv')

print(f"Dataset loaded: {len(df)} records")
print(f"Stations: {df['station_code'].nunique()}")

# Define monthly columns
monthly_cols = [
    'oct_avg', 'nov_avg', 'dec_avg', 'jan_avg', 'feb_avg', 'mar_avg',
    'apr_avg', 'may_avg', 'jun_avg', 'jul_avg', 'aug_avg', 'sep_avg'
]

# Extract all monthly flow values
print("Extracting all monthly flow values...")
all_flows = []
for col in monthly_cols:
    if col in df.columns:
        flows = df[col].dropna().tolist()
        all_flows.extend(flows)

print(f"Total flow data points: {len(all_flows)}")
print(f"Flow range: {min(all_flows):.3f} - {max(all_flows):.3f} m³/s")

# Convert to numpy array
flow_array = np.array(all_flows)

# Calculate percentiles (exceedance probability)
# Use high resolution for more precision
percentiles = np.arange(0, 101, 0.5)  # Every 0.5% instead of every 1%
# For exceedance probability, we want percentile = 100 - exceedance_probability
# So exceedance 90% means percentile 10%
percentile_values = (100 - percentiles).clip(0, 100)
flow_values = np.percentile(flow_array, percentile_values)

# Create the plot
fig, ax = plt.subplots(figsize=(14, 8))

# Plot the flow duration curve
ax.plot(percentiles, flow_values, linewidth=2.5, color='#2E86AB', label='Flow Duration Curve')

# Highlight 90% exceedance probability with a marker
idx_90 = np.where(percentiles == 90)[0][0]
flow_90 = flow_values[idx_90]
ax.plot(90, flow_90, 'ro', markersize=12, label=f'90%: {flow_90:.4f} m³/s', zorder=5)

# Add vertical line at 90%
ax.axvline(x=90, color='red', linestyle='--', linewidth=1.5, alpha=0.5, zorder=4)

# Add horizontal line at flow value for 90%
ax.axhline(y=flow_90, color='red', linestyle='--', linewidth=1.5, alpha=0.5, zorder=4)

# Add text annotation for 90%
ax.annotate(f'90%: {flow_90:.4f} m³/s', 
           xy=(90, flow_90), 
           xytext=(92, flow_90 + max(flow_array) * 0.1),
           fontsize=11, 
           fontweight='bold',
           color='darkred',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2', color='darkred'))

# Highlight key percentiles
key_percentiles = [0, 10, 25, 50, 75, 90, 95, 99, 100]
for p in key_percentiles:
    idx = np.where(percentiles == p)[0][0]
    flow_p = flow_values[idx]
    ax.plot(p, flow_p, 'o', markersize=6, color='darkblue', alpha=0.7)
    
    # Add labels for key percentiles
    if p in [10, 50, 90]:
        ax.text(p, flow_p, f'{flow_p:.3f}', 
               fontsize=9, ha='center', va='bottom',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Customize the plot
ax.set_xlabel('Exceedance Probability (%)', fontsize=13, fontweight='bold')
ax.set_ylabel('Flow (m³/s)', fontsize=13, fontweight='bold')
ax.set_title('Flow Duration Curve (Precise)', fontsize=15, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3)
ax.legend(loc='upper right', fontsize=10)

# Add statistics text box
stats_text = f"""Statistics:
Total data points: {len(all_flows):,}
Max flow: {max(flow_array):.3f} m³/s
Min flow: {min(flow_array):.3f} m³/s
Mean flow: {np.mean(flow_array):.3f} m³/s
Median flow: {np.median(flow_array):.3f} m³/s
90% flow: {flow_90:.4f} m³/s"""
ax.text(0.02, 0.98, stats_text, 
        transform=ax.transAxes, 
        fontsize=9,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.savefig('charts/fdc_precise.png', dpi=300, bbox_inches='tight')
print("\n[OK] Created charts/fdc_precise.png")

# Print detailed statistics
print("\n" + "="*60)
print("FLOW DURATION CURVE STATISTICS")
print("="*60)
print(f"\nTotal monthly flow observations: {len(all_flows):,}")
print(f"Flow range: {min(all_flows):.3f} - {max(all_flows):.3f} m³/s")
print(f"Mean flow: {np.mean(flow_array):.3f} m³/s")
print(f"Median flow: {np.median(flow_array):.3f} m³/s")

print("\nKey Exceedance Probabilities:")
for p in [0, 5, 10, 25, 50, 75, 90, 95, 99, 100]:
    idx = np.where(percentiles == p)[0][0]
    flow_p = flow_values[idx]
    print(f"  {p:3d}%: {flow_p:8.4f} m³/s")

print("="*60)
print("\nChart saved to: charts/fdc_precise.png")

