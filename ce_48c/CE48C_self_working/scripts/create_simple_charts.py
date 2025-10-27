import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file
df = pd.read_csv('dsi_2000_2020_final_cleaned.csv')

# Set up simple matplotlib style
plt.style.use('default')
plt.rcParams['figure.figsize'] = (8, 5)
plt.rcParams['font.size'] = 12

# Define month names in Turkish
months = ['Ekim', 'Kasım', 'Aralık', 'Ocak', 'Şubat', 'Mart', 
          'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül']

# Monthly columns mapping
monthly_columns = {
    'flow': ['flow_october_m3s', 'flow_november_m3s', 'flow_december_m3s', 
             'flow_january_m3s', 'flow_february_m3s', 'flow_march_m3s',
             'flow_april_m3s', 'flow_may_m3s', 'flow_june_m3s', 
             'flow_july_m3s', 'flow_august_m3s', 'flow_september_m3s'],
    'ltsnkm2': ['ltsnkm2_Ekim', 'ltsnkm2_Kasım', 'ltsnkm2_Aralık', 
                'ltsnkm2_Ocak', 'ltsnkm2_Şubat', 'ltsnkm2_Mart',
                'ltsnkm2_Nisan', 'ltsnkm2_Mayıs', 'ltsnkm2_Haziran', 
                'ltsnkm2_Temmuz', 'ltsnkm2_Ağustos', 'ltsnkm2_Eylül'],
    'mm_akim': ['mm_akim_Ekim', 'mm_akim_Kasım', 'mm_akim_Aralık', 
                'mm_akim_Ocak', 'mm_akim_Şubat', 'mm_akim_Mart',
                'mm_akim_Nisan', 'mm_akim_Mayıs', 'mm_akim_Haziran', 
                'mm_akim_Temmuz', 'mm_akim_Ağustos', 'mm_akim_Eylül'],
    'mil_m3': ['mil_m3_Ekim', 'mil_m3_Kasım', 'mil_m3_Aralık', 
               'mil_m3_Ocak', 'mil_m3_Şubat', 'mil_m3_Mart',
               'mil_m3_Nisan', 'mil_m3_Mayıs', 'mil_m3_Haziran', 
               'mil_m3_Temmuz', 'mil_m3_Ağustos', 'mil_m3_Eylül']
}

# Function to create simple monthly average charts
def create_simple_monthly_chart(data_type, title, ylabel, filename):
    plt.figure(figsize=(10, 6))
    
    # Calculate 20-year average for each month
    monthly_avg = []
    for col in monthly_columns[data_type]:
        if col in df.columns:
            avg_val = df[col].mean()
            monthly_avg.append(avg_val)
        else:
            monthly_avg.append(0)
    
    # Create simple bar chart
    bars = plt.bar(range(len(months)), monthly_avg, color='lightblue', edgecolor='black', linewidth=1)
    
    # Add simple value labels
    for i, val in enumerate(monthly_avg):
        plt.text(i, val + max(monthly_avg)*0.02, f'{val:.1f}', ha='center', va='bottom')
    
    plt.title(title, fontsize=14)
    plt.xlabel('Months')
    plt.ylabel(ylabel)
    plt.xticks(range(len(months)), months, rotation=45)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Created {filename}")

# Function to create simple annual average charts
def create_simple_annual_chart(column, title, ylabel, filename):
    plt.figure(figsize=(10, 6))
    
    # Get annual data
    years = df['year'].values
    values = df[column].values
    
    # Create simple line plot
    plt.plot(years, values, marker='o', linewidth=2, markersize=8, color='blue')
    
    # Add simple value labels
    for year, val in zip(years, values):
        plt.text(year, val + max(values)*0.02, f'{val:.1f}', ha='center', va='bottom')
    
    plt.title(title, fontsize=14)
    plt.xlabel('Year')
    plt.ylabel(ylabel)
    plt.xticks(years, rotation=45)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Created {filename}")

# Create simple monthly average charts
print("Creating simple monthly average charts...")
create_simple_monthly_chart('flow', 'Monthly Average Flow', 'Flow (m³/s)', 'chart1_flow_monthly_avg_simple.png')
create_simple_monthly_chart('ltsnkm2', 'Monthly Average Specific Flow', 'Specific Flow (L/s/km²)', 'chart2_ltsnkm2_monthly_avg_simple.png')
create_simple_monthly_chart('mm_akim', 'Monthly Average Runoff', 'Runoff (mm)', 'chart3_mm_akim_monthly_avg_simple.png')
create_simple_monthly_chart('mil_m3', 'Monthly Average Flow Volume', 'Flow Volume (million m³)', 'chart4_mil_m3_monthly_avg_simple.png')

# Create simple annual average charts
print("Creating simple annual average charts...")
create_simple_annual_chart('flow_avg_annual_m3s', 'Annual Average Flow', 'Flow (m³/s)', 'chart5_flow_annual_avg_simple.png')
create_simple_annual_chart('ltsnkm2_average', 'Annual Average Specific Flow', 'Specific Flow (L/s/km²)', 'chart6_ltsnkm2_annual_avg_simple.png')
create_simple_annual_chart('mm_akim_annual_average', 'Annual Average Runoff', 'Runoff (mm)', 'chart7_mm_akim_annual_avg_simple.png')
create_simple_annual_chart('mil_m3_annual_average', 'Annual Average Flow Volume', 'Flow Volume (million m³)', 'chart8_mil_m3_annual_avg_simple.png')

print("\nAll 8 simple charts have been created successfully!")
print("Simple chart files created:")
print("- chart1_flow_monthly_avg_simple.png")
print("- chart2_ltsnkm2_monthly_avg_simple.png") 
print("- chart3_mm_akim_monthly_avg_simple.png")
print("- chart4_mil_m3_monthly_avg_simple.png")
print("- chart5_flow_annual_avg_simple.png")
print("- chart6_ltsnkm2_annual_avg_simple.png")
print("- chart7_mm_akim_annual_avg_simple.png")
print("- chart8_mil_m3_annual_avg_simple.png")
