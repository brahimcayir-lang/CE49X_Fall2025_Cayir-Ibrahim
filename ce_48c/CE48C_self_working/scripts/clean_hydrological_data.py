import pandas as pd
import numpy as np

def clean_hydrological_data(input_file, output_file):
    """
    Clean hydrological dataset by detecting and handling outliers using 2-sigma rule.
    
    Parameters:
    input_file (str): Path to input CSV file
    output_file (str): Path to output cleaned CSV file
    """
    
    # Read the dataset
    print("Reading dataset...")
    df = pd.read_csv(input_file)
    
    print(f"Original dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Identify numeric columns (excluding non-numeric columns)
    non_numeric_cols = ['file', 'page', 'year', 'station_code', 'station_name', 'coordinates']
    numeric_cols = [col for col in df.columns if col not in non_numeric_cols]
    
    print(f"\nNumeric columns to process: {len(numeric_cols)}")
    print(f"Numeric columns: {numeric_cols}")
    
    # Create a copy for cleaning
    df_cleaned = df.copy()
    
    # Store statistics for summary
    outlier_stats = {}
    before_after_stats = {}
    
    print("\nProcessing numeric columns...")
    
    for col in numeric_cols:
        print(f"\nProcessing column: {col}")
        
        # Convert to numeric, coercing errors to NaN
        df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
        
        # Calculate statistics before outlier removal
        original_mean = df_cleaned[col].mean()
        original_std = df_cleaned[col].std()
        
        # Identify outliers using 2-sigma rule
        lower_bound = original_mean - 2 * original_std
        upper_bound = original_mean + 2 * original_std
        
        # Count outliers
        outliers_mask = (df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)
        outlier_count = outliers_mask.sum()
        
        # Replace outliers with NaN, then fill with mean
        df_cleaned.loc[outliers_mask, col] = np.nan
        df_cleaned[col] = df_cleaned[col].fillna(original_mean)
        
        # Calculate statistics after cleaning
        cleaned_mean = df_cleaned[col].mean()
        
        # Store statistics
        outlier_stats[col] = outlier_count
        before_after_stats[col] = {
            'before_mean': original_mean,
            'after_mean': cleaned_mean,
            'std': original_std,
            'outliers': outlier_count
        }
        
        print(f"  - Outliers detected: {outlier_count}")
        print(f"  - Range: [{lower_bound:.3f}, {upper_bound:.3f}]")
        print(f"  - Mean before: {original_mean:.3f}, after: {cleaned_mean:.3f}")
    
    # Save cleaned dataset
    print(f"\nSaving cleaned dataset to {output_file}...")
    df_cleaned.to_csv(output_file, index=False)
    
    # Print summary
    print("\n" + "="*80)
    print("CLEANING SUMMARY")
    print("="*80)
    
    print(f"\nDataset saved as: {output_file}")
    print(f"Original shape: {df.shape}")
    print(f"Cleaned shape: {df_cleaned.shape}")
    
    print(f"\nOUTLIER DETECTION SUMMARY:")
    print("-" * 50)
    print(f"{'Column':<30} {'Outliers':<10} {'Before Mean':<12} {'After Mean':<12}")
    print("-" * 50)
    
    total_outliers = 0
    for col in numeric_cols:
        stats = before_after_stats[col]
        print(f"{col:<30} {stats['outliers']:<10} {stats['before_mean']:<12.3f} {stats['after_mean']:<12.3f}")
        total_outliers += stats['outliers']
    
    print("-" * 50)
    print(f"{'TOTAL OUTLIERS':<30} {total_outliers:<10}")
    
    print(f"\nDETAILED STATISTICS:")
    print("-" * 50)
    for col in numeric_cols:
        stats = before_after_stats[col]
        print(f"\n{col}:")
        print(f"  - Outliers detected: {stats['outliers']}")
        print(f"  - Standard deviation: {stats['std']:.3f}")
        print(f"  - Mean before cleaning: {stats['before_mean']:.3f}")
        print(f"  - Mean after cleaning: {stats['after_mean']:.3f}")
        print(f"  - Mean difference: {stats['after_mean'] - stats['before_mean']:.3f}")
    
    return df_cleaned, outlier_stats, before_after_stats

if __name__ == "__main__":
    # Clean the dataset
    cleaned_df, outliers, stats = clean_hydrological_data(
        'dsi_2000_2020_final.csv', 
        'dsi_2000_2020_final_cleaned.csv'
    )
    
    print("\nCleaning completed successfully!")
