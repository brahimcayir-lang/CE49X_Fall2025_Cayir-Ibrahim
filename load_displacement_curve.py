import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set seaborn style for professional appearance
sns.set_style("whitegrid")
sns.set_palette("husl")

# Generate displacement data from 0 to 10 mm
displacement = np.linspace(0, 10, 100)  # 100 points for smooth curve

# Calculate load using the given formula: load = 50 * displacement - 2 * displacement^2
load = 50 * displacement - 2 * displacement**2

# Create the plot
plt.figure(figsize=(10, 6))

# Plot the main curve
plt.plot(displacement, load, linewidth=2.5, color='#2E86AB', label='Load-Displacement Curve')

# Mark the yield point at displacement=5mm
yield_displacement = 5
yield_load = 50 * yield_displacement - 2 * yield_displacement**2
plt.plot(yield_displacement, yield_load, 'ro', markersize=10, label=f'Yield Point ({yield_displacement} mm)')

# Add a vertical line at the yield point
plt.axvline(x=yield_displacement, color='red', linestyle='--', alpha=0.7, linewidth=1)

# Customize the plot
plt.xlabel('Displacement (mm)', fontsize=12, fontweight='bold')
plt.ylabel('Load (N)', fontsize=12, fontweight='bold')
plt.title('Load-Displacement Curve', fontsize=16, fontweight='bold', pad=20)

# Add grid
plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

# Add legend
plt.legend(fontsize=11, loc='upper right')

# Set axis limits for better visualization
plt.xlim(0, 10)
plt.ylim(0, max(load) * 1.1)

# Add some styling touches
plt.tick_params(axis='both', which='major', labelsize=10)
plt.tight_layout()

# Display the plot
plt.show()

# Print some key information
print(f"Maximum load: {max(load):.2f} N at displacement: {displacement[np.argmax(load)]:.2f} mm")
print(f"Yield point: {yield_load:.2f} N at displacement: {yield_displacement} mm")


