# CE 49X - Lab 2: Soil Test Data Analysis

# Student Name: ________________  
# Student ID: ________________  
# Date: ________________

import pandas as pd
import numpy as np

def load_data(file_path):
    """
    Load the soil test dataset from a CSV file.
    
    Parameters:
        file_path (str): The path to the CSV file.
        
    Returns:
        pd.DataFrame: The loaded DataFrame, or None if the file is not found.
    """
    # TODO: Implement data loading with error handling
    try:
        df = pd.read_csv(file_path)
        print("Data loaded successfully.")
        return df
    except FileNotFoundError:
        print(f"Error: File not found. Ensure the file exists at the specified path: {file_path}")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def clean_data(df):
    """
    Clean the dataset by handling missing values and removing outliers from 'soil_ph'.
    
    For each column in ['soil_ph', 'nitrogen', 'phosphorus', 'moisture']:
    - Missing values are filled with the column mean.
    
    Additionally, remove outliers in 'soil_ph' that are more than 3 standard deviations from the mean.
    
    Parameters:
        df (pd.DataFrame): The raw DataFrame.
        
    Returns:
        pd.DataFrame: The cleaned DataFrame.
    """
    df_cleaned = df.copy()
    
    # TODO: Fill missing values in each specified column with the column mean
    for col in ['soil_ph', 'nitrogen', 'phosphorus', 'moisture']:
        if df_cleaned[col].isnull().any():
            mean_val = df_cleaned[col].mean()
            df_cleaned[col].fillna(mean_val, inplace=True)
            print(f"Filled missing values in '{col}' with mean value {mean_val:.2f}")
    
    # TODO: Remove outliers in 'soil_ph': values more than 3 standard deviations from the mean
    ph_mean = df_cleaned['soil_ph'].mean()
    ph_std = df_cleaned['soil_ph'].std()
    lower_bound = ph_mean - 3 * ph_std
    upper_bound = ph_mean + 3 * ph_std
    df_cleaned = df_cleaned[(df_cleaned['soil_ph'] >= lower_bound) & (df_cleaned['soil_ph'] <= upper_bound)]
    
    print(f"After cleaning, 'soil_ph' values are within the range [{lower_bound:.2f}, {upper_bound:.2f}].")
    print(df_cleaned.head())
    return df_cleaned

def compute_statistics(df, column):
    """
    Compute and print descriptive statistics for the specified column.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        column (str): The name of the column for which to compute statistics.
    """
    # TODO: Calculate minimum value
    min_val = df[column].min()
    
    # TODO: Calculate maximum value
    max_val = df[column].max()
    
    # TODO: Calculate mean value
    mean_val = df[column].mean()
    
    # TODO: Calculate median value
    median_val = df[column].median()
    
    # TODO: Calculate standard deviation
    std_val = df[column].std()
    
    print(f"\nDescriptive statistics for '{column}':")
    print(f"  Minimum: {min_val}")
    print(f"  Maximum: {max_val}")
    print(f"  Mean: {mean_val:.2f}")
    print(f"  Median: {median_val:.2f}")
    print(f"  Standard Deviation: {std_val:.2f}")

def main():
    # TODO: Update the file path to point to your soil_test.csv file
    file_path = 'soil_test.csv'  # Update this path as needed
    
    # TODO: Load the dataset using the load_data function
    df = load_data(file_path)
    if df is None:
        return
    
    # TODO: Clean the dataset using the clean_data function
    df_clean = clean_data(df)
    
    # TODO: Compute and display statistics for the 'soil_ph' column
    compute_statistics(df_clean, 'soil_ph')
    
    # TODO: (Optional) Compute statistics for other columns
    # compute_statistics(df_clean, 'nitrogen')
    # compute_statistics(df_clean, 'phosphorus')
    # compute_statistics(df_clean, 'moisture')
    
if __name__ == '__main__':
    main()

# =============================================================================
# REFLECTION QUESTIONS
# =============================================================================
# Answer these questions in comments below:

# 1. What was the most challenging part of this lab?
# Answer: 

# 2. How could soil data analysis help civil engineers in real projects?
# Answer: 

# 3. What additional features would make this soil analysis tool more useful?
# Answer: 

# 4. How did error handling improve the robustness of your code?
# Answer: 