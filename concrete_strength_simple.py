import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set random seed for reproducibility
np.random.seed(42)

# 1. Create time data from day 1 to 28
days = np.arange(1, 29)

# 2-5. Generate 3 concrete batches with different strength curves
# Batch A: 25 + 0.5*day + noise
batch_a_strength = 25 + 0.5 * days + np.random.normal(0, 0.8, len(days))

# Batch B: 27 + 0.4*day + noise  
batch_b_strength = 27 + 0.4 * days + np.random.normal(0, 0.6, len(days))

# Batch C: 23 + 0.6*day + noise
batch_c_strength = 23 + 0.6 * days + np.random.normal(0, 0.7, len(days))

# Create DataFrame for seaborn plotting
data = []
for i, day in enumerate(days):
    data.extend([
        {'Day': day, 'Batch': 'Batch A', 'Strength (MPa)': batch_a_strength[i]},
        {'Day': day, 'Batch': 'Batch B', 'Strength (MPa)': batch_b_strength[i]},
        {'Day': day, 'Batch': 'Batch C', 'Strength (MPa)': batch_c_strength[i]}
    ])

df = pd.DataFrame(data)

# 6. Use seaborn lineplot with confidence intervals
plt.figure(figsize=(12, 8))
sns.lineplot(data=df, x='Day', y='Strength (MPa)', hue='Batch', 
             ci=95, marker='o', markersize=6, linewidth=2.5)

# 7. Add proper labels and legend
plt.title('Concrete Strength Development Over Time\nChallenge 4: Construction Quality Control', 
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Days', fontsize=14, fontweight='bold')
plt.ylabel('Compressive Strength (MPa)', fontsize=14, fontweight='bold')
plt.legend(title='Concrete Batches', title_fontsize=12, fontsize=11, loc='lower right')
plt.grid(True, alpha=0.3, linestyle='--')
plt.xlim(0, 29)
plt.ylim(20, 45)

# Add threshold line
plt.axhline(y=30, color='red', linestyle=':', alpha=0.7, 
            label='Typical Strength Threshold (30 MPa)')

plt.tight_layout()
plt.show()

print("🎉 Challenge 4 Complete! Time series plot generated successfully!")
print("🏆 First team to show the time series plot wins Challenge 4!")

# Print summary
print(f"\nFinal strengths at Day 28:")
print(f"Batch A: {batch_a_strength[-1]:.2f} MPa")
print(f"Batch B: {batch_b_strength[-1]:.2f} MPa") 
print(f"Batch C: {batch_c_strength[-1]:.2f} MPa")
