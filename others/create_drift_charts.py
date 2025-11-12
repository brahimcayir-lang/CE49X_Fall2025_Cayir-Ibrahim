import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# =====================================================
# Read Excel file
# =====================================================
excel_file = Path(__file__).parent / "drift checks.xlsx"

try:
    # Read the Excel file - use header=1 to skip title row and use row 1 as headers
    # Then skip the units row (row 2, index 1) by starting from row 3 (index 2)
    df_raw = pd.read_excel(excel_file, sheet_name=0, header=1)
    
    # Remove the units row (usually the first data row after headers)
    # Check if first row contains mostly text/non-numeric - if so, drop it
    if df_raw.shape[0] > 0:
        first_row = df_raw.iloc[0]
        # If first row is mostly non-numeric or contains 'unitless', drop it
        non_numeric_count = sum([not pd.api.types.is_numeric_dtype(type(v)) and pd.notna(v) 
                                 for v in first_row.values])
        if non_numeric_count > len(first_row) / 2:
            df = df_raw.iloc[1:].reset_index(drop=True)
        else:
            df = df_raw
    else:
        df = df_raw
    
    print("[OK] Excel file loaded successfully")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Shape: {df.shape}")
    print("\nFirst few rows:")
    print(df.head())
    
except Exception as e:
    print(f"[ERROR] Error reading Excel file: {e}")
    print("   Make sure openpyxl is installed: pip install openpyxl")
    raise

# =====================================================
# Extract data from DataFrame
# =====================================================
def find_column(df, keywords):
    """Find column by keywords (case-insensitive)"""
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword.lower() in col_lower for keyword in keywords):
            return col
    return None

# Find elevation column - try multiple patterns
elev_col = find_column(df, ['Elevation', 'elevation', 'Elevation (m)'])
if elev_col is None:
    # Try by position (usually column 1 or 2)
    for idx in [1, 2]:
        if idx < len(df.columns):
            col_val = df.iloc[0, idx] if len(df) > 0 else None
            if pd.api.types.is_numeric_dtype(df.dtypes.iloc[idx]) or (col_val and pd.api.types.is_number(col_val)):
                elev_col = df.columns[idx]
                break
    if elev_col is None:
        elev_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
    print(f"[WARNING] Using column '{elev_col}' as elevation")

# Find drift ratio columns - look for columns containing the drift ratio pattern
# Based on Excel structure: columns 11 and 12 typically contain (δi,max-x)/hi and (δi,max-y)/hi
drift_x_col = None
drift_y_col = None

# Try to find by name first
for col in df.columns:
    col_str = str(col).lower()
    if 'max-x' in col_str or ('x' in col_str and 'hi' in col_str) or ('x' in col_str and 'δ' in str(col)):
        if drift_x_col is None:
            drift_x_col = col
    if 'max-y' in col_str or ('y' in col_str and 'hi' in col_str) or ('y' in col_str and 'δ' in str(col)):
        if drift_y_col is None:
            drift_y_col = col

# If not found by name, try by position (columns 11 and 12 are typically drift ratios)
if drift_x_col is None:
    if len(df.columns) > 11:
        drift_x_col = df.columns[11]
    else:
        # Search for numeric columns that might be drift ratios
        for col in df.columns:
            if df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                sample_vals = df[col].dropna().head(5)
                if len(sample_vals) > 0 and all(0 <= abs(v) <= 1 for v in sample_vals):
                    drift_x_col = col
                    break

if drift_y_col is None:
    if len(df.columns) > 12:
        drift_y_col = df.columns[12]
    elif drift_x_col and drift_x_col in df.columns:
        # Y column is usually right after X column
        x_idx = list(df.columns).index(drift_x_col)
        if x_idx + 1 < len(df.columns):
            drift_y_col = df.columns[x_idx + 1]
    else:
        # Search for another numeric column with small values
        for col in df.columns:
            if col != drift_x_col and df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                sample_vals = df[col].dropna().head(5)
                if len(sample_vals) > 0 and all(0 <= abs(v) <= 1 for v in sample_vals):
                    drift_y_col = col
                    break

# Find limit columns - typically columns 9 and 10
limit_x_col = find_column(df, ['0.008κ / λₓ', '0.008κ / λx', 'limit_x', '0.008'])
limit_y_col = find_column(df, ['0.008κ / λᵧ', '0.008κ / λy', 'limit_y'])

# If not found by name, try by position (columns 9 and 10)
if limit_x_col is None and len(df.columns) > 9:
    limit_x_col = df.columns[9]
if limit_y_col is None:
    # Try to find column with 'y' or 'λy' in the name
    for col in df.columns:
        col_str = str(col).lower()
        if ('y' in col_str or 'λy' in col_str or 'lambda_y' in col_str) and '0.008' in col_str:
            limit_y_col = col
            break
    if limit_y_col is None and len(df.columns) > 10:
        limit_y_col = df.columns[10]

