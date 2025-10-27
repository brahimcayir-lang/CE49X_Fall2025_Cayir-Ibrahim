import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set seaborn style for professional appearance
sns.set_style("whitegrid")
sns.set_palette("husl")

# Set random seed for reproducible results
np.random.seed(42)

# Generate strength data for each material
# Steel: mean=50, std=5 MPa
steel_strength = np.random.normal(50, 5, 100)

# Concrete: mean=30, std=3 MPa
concrete_strength = np.random.normal(30, 3, 100)

# Composite: mean=40, std=4 MPa
composite_strength = np.random.normal(40, 4, 100)

# Create a DataFrame for easier plotting with seaborn
data = {
    'Material': ['Steel'] * 100 + ['Concrete'] * 100 + ['Composite'] * 100,
    'Strength (MPa)': list(steel_strength) + list(concrete_strength) + list(composite_strength)
}

df = pd.DataFrame(data)

# Create the boxplot
plt.figure(figsize=(14, 8))

# Create seaborn boxplot
box_plot = sns.boxplot(data=df, x='Material', y='Strength (MPa)', 
                       palette=['#E74C3C', '#3498DB', '#2ECC71'])

# Customize the plot
plt.title('Material Strength Comparison', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Material Type', fontsize=12, fontweight='bold')
plt.ylabel('Strength (MPa)', fontsize=12, fontweight='bold')

# Add grid for better readability
plt.grid(True, alpha=0.3, axis='y')

# Customize tick parameters
plt.tick_params(axis='both', which='major', labelsize=10)

# Calculate statistics for annotations
steel_mean = np.mean(steel_strength)
concrete_mean = np.mean(concrete_strength)
composite_mean = np.mean(composite_strength)

# Calculate quartiles, min, and max for each material
materials_stats = {
    'Steel': steel_strength,
    'Concrete': concrete_strength,
    'Composite': composite_strength
}

# Add detailed annotations for each material
for i, (material, data) in enumerate(materials_stats.items()):
    q25 = np.percentile(data, 25)
    q50 = np.percentile(data, 50)
    q75 = np.percentile(data, 75)
    min_val = np.min(data)
    max_val = np.max(data)
    mean_val = np.mean(data)
    
    # Position annotations to the right of each boxplot
    x_pos = i + 0.4
    
    # Mean annotation
    plt.text(x_pos, mean_val + 8, f'Mean: {mean_val:.1f}', 
             ha='left', va='center', fontsize=9, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.2", facecolor="lightblue", alpha=0.7))
    
    # Quartile annotations
    plt.text(x_pos, q75 + 2, f'Q3: {q75:.1f}', 
             ha='left', va='bottom', fontsize=8, color='darkgreen',
             bbox=dict(boxstyle="round,pad=0.1", facecolor="lightgreen", alpha=0.6))
    
    plt.text(x_pos, q50, f'Q2: {q50:.1f}', 
             ha='left', va='center', fontsize=8, color='darkblue',
             bbox=dict(boxstyle="round,pad=0.1", facecolor="lightcyan", alpha=0.6))
    
    plt.text(x_pos, q25 - 2, f'Q1: {q25:.1f}', 
             ha='left', va='top', fontsize=8, color='darkred',
             bbox=dict(boxstyle="round,pad=0.1", facecolor="lightcoral", alpha=0.6))
    
    # Min and Max annotations
    plt.text(x_pos, max_val + 1, f'Max: {max_val:.1f}', 
             ha='left', va='bottom', fontsize=8, color='purple',
             bbox=dict(boxstyle="round,pad=0.1", facecolor="plum", alpha=0.6))
    
    plt.text(x_pos, min_val - 1, f'Min: {min_val:.1f}', 
             ha='left', va='top', fontsize=8, color='orange',
             bbox=dict(boxstyle="round,pad=0.1", facecolor="moccasin", alpha=0.6))

# Adjust layout
plt.tight_layout()

# Display the plot
plt.show()

# Print summary statistics
print("\nMaterial Strength Summary Statistics:")
print("=" * 50)
print(f"Steel:     Mean = {steel_mean:.2f} MPa, Std = {np.std(steel_strength):.2f} MPa")
print(f"Concrete:  Mean = {concrete_mean:.2f} MPa, Std = {np.std(concrete_strength):.2f} MPa")
print(f"Composite: Mean = {composite_mean:.2f} MPa, Std = {np.std(composite_strength):.2f} MPa")

# Calculate and display quartile values
print("\nQuartile Values:")
print("=" * 30)
materials_data = {
    'Steel': steel_strength,
    'Concrete': concrete_strength,
    'Composite': composite_strength
}

for material, data in materials_data.items():
    q25 = np.percentile(data, 25)
    q50 = np.percentile(data, 50)  # Median
    q75 = np.percentile(data, 75)
    print(f"{material}:")
    print(f"  Q1 (25th percentile): {q25:.2f} MPa")
    print(f"  Q2 (50th percentile/Median): {q50:.2f} MPa")
    print(f"  Q3 (75th percentile): {q75:.2f} MPa")
    print(f"  IQR (Q3-Q1): {q75-q25:.2f} MPa")
    print()

# Additional analysis
print(f"\nStrength Ranking (by mean):")
print("=" * 30)
materials = ['Steel', 'Concrete', 'Composite']
means = [steel_mean, concrete_mean, composite_mean]
sorted_materials = sorted(zip(materials, means), key=lambda x: x[1], reverse=True)

for i, (material, mean) in enumerate(sorted_materials, 1):
    print(f"{i}. {material}: {mean:.2f} MPa")
