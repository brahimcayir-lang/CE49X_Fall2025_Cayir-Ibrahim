# CE 49X - Lab 2: Soil Test Data Analysis

# Student Name:İbrahim Çayır   
# Student ID: 2020403207  
# Date: 13.10.2025

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
        # Attempt to read the data from the CSV file specified by file_path.
        df = pd.read_csv(file_path)
        
        # If the file is read successfully, print a confirmation message.
        print("Data loaded successfully.")
        
        # Return the loaded DataFrame.
        return df

    except FileNotFoundError:
        # This block executes ONLY if the file is not found at the specified path.
        print(f"Error: File not found. Ensure the file exists at the specified path: {file_path}")
        
        # Return None to indicate that the data loading failed.
        return None

    except Exception as e:
        # This is a general "catch-all" for any other errors.
        print(f"An unexpected error occurred: {e}")
        return None
    
def clean_data(df):
    """
    Clean the dataset by handling missing values and removing outliers from 'soil_ph'.
    
    Parameters:
        df (pd.DataFrame): The raw DataFrame.
        
    Returns:
        pd.DataFrame: The cleaned DataFrame.
    """
    # Create a copy of the original DataFrame to avoid modifying it directly.
    # This is a good practice to prevent unintended side effects.
    df_cleaned = df.copy()
    
    # --- Step 1: Fill Missing Values ---
    print("Starting data cleaning process...")
    columns_to_clean = ['soil_ph', 'nitrogen', 'phosphorus', 'moisture']
    
    # Loop through each specified column to handle missing data.
    for col in columns_to_clean:
        # Check if the column has any missing (null) values. This is more efficient
        # than calculating the mean for columns that don't need cleaning.
        if df_cleaned[col].isnull().any():
            # Calculate the mean of the non-missing values in the column.
            mean_val = df_cleaned[col].mean()
            
            # Fill the missing values (NaN) with the calculated mean.
            # `inplace=True` modifies the df_cleaned DataFrame directly.
            df_cleaned[col].fillna(mean_val, inplace=True)
            
            # Print a message to confirm that missing values were filled.
            print(f"- Filled missing values in '{col}' with mean: {mean_val:.2f}")
    
    # --- Step 2: Remove Outliers from 'soil_ph' ---
    # Calculate the mean and standard deviation for the 'soil_ph' column.
    ph_mean = df_cleaned['soil_ph'].mean()
    ph_std = df_cleaned['soil_ph'].std()
    
    # Define the valid range: any value within 3 standard deviations of the mean.
    lower_bound = ph_mean - 3 * ph_std
    upper_bound = ph_mean + 3 * ph_std
    
    # Store the number of rows before removing outliers to track how many are removed.
    initial_rows = len(df_cleaned)
    
    # Filter the DataFrame, keeping only the rows where 'soil_ph' is within the valid range.
    # The '&' operator ensures both conditions (>= lower_bound and <= upper_bound) are met.
    df_cleaned = df_cleaned[(df_cleaned['soil_ph'] >= lower_bound) & (df_cleaned['soil_ph'] <= upper_bound)]
    
    # Get the number of rows after cleaning.
    final_rows = len(df_cleaned)
    
    # Print a summary of the outlier removal process, combining feedback from both snippets.
    print(f"- Removed {initial_rows - final_rows} outliers from 'soil_ph'.")
    print(f"- Kept 'soil_ph' values within the calculated range: [{lower_bound:.2f}, {upper_bound:.2f}].")
    
    # --- Step 3: Final Output ---
    # Display the first few rows of the cleaned DataFrame to verify the result.
    print("\nCleaned Data Head:")
    print(df_cleaned.head())
    
    # Return the fully cleaned DataFrame.
    return df_cleaned