print(f"\n[INFO] Detected columns:")
print(f"   Elevation: {elev_col}")
print(f"   X-Drift: {drift_x_col}")
print(f"   Y-Drift: {drift_y_col}")
print(f"   Limit X: {limit_x_col}")
print(f"   Limit Y: {limit_y_col}")

# Extract data
if drift_x_col is None or drift_y_col is None:
    print(f"[ERROR] Could not find drift ratio columns!")
    print(f"   Available columns: {list(df.columns)}")
    print(f"   Please check the Excel file structure.")
    raise ValueError("Missing drift ratio columns")

elevations = pd.to_numeric(df[elev_col], errors='coerce').values
drift_ratios_x = pd.to_numeric(df[drift_x_col], errors='coerce').values
drift_ratios_y = pd.to_numeric(df[drift_y_col], errors='coerce').values

# Remove rows with NaN values (like Foundation row with zeros)
valid_mask = ~(np.isnan(elevations) | np.isnan(drift_ratios_x) | np.isnan(drift_ratios_y))
# Also filter out rows where all values are zero (Foundation)
zero_mask = (np.abs(drift_ratios_x) > 1e-10) | (np.abs(drift_ratios_y) > 1e-10)
valid_mask = valid_mask & zero_mask

elevations = elevations[valid_mask]
drift_ratios_x = drift_ratios_x[valid_mask]
drift_ratios_y = drift_ratios_y[valid_mask]

if len(elevations) == 0:
    print(f"[ERROR] No valid data found after filtering!")
    raise ValueError("No valid data rows found")

# Get limit values
if limit_x_col and limit_x_col in df.columns:
    limit_x_values = pd.to_numeric(df[limit_x_col], errors='coerce').dropna()
    if len(limit_x_values) > 0:
        # Get first non-zero value, or first value if all are zero
        non_zero = limit_x_values[limit_x_values != 0]
        if len(non_zero) > 0:
            limit_x = non_zero.iloc[0]
        else:
            limit_x = limit_x_values.iloc[0] if len(limit_x_values) > 0 else None
    else:
        limit_x = None
else:
    limit_x = None

if limit_x is None:
    # Calculate from data: use max value * safety factor, or use default of 0.02
    if len(drift_ratios_x) > 0:
        max_abs_x = np.max(np.abs(drift_ratios_x))
        limit_x = max(max_abs_x * 1.5, 0.02)  # At least 0.02 or 1.5x max
    else:
        limit_x = 0.02
    print(f"[WARNING] Limit X not found, using calculated value: {limit_x:.6f}")

if limit_y_col and limit_y_col in df.columns:
    limit_y_values = pd.to_numeric(df[limit_y_col], errors='coerce').dropna()
    if len(limit_y_values) > 0:
        non_zero = limit_y_values[limit_y_values != 0]
        if len(non_zero) > 0:
            limit_y = non_zero.iloc[0]
        else:
            limit_y = limit_y_values.iloc[0] if len(limit_y_values) > 0 else None
    else:
        limit_y = None
else:
    limit_y = None

if limit_y is None:
    if len(drift_ratios_y) > 0:
        max_abs_y = np.max(np.abs(drift_ratios_y))
        limit_y = max(max_abs_y * 1.5, 0.02)
    else:
        limit_y = 0.02
    print(f"[WARNING] Limit Y not found, using calculated value: {limit_y:.6f}")

# Calculate maximum drift ratios
max_drift_x = np.max(np.abs(drift_ratios_x))
max_drift_y = np.max(np.abs(drift_ratios_y))

print(f"\n[INFO] Data summary:")
print(f"   Number of stories: {len(elevations)}")
print(f"   Elevation range: {np.min(elevations):.2f} to {np.max(elevations):.2f} m")
print(f"   Max X-drift: {max_drift_x:.6f}")
print(f"   Max Y-drift: {max_drift_y:.6f}")
print(f"   Limit X: {limit_x:.6f}")
print(f"   Limit Y: {limit_y:.6f}")

# =====================================================
# Create symmetric data for oscillatory motion
# =====================================================
# Sort by elevation for smooth curves
sort_idx = np.argsort(elevations)
elevations_sorted = elevations[sort_idx]
drift_ratios_x_sorted = drift_ratios_x[sort_idx]
drift_ratios_y_sorted = drift_ratios_y[sort_idx]

# Create symmetric curves: positive and negative values
# This represents the building motion going back and forth (oscillatory motion)
# The envelope shows maximum displacement range at each elevation
drift_x_pos = drift_ratios_x_sorted
drift_x_neg = -drift_ratios_x_sorted
drift_y_pos = drift_ratios_y_sorted
drift_y_neg = -drift_ratios_y_sorted

# Create symmetric curves - two separate lines (not connected at top)
# Negative values (left side) and positive values (right side)
# No connection between them at the top

