import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set seaborn style for professional appearance
sns.set_style("whitegrid")
sns.set_palette("husl")

# Set random seed for reproducible results
np.random.seed(42)

# Generate depth data from 0 to 20 meters
depths = np.linspace(0, 20, 100)

# Create soil types
soil_types = ['Clay', 'Sand', 'Silt']

# Initialize lists to store data
all_depths = []
all_shear_strengths = []
all_soil_types = []

# Generate data for each soil type
for soil_type in soil_types:
    # Base shear strength formula: 20 + 2*depth + noise
    base_strength = 20 + 2 * depths
    
    # Add soil-specific adjustments
    if soil_type == 'Clay':
        soil_adjustment = 10  # Clay +10
    elif soil_type == 'Sand':
        soil_adjustment = -5  # Sand -5
    else:  # Silt
        soil_adjustment = 0   # Silt +0
    
    # Add noise (random variation)
    noise = np.random.normal(0, 3, len(depths))  # Standard deviation of 3
    
    # Calculate final shear strength
    shear_strength = base_strength + soil_adjustment + noise
    
    # Store data
    all_depths.extend(depths)
    all_shear_strengths.extend(shear_strength)
    all_soil_types.extend([soil_type] * len(depths))

# Create DataFrame
df = pd.DataFrame({
    'Depth (m)': all_depths,
    'Shear_Strength (kPa)': all_shear_strengths,
    'Soil_Type': all_soil_types
})

# Create the regression plot using seaborn lmplot
plt.figure(figsize=(12, 8))

# Use lmplot with hue for different soil types
g = sns.lmplot(data=df, x='Depth (m)', y='Shear_Strength (kPa)', 
                hue='Soil_Type', height=8, aspect=1.5,
                palette=['#E74C3C', '#3498DB', '#2ECC71'],  # Red, Blue, Green
                scatter_kws={'s': 60, 'alpha': 0.7},  # Larger, semi-transparent points
                line_kws={'linewidth': 3})  # Thicker regression lines

# Customize the plot
g.set_axis_labels('Depth (m)', 'Shear Strength (kPa)', fontsize=12, fontweight='bold')
g.fig.suptitle('Soil Shear Strength vs Depth Analysis', fontsize=16, fontweight='bold', y=0.95)

# Add grid
plt.grid(True, alpha=0.3)

# Customize legend
plt.legend(title='Soil Type', title_fontsize=12, fontsize=11, 
           loc='upper left', frameon=True, fancybox=True, shadow=True)

# Add some statistics annotations
print("\nSoil Analysis Regression Results:")
print("=" * 50)

for soil_type in soil_types:
    soil_data = df[df['Soil_Type'] == soil_type]
    
    # Calculate regression coefficients manually for verification
    x = soil_data['Depth (m)'].values
    y = soil_data['Shear_Strength (kPa)'].values
    
    # Simple linear regression: y = mx + b
    n = len(x)
    slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
    intercept = (np.sum(y) - slope * np.sum(x)) / n
    
    # Calculate R-squared
    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    
    print(f"{soil_type}:")
    print(f"  Regression equation: Shear Strength = {slope:.2f} × Depth + {intercept:.2f}")
    print(f"  R² = {r_squared:.3f}")
    print(f"  Expected slope ≈ 2.0 (actual: {slope:.2f})")
    print()

# Add equation annotations on the plot
equations = []
for soil_type in soil_types:
    soil_data = df[df['Soil_Type'] == soil_type]
    x = soil_data['Depth (m)'].values
    y = soil_data['Shear_Strength (kPa)'].values
    
    n = len(x)
    slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
    intercept = (np.sum(y) - slope * np.sum(x)) / n
    
    equations.append(f"{soil_type}: y = {slope:.1f}x + {intercept:.1f}")

# Add equation text box
equation_text = "\n".join(equations)
plt.text(0.02, 0.98, equation_text, transform=plt.gca().transAxes, 
         fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8))

plt.tight_layout()
plt.show()

print("🎉 Challenge 3 Complete! Regression plot showing soil shear strength vs depth!")
print("🏆 First team to show the regression plot wins Challenge 3!")