def compute_statistics(df, column):
    """
    Compute and print descriptive statistics for the specified column.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        column (str): The name of the column for which to compute statistics.
    """
    # Check if the column exists in the DataFrame
    # Before performing calculations, check if the provided 'column' name actually exists in the DataFrame.
    # This is a safety check to prevent errors if a wrong column name is given.
    if column not in df.columns:
        # If the column is not found, print an error message and exit the function early.
        print(f"\nError: Column '{column}' not found in the DataFrame.")
        return

    # --- Statistical Calculations ---
    # These methods are called on the specific column (a pandas Series) of the DataFrame.

    # Calculate the smallest value in the column.
    min_val = df[column].min()
    
    # Calculate the largest value in the column.
    max_val = df[column].max()
    
    # Calculate the average value (the sum of values divided by the count of values).
    mean_val = df[column].mean()
    
    # Calculate the median (the middle value when the data is sorted).
    # This is often a better measure of center for skewed data.
    median_val = df[column].median()
    
    # Calculate the standard deviation, which measures the amount of variation or spread in the data.
    std_val = df[column].std()
    
    # --- Display Results ---
    # Print the calculated statistics in a formatted, easy-to-read block.
    # The ':.2f' formatting rounds the numbers to two decimal places.
    print(f"\nDescriptive statistics for '{column}':")
    print(f"  Minimum: {min_val:.2f}")
    print(f"  Maximum: {max_val:.2f}")
    print(f"  Mean: {mean_val:.2f}")
    print(f"  Median: {median_val:.2f}")
    print(f"  Standard Deviation: {std_val:.2f}")


def main():
    """ The main function to orchestrate the data loading, cleaning, and analysis process."""
# Define the location of the dataset.
# This variable holds the name of the CSV file to be loaded.
file_path = 'soil_test.csv'  # Update this path as needed

# Call the load_data function to read the CSV file into a pandas DataFrame.
# The result is stored in the 'df_raw' variable.
df_raw = load_data(file_path)

# This is a critical safety check. The program will only proceed if the DataFrame
# was loaded successfully (i.e., it's not None). This prevents errors if the file was not found.
if df_raw is not None:
    # Call the clean_data function to handle missing values and remove outliers.
    # The cleaned data is stored in a new DataFrame called 'df_clean'.
    df_clean = clean_data(df_raw)
    
    # --- Data Analysis ---
    # Call the compute_statistics function to calculate and display key stats
    # for the specified columns from the cleaned dataset.
    
    # Analyze the 'soil_ph' column.
    compute_statistics(df_clean, 'soil_ph')
    
    # Analyze other important columns.
    compute_statistics(df_clean, 'nitrogen')
    compute_statistics(df_clean, 'phosphorus')
    compute_statistics(df_clean, 'moisture')

# This is a standard Python construct. It serves as the entry point of the script.
# The code inside this block will only run when the script is executed directly,
# not when it's imported as a module into another script.
if __name__ == '__main__':
# Call the main function to start the program.
    main()

# =============================================================================
# REFLECTION QUESTIONS
# =============================================================================
# Answer these questions in comments below:

# 1. What was the most challenging part of this lab?
# Answer: # The most challenging aspect of this lab was translating the statistical concept
# of outlier removal into a functional line of code. While understanding the
# 3-standard-deviation rule was straightforward, implementing the correct
# boolean indexing syntax in pandas to filter the DataFrame required careful
# consideration and proved to be a critical learning experience.

# 2. How could soil data analysis help civil engineers in real projects?
# Answer: Soil data analysis is fundamental to civil engineering, providing essential
# insights for project safety, durability, and cost-effectiveness. It directly
# informs foundation design by quantifying the soil's bearing capacity and
# identifying chemical properties that could degrade materials. This data is also
# crucial for geotechnical assessments, such as analyzing slope stability based on
# moisture content, and for evaluating the corrosion risk to buried infrastructure.

# 3. What additional features would make this soil analysis tool more useful?
# Answer: The utility of this tool could be significantly enhanced by incorporating several
# features. The primary addition would be data visualization capabilities, allowing
# for the generation of histograms and scatter plots to intuitively interpret
# data distributions. Another valuable feature would be automated soil
# classification based on its properties (e.g., pH levels). Finally, a function
# to generate summary reports in a PDF format would streamline documentation.

# 4. How did error handling improve the robustness of your code?
# Answer: Error handling improved the script's robustness by making it resilient to
# common runtime problems, such as a missing input file. The try-except block
# prevents an uncontrolled crash and instead provides specific, user-friendly
# feedback. This "graceful failure" mechanism, combined with the conditional
# check that the DataFrame loaded successfully, prevents subsequent functions
# from executing on null data, thereby making the entire program more reliable.