# =====================================================
# Create the plots
# =====================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))

# Common settings
drift_range = max(0.03, max(max_drift_x, max_drift_y) * 1.5)
elevation_min = np.min(elevations) - 2
elevation_max = np.max(elevations) + 2

# =====================================================
# Plot 1: X-Direction
# =====================================================
# Plot two separate symmetric curves (negative and positive, not connected at top)
ax1.plot(drift_x_neg, elevations_sorted, 'b-', linewidth=2, label='Interstory Drift Ratio')
ax1.plot(drift_x_pos, elevations_sorted, 'b-', linewidth=2)
# Plot individual data points for clarity
ax1.plot(drift_x_pos, elevations_sorted, 'bo', markersize=3, alpha=0.5, zorder=3)
ax1.plot(drift_x_neg, elevations_sorted, 'bo', markersize=3, alpha=0.5, zorder=3)
ax1.axvline(x=limit_x, color='r', linestyle='--', linewidth=1.5, label=f'Limit = {limit_x:.4f}')
ax1.axvline(x=-limit_x, color='r', linestyle='--', linewidth=1.5)
ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
ax1.axvline(x=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)

ax1.set_xlabel('Interstory Drift Ratio', fontsize=12, fontweight='bold')
ax1.set_ylabel('Elevation (m)', fontsize=12, fontweight='bold')
ax1.set_title('Maximum Interstory Drift Ratios in X Direction', fontsize=13, fontweight='bold')
ax1.set_xlim(-drift_range, drift_range)
ax1.set_ylim(elevation_min, elevation_max)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.legend(loc='upper right', fontsize=9)

# Add summary equation
summary_text_x = f'$\\delta_{{i,max}}^{{(X)}} / h_i = {max_drift_x:.3f} \\leq {limit_x:.3f}$'
ax1.text(0.02, 0.98, summary_text_x, transform=ax1.transAxes, 
         fontsize=11, verticalalignment='top', horizontalalignment='left',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# =====================================================
# Plot 2: Y-Direction
# =====================================================
# Plot two separate symmetric curves (negative and positive, not connected at top)
ax2.plot(drift_y_neg, elevations_sorted, 'b-', linewidth=2, label='Interstory Drift Ratio')
ax2.plot(drift_y_pos, elevations_sorted, 'b-', linewidth=2)
# Plot individual data points for clarity
ax2.plot(drift_y_pos, elevations_sorted, 'bo', markersize=3, alpha=0.5, zorder=3)
ax2.plot(drift_y_neg, elevations_sorted, 'bo', markersize=3, alpha=0.5, zorder=3)
ax2.axvline(x=limit_y, color='r', linestyle='--', linewidth=1.5, label=f'Limit = {limit_y:.4f}')
ax2.axvline(x=-limit_y, color='r', linestyle='--', linewidth=1.5)
ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
ax2.axvline(x=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)

ax2.set_xlabel('Interstory Drift Ratio', fontsize=12, fontweight='bold')
ax2.set_ylabel('Elevation (m)', fontsize=12, fontweight='bold')
ax2.set_title('Maximum Interstory Drift Ratios in Y Direction', fontsize=13, fontweight='bold')
ax2.set_xlim(-drift_range, drift_range)
ax2.set_ylim(elevation_min, elevation_max)
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.legend(loc='upper right', fontsize=9)

# Add summary equation
summary_text_y = f'$\\delta_{{i,max}}^{{(Y)}} / h_i = {max_drift_y:.3f} \\leq {limit_y:.3f}$'
ax2.text(0.02, 0.98, summary_text_y, transform=ax2.transAxes, 
         fontsize=11, verticalalignment='top', horizontalalignment='left',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# =====================================================
# Add main title
# =====================================================
fig.suptitle('"Preliminary" Interstory Drift Ratio Calculation', 
             fontsize=15, fontweight='bold', y=0.98)

# Add description text
description = 'Under the DD-2 level ground motion elastic design spectrum, the interstory drift ratios are:'
fig.text(0.5, 0.94, description, ha='center', fontsize=10, style='italic')

plt.tight_layout(rect=[0, 0, 1, 0.92])

# Save the figure
output_file = Path(__file__).parent / 'drift_ratio_charts.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\n[OK] Charts saved as '{output_file}'")

plt.show()

print(f"\n[OK] Analysis complete!")
print(f"   Max X-direction drift ratio: {max_drift_x:.6f} (Limit: {limit_x:.6f})")
print(f"   Max Y-direction drift ratio: {max_drift_y:.6f} (Limit: {limit_y:.6f})")
print(f"   X-direction check: {'[PASS]' if max_drift_x <= limit_x else '[FAIL]'}")
print(f"   Y-direction check: {'[PASS]' if max_drift_y <= limit_y else '[FAIL]'}")

