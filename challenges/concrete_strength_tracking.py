import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# TASK: Track concrete strength development over time
# Requirements:
# 1. Create time data from day 1 to 28
# 2. Generate 3 concrete batches with different strength curves
# 3. Batch A: 25 + 0.5*day + noise
# 4. Batch B: 27 + 0.4*day + noise
# 5. Batch C: 23 + 0.6*day + noise
# 6. Use seaborn lineplot with confidence intervals
# 7. Add proper labels and legend

def generate_concrete_strength_data():
    """
    Generate concrete strength development data for 3 batches over 28 days
    """
    # 1. Create time data from day 1 to 28
    days = np.arange(1, 29)  # Day 1 to 28
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # 2-5. Generate 3 concrete batches with different strength curves
    # Batch A: 25 + 0.5*day + noise
    batch_a_base = 25 + 0.5 * days
    batch_a_noise = np.random.normal(0, 0.8, len(days))  # Gaussian noise
    batch_a_strength = batch_a_base + batch_a_noise
    
    # Batch B: 27 + 0.4*day + noise
    batch_b_base = 27 + 0.4 * days
    batch_b_noise = np.random.normal(0, 0.6, len(days))  # Gaussian noise
    batch_b_strength = batch_b_base + batch_b_noise
    
    # Batch C: 23 + 0.6*day + noise
    batch_c_base = 23 + 0.6 * days
    batch_c_noise = np.random.normal(0, 0.7, len(days))  # Gaussian noise
    batch_c_strength = batch_c_base + batch_c_noise
    
    # Create DataFrame for easier plotting
    data = []
    for i, day in enumerate(days):
        data.extend([
            {'Day': day, 'Batch': 'Batch A', 'Strength (MPa)': batch_a_strength[i]},
            {'Day': day, 'Batch': 'Batch B', 'Strength (MPa)': batch_b_strength[i]},
            {'Day': day, 'Batch': 'Batch C', 'Strength (MPa)': batch_c_strength[i]}
        ])
    
    df = pd.DataFrame(data)
    return df, days, batch_a_strength, batch_b_strength, batch_c_strength

def create_strength_development_plot():
    """
    Create seaborn lineplot with confidence intervals for concrete strength development
    """
    # Generate data
    df, days, batch_a, batch_b, batch_c = generate_concrete_strength_data()
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # 6. Use seaborn lineplot with confidence intervals
    sns.lineplot(data=df, x='Day', y='Strength (MPa)', hue='Batch', 
                 ci=95,  # 95% confidence interval
                 marker='o', 
                 markersize=6,
                 linewidth=2.5)
    
    # 7. Add proper labels and legend
    plt.title('Concrete Strength Development Over Time\nChallenge 4: Construction Quality Control', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Days', fontsize=14, fontweight='bold')
    plt.ylabel('Compressive Strength (MPa)', fontsize=14, fontweight='bold')
    
    # Customize legend
    plt.legend(title='Concrete Batches', 
               title_fontsize=12, 
               fontsize=11,
               loc='lower right',
               frameon=True,
               fancybox=True,
               shadow=True)
    
    # Add grid for better readability
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Set axis limits and ticks
    plt.xlim(0, 29)
    plt.xticks(range(0, 29, 3))  # Show every 3rd day
    plt.ylim(20, 45)
    
    # Add horizontal line for typical concrete strength threshold
    plt.axhline(y=30, color='red', linestyle=':', alpha=0.7, 
                label='Typical Strength Threshold (30 MPa)')
    
    # Add annotations for final strengths
    final_day = 28
    plt.annotate(f'Batch A: {batch_a[-1]:.1f} MPa', 
                xy=(final_day, batch_a[-1]), 
                xytext=(final_day+1, batch_a[-1]+1),
                arrowprops=dict(arrowstyle='->', color='blue', alpha=0.7),
                fontsize=10, fontweight='bold')
    
    plt.annotate(f'Batch B: {batch_b[-1]:.1f} MPa', 
                xy=(final_day, batch_b[-1]), 
                xytext=(final_day+1, batch_b[-1]-1),
                arrowprops=dict(arrowstyle='->', color='orange', alpha=0.7),
                fontsize=10, fontweight='bold')
    
    plt.annotate(f'Batch C: {batch_c[-1]:.1f} MPa', 
                xy=(final_day, batch_c[-1]), 
                xytext=(final_day+1, batch_c[-1]+1),
                arrowprops=dict(arrowstyle='->', color='green', alpha=0.7),
                fontsize=10, fontweight='bold')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    return plt

def print_strength_summary():
    """
    Print summary statistics for each batch
    """
    df, days, batch_a, batch_b, batch_c = generate_concrete_strength_data()
    
    print("=" * 60)
    print("CONCRETE STRENGTH DEVELOPMENT SUMMARY")
    print("=" * 60)
    print(f"{'Batch':<10} {'Initial (Day 1)':<15} {'Final (Day 28)':<15} {'Avg Growth/Day':<15}")
    print("-" * 60)
    print(f"{'Batch A':<10} {batch_a[0]:<15.2f} {batch_a[-1]:<15.2f} {0.5:<15.2f}")
    print(f"{'Batch B':<10} {batch_b[0]:<15.2f} {batch_b[-1]:<15.2f} {0.4:<15.2f}")
    print(f"{'Batch C':<10} {batch_c[0]:<15.2f} {batch_c[-1]:<15.2f} {0.6:<15.2f}")
    print("=" * 60)
    
    # Find which batch reaches 30 MPa first
    threshold = 30
    batch_a_day = next((i+1 for i, val in enumerate(batch_a) if val >= threshold), None)
    batch_b_day = next((i+1 for i, val in enumerate(batch_b) if val >= threshold), None)
    batch_c_day = next((i+1 for i, val in enumerate(batch_c) if val >= threshold), None)
    
    print(f"\nDays to reach {threshold} MPa threshold:")
    print(f"Batch A: Day {batch_a_day if batch_a_day else 'Not reached'}")
    print(f"Batch B: Day {batch_b_day if batch_b_day else 'Not reached'}")
    print(f"Batch C: Day {batch_c_day if batch_c_day else 'Not reached'}")

if __name__ == "__main__":
    # Generate and display the plot
    plot = create_strength_development_plot()
    
    # Print summary statistics
    print_strength_summary()
    
    # Show the plot
    plt.show()
    
    print("\n🎉 Challenge 4 Complete! Time series plot generated successfully!")
    print("🏆 First team to show the time series plot wins Challenge 4!")
