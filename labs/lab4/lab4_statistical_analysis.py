"""
Lab 4: Statistical Analysis
Descriptive Statistics and Probability Distributions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import norm, binom, poisson, uniform, expon
import os
from pathlib import Path

# Set style for better plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


def load_data(file_path):
    """
    Load dataset from CSV file in root-level datasets/ folder.
    
    Args:
        file_path: Name of the CSV file (e.g., 'concrete_strength.csv')
        
    Returns:
        pandas.DataFrame: Loaded dataset
    """
    # Get the root directory (two levels up from labs/lab4/)
    current_dir = Path(__file__).parent
    root_dir = current_dir.parent.parent
    datasets_dir = root_dir / 'datasets'
    full_path = datasets_dir / file_path
    
    try:
        data = pd.read_csv(full_path)
        print(f"Successfully loaded {file_path}")
        print(f"Shape: {data.shape}")
        return data
    except FileNotFoundError:
        print(f"Error: File {full_path} not found")
        raise
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        raise


def calculate_descriptive_stats(data, column='strength_mpa'):
    """
    Calculate all descriptive statistics.
    
    Args:
        data: pandas.DataFrame
        column: str, column name to analyze
        
    Returns:
        dict: Dictionary containing all descriptive statistics
    """
    values = data[column].dropna()
    
    stats_dict = {
        'count': len(values),
        'mean': np.mean(values),
        'median': np.median(values),
        'mode': stats.mode(values, keepdims=True)[0][0],
        'std': np.std(values, ddof=1),
        'variance': np.var(values, ddof=1),
        'min': np.min(values),
        'max': np.max(values),
        'range': np.max(values) - np.min(values),
        'q1': np.percentile(values, 25),
        'q2': np.median(values),
        'q3': np.percentile(values, 75),
        'iqr': np.percentile(values, 75) - np.percentile(values, 25),
        'skewness': stats.skew(values),
        'kurtosis': stats.kurtosis(values)
    }
    
    return stats_dict


def plot_distribution(data, column, title, save_path=None):
    """
    Create a two-panel visualization (histogram + boxplot) that highlights
    descriptive statistics for a single numerical column.
    
    Args:
        data: pandas.DataFrame
        column: str, column name to plot
        title: str, plot title
        save_path: str, optional path to save figure
    """
    # ------------------------------------------------------------------
    # PREPARE CORE STATISTICS USED THROUGHOUT THE VISUALIZATION
    # ------------------------------------------------------------------
    values = data[column].dropna()
    mean_val = np.mean(values)
    median_val = np.median(values)
    mode_val = stats.mode(values, keepdims=True)[0][0]
    std_val = np.std(values, ddof=1)
    summary_stats = calculate_descriptive_stats(data, column)
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Histogram with normal curve overlay
    axes[0].hist(values, bins=30, density=True, alpha=0.7, color='steelblue', edgecolor='black')
    
    # Fit normal distribution
    x = np.linspace(values.min(), values.max(), 100)
    normal_curve = norm.pdf(x, mean_val, std_val)
    axes[0].plot(x, normal_curve, 'r-', linewidth=2, label='Normal Distribution')
    
    # Mark statistics
    axes[0].axvline(mean_val, color='green', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
    axes[0].axvline(median_val, color='orange', linestyle='--', linewidth=2, label=f'Median: {median_val:.2f}')
    axes[0].axvline(mode_val, color='purple', linestyle='--', linewidth=2, label=f'Mode: {mode_val:.2f}')
    
    # Mark standard deviations
    for i, sigma in enumerate([1, 2, 3], 1):
        axes[0].axvline(mean_val + sigma * std_val, color='red', linestyle=':', alpha=0.5, linewidth=1)
        axes[0].axvline(mean_val - sigma * std_val, color='red', linestyle=':', alpha=0.5, linewidth=1)
    
    axes[0].set_xlabel(column.replace('_', ' ').title())
    axes[0].set_ylabel('Density')
    axes[0].set_title(f'{title} - Histogram with Normal Curve')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Add a numerical summary box directly on the histogram
    hist_text = (
        f"Mean: {mean_val:.2f}\n"
        f"Median: {median_val:.2f}\n"
        f"Mode: {mode_val:.2f}\n"
        f"Std Dev: {std_val:.2f}"
    )
    axes[0].text(
        0.98, 0.95, hist_text,
        transform=axes[0].transAxes,
        ha='right', va='top',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.75)
    )
    
    # Boxplot
    axes[1].boxplot(values, vert=True, patch_artist=True,
                    boxprops=dict(facecolor='lightblue', alpha=0.7),
                    medianprops=dict(color='red', linewidth=2),
                    whiskerprops=dict(color='black', linewidth=1.5),
                    capprops=dict(color='black', linewidth=1.5))
    axes[1].set_ylabel(column.replace('_', ' ').title())
    axes[1].set_title(f'{title} - Boxplot')
    axes[1].grid(True, alpha=0.3)
    
    # Display quartile information next to the boxplot for quick reference
    box_text = (
        f"Q1: {summary_stats['q1']:.2f}\n"
        f"Median: {summary_stats['median']:.2f}\n"
        f"Q3: {summary_stats['q3']:.2f}\n"
        f"IQR: {summary_stats['iqr']:.2f}"
    )
    axes[1].text(
        1.08, 0.95, box_text,
        transform=axes[1].transAxes,
        ha='left', va='top',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.75)
    )
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    plt.show()


def fit_distribution(data, column, distribution_type='normal'):
    """
    Fit probability distribution to data.
    
    Args:
        data: pandas.DataFrame
        column: str, column name
        distribution_type: str, type of distribution to fit ('normal', 'exponential', etc.)
        
    Returns:
        tuple: Fitted distribution parameters and distribution object
    """
    values = data[column].dropna()
    
    if distribution_type == 'normal':
        # Fit normal distribution
        mean_fit, std_fit = norm.fit(values)
        fitted_dist = norm(loc=mean_fit, scale=std_fit)
        params = {'mean': mean_fit, 'std': std_fit}
        
    elif distribution_type == 'exponential':
        # Fit exponential distribution
        loc, scale = expon.fit(values)
        fitted_dist = expon(loc=loc, scale=scale)
        params = {'loc': loc, 'scale': scale, 'mean': scale}
        
    else:
        raise ValueError(f"Distribution type {distribution_type} not supported")
    
    return params, fitted_dist


def calculate_probability_binomial(n, p, k):
    """
    Calculate binomial probabilities.
    
    Args:
        n: int, number of trials
        p: float, probability of success
        k: int or array, number of successes
        
    Returns:
        dict: Dictionary with probability results
    """
    if isinstance(k, (int, np.integer)):
        k = [k]
    
    results = {}
    for k_val in k:
        prob_exact = binom.pmf(k_val, n, p)
        prob_at_most = binom.cdf(k_val, n, p)
        prob_at_least = 1 - binom.cdf(k_val - 1, n, p)
        results[k_val] = {
            'exact': prob_exact,
            'at_most': prob_at_most,
            'at_least': prob_at_least
        }
    
    mean_binom = n * p
    var_binom = n * p * (1 - p)
    
    results['distribution'] = {
        'mean': mean_binom,
        'variance': var_binom,
        'std': np.sqrt(var_binom)
    }
    
    return results


def calculate_probability_normal(mean, std, x_lower=None, x_upper=None):
    """
    Calculate normal probabilities.
    
    Args:
        mean: float, mean of normal distribution
        std: float, standard deviation
        x_lower: float, lower bound (None for -infinity)
        x_upper: float, upper bound (None for +infinity)
        
    Returns:
        dict: Probability results
    """
    dist = norm(loc=mean, scale=std)
    
    if x_lower is None and x_upper is None:
        raise ValueError("At least one bound must be specified")
    
    if x_lower is None:
        prob = dist.cdf(x_upper)
        description = f"P(X <= {x_upper:.2f})"
    elif x_upper is None:
        prob = 1 - dist.cdf(x_lower)
        description = f"P(X >= {x_lower:.2f})"
    else:
        prob = dist.cdf(x_upper) - dist.cdf(x_lower)
        description = f"P({x_lower:.2f} <= X <= {x_upper:.2f})"
    
    percentile_95 = dist.ppf(0.95)
    
    return {
        'probability': prob,
        'description': description,
        'percentile_95': percentile_95,
        'mean': mean,
        'std': std
    }


def calculate_probability_poisson(lambda_param, k):
    """
    Calculate Poisson probabilities.
    
    Args:
        lambda_param: float, rate parameter
        k: int or array, number of events
        
    Returns:
        dict: Probability results
    """
    if isinstance(k, (int, np.integer)):
        k = [k]
    
    results = {}
    for k_val in k:
        prob_exact = poisson.pmf(k_val, lambda_param)
        prob_at_most = poisson.cdf(k_val, lambda_param)
        prob_more_than = 1 - poisson.cdf(k_val, lambda_param)
        results[k_val] = {
            'exact': prob_exact,
            'at_most': prob_at_most,
            'more_than': prob_more_than
        }
    
    results['distribution'] = {
        'mean': lambda_param,
        'variance': lambda_param,
        'std': np.sqrt(lambda_param)
    }
    
    return results


def calculate_probability_exponential(mean, x):
    """
    Calculate exponential probabilities.
    
    Args:
        mean: float, mean of exponential distribution
        x: float or array, time values
        
    Returns:
        dict: Probability results
    """
    if isinstance(x, (int, float)):
        x = [x]
    
    # Exponential distribution: scale parameter = mean
    dist = expon(scale=mean)
    
    results = {}
    for x_val in x:
        prob_before = dist.cdf(x_val)
        prob_after = 1 - dist.cdf(x_val)
        results[x_val] = {
            'before': prob_before,
            'after': prob_after
        }
    
    results['distribution'] = {
        'mean': mean,
        'variance': mean**2,
        'std': mean
    }
    
    return results


def apply_bayes_theorem(prior, sensitivity, specificity):
    """
    Apply Bayes' theorem for diagnostic test scenario.
    
    Args:
        prior: float, prior probability (base rate)
        sensitivity: float, true positive rate (P(test+|disease+))
        specificity: float, true negative rate (P(test-|disease-))
        
    Returns:
        dict: Results including posterior probability and probability tree
    """
    # Calculate probabilities
    p_disease = prior
    p_no_disease = 1 - prior
    
    # Conditional probabilities
    p_test_pos_given_disease = sensitivity
    p_test_neg_given_disease = 1 - sensitivity
    p_test_neg_given_no_disease = specificity
    p_test_pos_given_no_disease = 1 - specificity
    
    # Joint probabilities
    p_test_pos_and_disease = p_disease * p_test_pos_given_disease
    p_test_pos_and_no_disease = p_no_disease * p_test_pos_given_no_disease
    p_test_neg_and_disease = p_disease * p_test_neg_given_disease
    p_test_neg_and_no_disease = p_no_disease * p_test_neg_given_no_disease
    
    # Marginal probability of positive test
    p_test_pos = p_test_pos_and_disease + p_test_pos_and_no_disease
    
    # Posterior probability using Bayes' theorem
    p_disease_given_test_pos = p_test_pos_and_disease / p_test_pos if p_test_pos > 0 else 0
    
    results = {
        'prior': p_disease,
        'sensitivity': sensitivity,
        'specificity': specificity,
        'p_test_positive': p_test_pos,
        'posterior': p_disease_given_test_pos,
        'probability_tree': {
            'p_disease': p_disease,
            'p_no_disease': p_no_disease,
            'p_test_pos_given_disease': p_test_pos_given_disease,
            'p_test_pos_given_no_disease': p_test_pos_given_no_disease,
            'p_test_neg_given_disease': p_test_neg_given_disease,
            'p_test_neg_given_no_disease': p_test_neg_given_no_disease,
            'p_test_pos_and_disease': p_test_pos_and_disease,
            'p_test_pos_and_no_disease': p_test_pos_and_no_disease
        }
    }
    
    return results


def plot_material_comparison(data, column, group_column, save_path=None):
    """
    Compare the distribution of a numerical metric across categorical groups
    using both boxplots and violin plots, with annotated summary statistics.
    
    Args:
        data: pandas.DataFrame
        column: str, column name to compare
        group_column: str, column name for grouping
        save_path: str, optional path to save figure
    """
    # ------------------------------------------------------------------
    # PRE-COMPUTE GROUPED STATISTICS TO REUSE FOR BOTH SUBPLOTS
    # ------------------------------------------------------------------
    grouped_stats = {
        group: calculate_descriptive_stats(subset, column)
        for group, subset in data.groupby(group_column)
    }
    groups = list(grouped_stats.keys())
    
    # Larger figure size for improved readability while keeping minimalist layout
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))
    plt.subplots_adjust(wspace=0.3)
    
    # Boxplot
    data.boxplot(column=column, by=group_column, ax=axes[0], patch_artist=True)
    axes[0].set_title(
        f'{column.replace("_", " ").title()} by {group_column.replace("_", " ").title()}',
        fontweight='bold',
        fontsize=16
    )
    axes[0].set_xlabel(group_column.replace('_', ' ').title())
    axes[0].set_ylabel(column.replace('_', ' ').title())
    axes[0].tick_params(labelsize=11)
    axes[0].grid(True, alpha=0.3)
    
    # Annotate key descriptive statistics directly on top of each box
    for idx, group in enumerate(groups, start=1):
        stats_group = grouped_stats[group]
        axes[0].annotate(
            f"Median: {stats_group['median']:.2f}\nIQR: {stats_group['iqr']:.2f}",
            xy=(idx, stats_group['median']),
            xytext=(0, 24),
            textcoords='offset points',
            ha='center',
            va='bottom',
            fontsize=11,
            fontweight='semibold',
            arrowprops=dict(arrowstyle='-', linewidth=0.8, color='black', shrinkA=0, shrinkB=5)
        )
    
    # Violin plot for better distribution visualization
    plot_data = [data[data[group_column] == group][column].values for group in groups]
    
    parts = axes[1].violinplot(plot_data, positions=range(len(groups)), showmeans=True, showmedians=True)
    axes[1].set_xticks(range(len(groups)))
    axes[1].set_xticklabels(groups)
    axes[1].set_ylabel(column.replace('_', ' ').title())
    axes[1].set_title(
        f'{column.replace("_", " ").title()} Distribution by {group_column.replace("_", " ").title()}',
        fontweight='bold',
        fontsize=16
    )
    axes[1].tick_params(labelsize=11)
    axes[1].grid(True, alpha=0.3)
    
    # Add means and standard deviations next to each violin for quick comparison
    for idx, group in enumerate(groups):
        stats_group = grouped_stats[group]
        axes[1].annotate(
            f"Mean: {stats_group['mean']:.2f}\nStd: {stats_group['std']:.2f}",
            xy=(idx, stats_group['mean']),
            xytext=(0, 24),
            textcoords='offset points',
            ha='center',
            va='bottom',
            fontsize=11,
            fontweight='semibold',
            arrowprops=dict(arrowstyle='-', linewidth=0.8, color='black', shrinkA=0, shrinkB=5)
        )
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    plt.show()


def plot_distribution_fitting(data, column, fitted_dist=None, save_path=None):
    """
    Visualize a fitted distribution alongside empirical data and provide
    numerical comparisons between real and synthetic samples.
    
    Args:
        data: pandas.DataFrame
        column: str, column name
        fitted_dist: scipy.stats distribution object
        save_path: str, optional path to save figure
    """
    # ------------------------------------------------------------------
    # PREPARE BOTH REAL AND SYNTHETIC DATASETS FOR VISUAL AND NUMERIC COMPARISON
    # ------------------------------------------------------------------
    values = data[column].dropna()
    
    if fitted_dist is None:
        # Fit normal distribution
        mean_fit, std_fit = norm.fit(values)
        fitted_dist = norm(loc=mean_fit, scale=std_fit)
    
    # Generate synthetic data
    n_samples = len(values)
    synthetic_data = fitted_dist.rvs(size=n_samples)
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Overlay histogram with fitted distribution
    axes[0].hist(values, bins=30, density=True, alpha=0.7, color='steelblue', 
                 label='Real Data', edgecolor='black')
    
    x = np.linspace(values.min(), values.max(), 100)
    pdf = fitted_dist.pdf(x)
    axes[0].plot(x, pdf, 'r-', linewidth=2, label='Fitted Distribution')
    
    axes[0].set_xlabel(column.replace('_', ' ').title())
    axes[0].set_ylabel('Density')
    axes[0].set_title('Real Data vs Fitted Distribution')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[0].text(
        0.02, 0.98,
        f"Fitted Mean: {fitted_dist.mean():.2f}\nFitted Std: {fitted_dist.std():.2f}",
        transform=axes[0].transAxes,
        ha='left', va='top',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8)
    )
    
    # Compare real vs synthetic data
    axes[1].hist(values, bins=30, density=True, alpha=0.5, color='steelblue', 
                 label='Real Data', edgecolor='black')
    axes[1].hist(synthetic_data, bins=30, density=True, alpha=0.5, color='red', 
                 label='Synthetic Data', edgecolor='black')
    
    axes[1].set_xlabel(column.replace('_', ' ').title())
    axes[1].set_ylabel('Density')
    axes[1].set_title('Real Data vs Synthetic Data')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].text(
        0.98, 0.98,
        f"Real Mean: {np.mean(values):.2f}\nReal Std: {np.std(values, ddof=1):.2f}\n"
        f"Synth Mean: {np.mean(synthetic_data):.2f}\nSynth Std: {np.std(synthetic_data, ddof=1):.2f}",
        transform=axes[1].transAxes,
        ha='right', va='top',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8)
    )
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    plt.show()
    
    # Print comparison statistics
    print("\nComparison Statistics:")
    print(f"Real Data - Mean: {np.mean(values):.2f}, Std: {np.std(values, ddof=1):.2f}")
    print(f"Synthetic Data - Mean: {np.mean(synthetic_data):.2f}, Std: {np.std(synthetic_data, ddof=1):.2f}")


def plot_probability_distributions(save_path=None):
    """
    Create a multi-panel figure summarizing theoretical probability distributions,
    and annotate each subplot with the most important numerical parameters.
    
    Args:
        save_path: str, optional path to save figure
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Binomial
    n, p = 20, 0.3
    k = np.arange(0, n+1)
    pmf_binom = binom.pmf(k, n, p)
    cdf_binom = binom.cdf(k, n, p)
    
    axes[0, 0].bar(k, pmf_binom, alpha=0.7, color='steelblue', edgecolor='black')
    axes[0, 0].set_xlabel('k (Number of Successes)')
    axes[0, 0].set_ylabel('Probability')
    axes[0, 0].set_title(f'Binomial PMF (n={n}, p={p})')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].text(
        0.02, 0.95,
        f"Mean: {n * p:.2f}\nStd: {np.sqrt(n * p * (1 - p)):.2f}",
        transform=axes[0, 0].transAxes,
        ha='left', va='top',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
    )
    
    axes[0, 1].plot(k, cdf_binom, 'o-', color='steelblue', linewidth=2, markersize=4)
    axes[0, 1].set_xlabel('k (Number of Successes)')
    axes[0, 1].set_ylabel('Cumulative Probability')
    axes[0, 1].set_title(f'Binomial CDF (n={n}, p={p})')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].text(
        0.02, 0.15,
        f"P(X ≤ 5) = {binom.cdf(5, n, p):.3f}\nP(X ≥ 10) = {1 - binom.cdf(9, n, p):.3f}",
        transform=axes[0, 1].transAxes,
        ha='left', va='bottom',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
    )
    
    # Poisson
    lambda_param = 5
    k_poisson = np.arange(0, 20)
    pmf_poisson = poisson.pmf(k_poisson, lambda_param)
    cdf_poisson = poisson.cdf(k_poisson, lambda_param)
    
    axes[0, 2].bar(k_poisson, pmf_poisson, alpha=0.7, color='green', edgecolor='black')
    axes[0, 2].set_xlabel('k (Number of Events)')
    axes[0, 2].set_ylabel('Probability')
    axes[0, 2].set_title(f'Poisson PMF (λ={lambda_param})')
    axes[0, 2].grid(True, alpha=0.3)
    axes[0, 2].text(
        0.02, 0.95,
        f"Mean = Variance = {lambda_param:.2f}\nStd: {np.sqrt(lambda_param):.2f}",
        transform=axes[0, 2].transAxes,
        ha='left', va='top',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
    )
    
    # Normal
    mu, sigma = 0, 1
    x_norm = np.linspace(-4, 4, 100)
    pdf_norm = norm.pdf(x_norm, mu, sigma)
    cdf_norm = norm.cdf(x_norm, mu, sigma)
    
    axes[1, 0].plot(x_norm, pdf_norm, 'r-', linewidth=2, label='PDF')
    axes[1, 0].set_xlabel('x')
    axes[1, 0].set_ylabel('Density')
    axes[1, 0].set_title(f'Normal PDF (μ={mu}, σ={sigma})')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].legend()
    axes[1, 0].text(
        0.02, 0.95,
        "68-95-99.7 Rule\nμ ± σ = 68%\nμ ± 2σ = 95%",
        transform=axes[1, 0].transAxes,
        ha='left', va='top',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
    )
    
    axes[1, 1].plot(x_norm, cdf_norm, 'r-', linewidth=2, label='CDF')
    axes[1, 1].set_xlabel('x')
    axes[1, 1].set_ylabel('Cumulative Probability')
    axes[1, 1].set_title(f'Normal CDF (μ={mu}, σ={sigma})')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].legend()
    axes[1, 1].text(
        0.02, 0.15,
        f"P(X ≤ 1.0) = {norm.cdf(1, mu, sigma):.3f}\nP(X ≥ 1.5) = {1 - norm.cdf(1.5, mu, sigma):.3f}",
        transform=axes[1, 1].transAxes,
        ha='left', va='bottom',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
    )
    
    # Exponential
    lambda_exp = 1
    x_exp = np.linspace(0, 5, 100)
    pdf_exp = expon.pdf(x_exp, scale=1/lambda_exp)
    cdf_exp = expon.cdf(x_exp, scale=1/lambda_exp)
    
    axes[1, 2].plot(x_exp, pdf_exp, 'purple', linewidth=2, label='PDF')
    axes[1, 2].plot(x_exp, cdf_exp, 'orange', linewidth=2, label='CDF')
    axes[1, 2].set_xlabel('x')
    axes[1, 2].set_ylabel('Density / Cumulative Probability')
    axes[1, 2].set_title(f'Exponential Distribution (λ={lambda_exp})')
    axes[1, 2].grid(True, alpha=0.3)
    axes[1, 2].legend()
    axes[1, 2].text(
        0.98, 0.95,
        f"Mean: {1/lambda_exp:.2f}\nP(X ≤ 2) = {expon.cdf(2, scale=1/lambda_exp):.3f}",
        transform=axes[1, 2].transAxes,
        ha='right', va='top',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
    )
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    plt.show()


def create_statistical_report(data_dict, output_file='lab4_statistical_report.txt'):
    """
    Create a statistical report summarizing findings.
    
    Args:
        data_dict: dict, dictionary containing data and statistics
        output_file: str, output file path
    """
    current_dir = Path(__file__).parent
    report_path = current_dir / output_file
    
    with open(report_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write("LAB 4: STATISTICAL ANALYSIS REPORT\n")
        f.write("Descriptive Statistics and Probability Distributions\n")
        f.write("="*80 + "\n\n")
        
        # Concrete Strength Analysis
        if 'concrete' in data_dict:
            f.write("1. CONCRETE STRENGTH ANALYSIS\n")
            f.write("-"*80 + "\n")
            stats = data_dict['concrete']['stats']
            f.write(f"Sample Size: {stats['count']}\n")
            f.write(f"Mean: {stats['mean']:.2f} MPa\n")
            f.write(f"Median: {stats['median']:.2f} MPa\n")
            f.write(f"Mode: {stats['mode']:.2f} MPa\n")
            f.write(f"Standard Deviation: {stats['std']:.2f} MPa\n")
            f.write(f"Variance: {stats['variance']:.2f} MPa²\n")
            f.write(f"Range: {stats['range']:.2f} MPa\n")
            f.write(f"IQR: {stats['iqr']:.2f} MPa\n")
            f.write(f"Skewness: {stats['skewness']:.3f}\n")
            f.write(f"Kurtosis: {stats['kurtosis']:.3f}\n\n")
            
            # Interpretation
            f.write("Interpretation:\n")
            if abs(stats['skewness']) < 0.5:
                f.write("- Distribution is approximately symmetric.\n")
            elif stats['skewness'] > 0.5:
                f.write("- Distribution is right-skewed (positive skew).\n")
            else:
                f.write("- Distribution is left-skewed (negative skew).\n")
            
            if stats['kurtosis'] < 0:
                f.write("- Distribution has lighter tails than normal (platykurtic).\n")
            elif stats['kurtosis'] > 0:
                f.write("- Distribution has heavier tails than normal (leptokurtic).\n")
            else:
                f.write("- Distribution has normal tail behavior (mesokurtic).\n")
            f.write("\n")
        
        # Material Comparison
        if 'materials' in data_dict:
            f.write("2. MATERIAL COMPARISON\n")
            f.write("-"*80 + "\n")
            for material, stats in data_dict['materials'].items():
                f.write(f"\n{material}:\n")
                f.write(f"  Mean: {stats['mean']:.2f} MPa\n")
                f.write(f"  Std: {stats['std']:.2f} MPa\n")
                f.write(f"  Min: {stats['min']:.2f} MPa\n")
                f.write(f"  Max: {stats['max']:.2f} MPa\n")
            f.write("\n")
        
        # Probability Calculations
        if 'probabilities' in data_dict:
            f.write("3. PROBABILITY CALCULATIONS\n")
            f.write("-"*80 + "\n")
            for scenario, result in data_dict['probabilities'].items():
                f.write(f"\n{scenario}:\n")
                f.write(str(result) + "\n")
            f.write("\n")
        
        # Bayes' Theorem
        if 'bayes' in data_dict:
            f.write("4. BAYES' THEOREM APPLICATION\n")
            f.write("-"*80 + "\n")
            bayes = data_dict['bayes']
            f.write(f"Prior Probability: {bayes['prior']:.3f}\n")
            f.write(f"Sensitivity: {bayes['sensitivity']:.3f}\n")
            f.write(f"Specificity: {bayes['specificity']:.3f}\n")
            f.write(f"Posterior Probability: {bayes['posterior']:.3f}\n")
            f.write("\nEngineering Implications:\n")
            f.write("- The posterior probability indicates the likelihood of actual damage\n")
            f.write("  given a positive test result, which is crucial for decision-making.\n")
            f.write("\n")
        
        # Distribution Fitting
        if 'fitting' in data_dict:
            f.write("5. DISTRIBUTION FITTING\n")
            f.write("-"*80 + "\n")
            fitting = data_dict['fitting']
            f.write(f"Fitted Mean: {fitting['mean']:.2f}\n")
            f.write(f"Fitted Std: {fitting['std']:.2f}\n")
            f.write(f"Sample Mean: {fitting['sample_mean']:.2f}\n")
            f.write(f"Sample Std: {fitting['sample_std']:.2f}\n")
            f.write("\n")
        
        f.write("="*80 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*80 + "\n")
    
    print(f"Statistical report saved to {report_path}")


def main():
    """Main execution function."""
    print("="*80)
    print("LAB 4: STATISTICAL ANALYSIS")
    print("Descriptive Statistics and Probability Distributions")
    print("="*80 + "\n")
    
    # Store results for report
    results_dict = {}
    
    # ============================================================================
    # PART 1: DESCRIPTIVE STATISTICS
    # ============================================================================
    print("\n" + "="*80)
    print("PART 1: DESCRIPTIVE STATISTICS")
    print("="*80 + "\n")
    
    # Task 1: Concrete Strength Analysis
    print("Task 1: Loading Concrete Strength Data...")
    concrete_data = load_data('concrete_strength.csv')
    print("\nFirst few rows:")
    print(concrete_data.head())
    print("\nData Info:")
    print(concrete_data.info())
    print("\nSummary Statistics:")
    print(concrete_data.describe())
    
    # Handle missing values
    print(f"\nMissing values: {concrete_data.isnull().sum().sum()}")
    if concrete_data.isnull().sum().sum() > 0:
        concrete_data = concrete_data.dropna()
        print("Missing values removed.")
    
    # Calculate descriptive statistics
    concrete_stats = calculate_descriptive_stats(concrete_data, 'strength_mpa')
    results_dict['concrete'] = {'stats': concrete_stats}
    
    print("\n" + "-"*80)
    print("DESCRIPTIVE STATISTICS - CONCRETE STRENGTH")
    print("-"*80)
    print(f"Count: {concrete_stats['count']}")
    print(f"Mean: {concrete_stats['mean']:.2f} MPa")
    print(f"Median: {concrete_stats['median']:.2f} MPa")
    print(f"Mode: {concrete_stats['mode']:.2f} MPa")
    print(f"Standard Deviation: {concrete_stats['std']:.2f} MPa")
    print(f"Variance: {concrete_stats['variance']:.2f} MPa²")
    print(f"Range: {concrete_stats['range']:.2f} MPa")
    print(f"IQR: {concrete_stats['iqr']:.2f} MPa")
    print(f"Q1: {concrete_stats['q1']:.2f} MPa")
    print(f"Q2 (Median): {concrete_stats['q2']:.2f} MPa")
    print(f"Q3: {concrete_stats['q3']:.2f} MPa")
    print(f"Skewness: {concrete_stats['skewness']:.3f}")
    print(f"Kurtosis: {concrete_stats['kurtosis']:.3f}")
    
    # Interpretation
    print("\nInterpretation:")
    if abs(concrete_stats['skewness']) < 0.5:
        print("- Distribution is approximately symmetric.")
    elif concrete_stats['skewness'] > 0.5:
        print("- Distribution is right-skewed (positive skew).")
    else:
        print("- Distribution is left-skewed (negative skew).")
    
    if concrete_stats['kurtosis'] < 0:
        print("- Distribution has lighter tails than normal (platykurtic).")
    elif concrete_stats['kurtosis'] > 0:
        print("- Distribution has heavier tails than normal (leptokurtic).")
    else:
        print("- Distribution has normal tail behavior (mesokurtic).")
    
    # Create visualizations
    print("\nCreating visualizations...")
    plot_distribution(concrete_data, 'strength_mpa', 'Concrete Strength',
                     save_path='concrete_strength_distribution.png')
    
    # Task 2: Material Comparison
    print("\n" + "-"*80)
    print("Task 2: Loading Material Properties Data...")
    material_data = load_data('material_properties.csv')
    print("\nFirst few rows:")
    print(material_data.head())
    
    # Calculate statistics for each material
    material_stats = {}
    for material in material_data['material_type'].unique():
        material_subset = material_data[material_data['material_type'] == material]
        stats_m = calculate_descriptive_stats(material_subset, 'yield_strength_mpa')
        material_stats[material] = stats_m
        print(f"\n{material} Statistics:")
        print(f"  Mean: {stats_m['mean']:.2f} MPa")
        print(f"  Std: {stats_m['std']:.2f} MPa")
        print(f"  Min: {stats_m['min']:.2f} MPa")
        print(f"  Max: {stats_m['max']:.2f} MPa")
    
    results_dict['materials'] = material_stats
    
    # Create comparative visualization
    plot_material_comparison(material_data, 'yield_strength_mpa', 'material_type',
                            save_path='material_comparison_boxplot.png')
    
    # ============================================================================
    # PART 2: PROBABILITY DISTRIBUTIONS
    # ============================================================================
    print("\n" + "="*80)
    print("PART 2: PROBABILITY DISTRIBUTIONS")
    print("="*80 + "\n")
    
    # Discrete Distributions
    print("Discrete Distributions:")
    print("-"*80)
    
    # Binomial
    print("\n1. Binomial Distribution:")
    print("   Scenario: Quality control - 100 components tested, 5% defect rate")
    n_binom, p_binom = 100, 0.05
    prob_binom = calculate_probability_binomial(n_binom, p_binom, [3, 5])
    print(f"   P(X = 3): {prob_binom[3]['exact']:.4f}")
    print(f"   P(X <= 5): {prob_binom[5]['at_most']:.4f}")
    print(f"   Mean: {prob_binom['distribution']['mean']:.2f}")
    print(f"   Variance: {prob_binom['distribution']['variance']:.2f}")
    
    # Poisson
    print("\n2. Poisson Distribution:")
    print("   Scenario: Bridge load events - Average 10 heavy trucks per hour")
    lambda_poisson = 10
    prob_poisson = calculate_probability_poisson(lambda_poisson, [8, 15])
    print(f"   P(X = 8): {prob_poisson[8]['exact']:.4f}")
    print(f"   P(X > 15): {prob_poisson[15]['more_than']:.4f}")
    print(f"   Mean: {prob_poisson['distribution']['mean']:.2f}")
    print(f"   Variance: {prob_poisson['distribution']['variance']:.2f}")
    
    # Continuous Distributions
    print("\nContinuous Distributions:")
    print("-"*80)
    
    # Normal
    print("\n3. Normal Distribution:")
    print("   Scenario: Steel yield strength - Mean = 250 MPa, Std = 15 MPa")
    mean_normal, std_normal = 250, 15
    prob_normal = calculate_probability_normal(mean_normal, std_normal, x_upper=280)
    prob_normal_upper = calculate_probability_normal(mean_normal, std_normal, x_lower=280)
    print(f"   P(X > 280 MPa): {prob_normal_upper['probability']:.4f} ({prob_normal_upper['probability']*100:.2f}%)")
    print(f"   95th Percentile: {prob_normal['percentile_95']:.2f} MPa")
    
    # Exponential
    print("\n4. Exponential Distribution:")
    print("   Scenario: Component lifetime - Mean = 1000 hours")
    mean_exp = 1000
    prob_exp = calculate_probability_exponential(mean_exp, [500, 1500])
    print(f"   P(X < 500 hours): {prob_exp[500]['before']:.4f}")
    print(f"   P(X > 1500 hours): {prob_exp[1500]['after']:.4f}")
    
    # Store probability results
    results_dict['probabilities'] = {
        'binomial': prob_binom,
        'poisson': prob_poisson,
        'normal': prob_normal,
        'exponential': prob_exp
    }
    
    # Plot probability distributions
    print("\nCreating probability distribution plots...")
    plot_probability_distributions(save_path='probability_distributions.png')
    
    # Distribution Fitting
    print("\n" + "-"*80)
    print("Distribution Fitting:")
    print("-"*80)
    params_fit, fitted_dist = fit_distribution(concrete_data, 'strength_mpa', 'normal')
    print(f"Fitted Normal Distribution:")
    print(f"  Mean: {params_fit['mean']:.2f} MPa")
    print(f"  Std: {params_fit['std']:.2f} MPa")
    print(f"Sample Statistics:")
    print(f"  Mean: {concrete_stats['mean']:.2f} MPa")
    print(f"  Std: {concrete_stats['std']:.2f} MPa")
    
    results_dict['fitting'] = {
        'mean': params_fit['mean'],
        'std': params_fit['std'],
        'sample_mean': concrete_stats['mean'],
        'sample_std': concrete_stats['std']
    }
    
    plot_distribution_fitting(concrete_data, 'strength_mpa', fitted_dist,
                             save_path='distribution_fitting.png')
    
    # ============================================================================
    # PART 3: PROBABILITY APPLICATIONS
    # ============================================================================
    print("\n" + "="*80)
    print("PART 3: PROBABILITY APPLICATIONS")
    print("="*80 + "\n")
    
    # Bayes' Theorem
    print("Bayes' Theorem Application:")
    print("-"*80)
    print("Scenario: Structural damage detection")
    print("  Base rate: 5% of structures have damage")
    print("  Test sensitivity: 95% (detects damage when present)")
    print("  Test specificity: 90% (correctly identifies no damage)")
    
    bayes_results = apply_bayes_theorem(prior=0.05, sensitivity=0.95, specificity=0.90)
    
    print(f"\nPrior Probability: {bayes_results['prior']:.3f}")
    print(f"Sensitivity: {bayes_results['sensitivity']:.3f}")
    print(f"Specificity: {bayes_results['specificity']:.3f}")
    print(f"\nPosterior Probability (P(damage | test+)): {bayes_results['posterior']:.3f}")
    print(f"Probability of Positive Test: {bayes_results['p_test_positive']:.3f}")
    
    print("\nProbability Tree:")
    tree = bayes_results['probability_tree']
    print(f"  P(Damage) = {tree['p_disease']:.3f}")
    print(f"  P(No Damage) = {tree['p_no_disease']:.3f}")
    print(f"  P(Test+ | Damage) = {tree['p_test_pos_given_disease']:.3f}")
    print(f"  P(Test+ | No Damage) = {tree['p_test_pos_given_no_disease']:.3f}")
    print(f"  P(Test+ and Damage) = {tree['p_test_pos_and_disease']:.3f}")
    print(f"  P(Test+ and No Damage) = {tree['p_test_pos_and_no_disease']:.3f}")
    
    print("\nEngineering Implications:")
    print("- Even with high sensitivity (95%), the posterior probability is relatively low")
    print("  due to the low prior probability (5%). This is a classic example of")
    print("  how base rates affect diagnostic test results.")
    
    results_dict['bayes'] = bayes_results
    
    # ============================================================================
    # PART 4: STATISTICAL SUMMARY DASHBOARD
    # ============================================================================
    print("\n" + "="*80)
    print("PART 4: CREATING STATISTICAL SUMMARY DASHBOARD")
    print("="*80 + "\n")
    
    # Create a comprehensive dashboard summarizing all core insights
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Concrete strength histogram
    ax1 = fig.add_subplot(gs[0, 0])
    concrete_data['strength_mpa'].hist(bins=30, ax=ax1, color='steelblue', edgecolor='black', alpha=0.7)
    ax1.axvline(concrete_stats['mean'], color='red', linestyle='--', linewidth=2, label='Mean')
    ax1.axvline(concrete_stats['median'], color='green', linestyle='--', linewidth=2, label='Median')
    ax1.set_xlabel('Strength (MPa)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Concrete Strength Distribution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.text(
        0.98, 0.95,
        f"Mean: {concrete_stats['mean']:.2f}\nStd: {concrete_stats['std']:.2f}",
        transform=ax1.transAxes,
        ha='right', va='top',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
    )
    
    # 2. Material comparison boxplot
    ax2 = fig.add_subplot(gs[0, 1])
    material_data.boxplot(column='yield_strength_mpa', by='material_type', ax=ax2)
    ax2.set_title('Material Strength Comparison')
    ax2.set_xlabel('Material Type')
    ax2.set_ylabel('Yield Strength (MPa)')
    ax2.grid(True, alpha=0.3)
    for idx, material in enumerate(material_data['material_type'].unique(), start=1):
        stats_m = material_stats[material]
        ax2.text(
            idx,
            stats_m['q3'],
            f"Median: {stats_m['median']:.1f}\nIQR: {stats_m['iqr']:.1f}",
            ha='center',
            va='bottom',
            fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
        )
    
    # 3. Normal distribution fit
    ax3 = fig.add_subplot(gs[0, 2])
    values = concrete_data['strength_mpa'].dropna()
    ax3.hist(values, bins=30, density=True, alpha=0.7, color='steelblue', edgecolor='black')
    x = np.linspace(values.min(), values.max(), 100)
    pdf = fitted_dist.pdf(x)
    ax3.plot(x, pdf, 'r-', linewidth=2, label='Fitted Normal')
    ax3.set_xlabel('Strength (MPa)')
    ax3.set_ylabel('Density')
    ax3.set_title('Distribution Fitting')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.text(
        0.02, 0.95,
        f"Fitted μ: {params_fit['mean']:.2f}\nFitted σ: {params_fit['std']:.2f}",
        transform=ax3.transAxes,
        ha='left', va='top',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
    )
    
    # 4. Statistics summary table
    ax4 = fig.add_subplot(gs[1, :])
    ax4.axis('off')
    stats_text = f"""
    CONCRETE STRENGTH STATISTICS
    {'='*60}
    Mean:              {concrete_stats['mean']:.2f} MPa
    Median:            {concrete_stats['median']:.2f} MPa
    Standard Deviation: {concrete_stats['std']:.2f} MPa
    Range:             {concrete_stats['range']:.2f} MPa
    IQR:               {concrete_stats['iqr']:.2f} MPa
    Skewness:          {concrete_stats['skewness']:.3f}
    Kurtosis:          {concrete_stats['kurtosis']:.3f}
    """
    ax4.text(0.1, 0.5, stats_text, fontsize=12, family='monospace', verticalalignment='center')
    
    # 5. Probability distributions
    ax5 = fig.add_subplot(gs[2, 0])
    k_binom = np.arange(0, 21)
    pmf = binom.pmf(k_binom, n_binom, p_binom)
    ax5.bar(k_binom, pmf, alpha=0.7, color='green', edgecolor='black')
    ax5.set_xlabel('Number of Defects')
    ax5.set_ylabel('Probability')
    ax5.set_title('Binomial Distribution (n=100, p=0.05)')
    ax5.grid(True, alpha=0.3)
    ax5.text(
        0.02, 0.95,
        f"Mean: {n_binom * p_binom:.1f}\nStd: {np.sqrt(n_binom * p_binom * (1 - p_binom)):.1f}",
        transform=ax5.transAxes,
        ha='left', va='top',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
    )
    
    ax6 = fig.add_subplot(gs[2, 1])
    k_pois = np.arange(0, 25)
    pmf_pois = poisson.pmf(k_pois, lambda_poisson)
    ax6.bar(k_pois, pmf_pois, alpha=0.7, color='orange', edgecolor='black')
    ax6.set_xlabel('Number of Trucks')
    ax6.set_ylabel('Probability')
    ax6.set_title('Poisson Distribution (λ=10)')
    ax6.grid(True, alpha=0.3)
    ax6.text(
        0.02, 0.95,
        f"Mean: {lambda_poisson:.1f}\nStd: {np.sqrt(lambda_poisson):.1f}",
        transform=ax6.transAxes,
        ha='left', va='top',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
    )
    
    ax7 = fig.add_subplot(gs[2, 2])
    x_norm = np.linspace(200, 300, 100)
    pdf_norm = norm.pdf(x_norm, mean_normal, std_normal)
    ax7.plot(x_norm, pdf_norm, 'r-', linewidth=2)
    ax7.axvline(280, color='blue', linestyle='--', linewidth=2, label='280 MPa')
    ax7.fill_between(x_norm[x_norm >= 280], 0, pdf_norm[x_norm >= 280], alpha=0.3, color='red')
    ax7.set_xlabel('Yield Strength (MPa)')
    ax7.set_ylabel('Density')
    ax7.set_title('Normal Distribution (μ=250, σ=15)')
    ax7.legend()
    ax7.grid(True, alpha=0.3)
    ax7.text(
        0.98, 0.95,
        f"P(X ≥ 280) = {prob_normal_upper['probability']:.3f}",
        transform=ax7.transAxes,
        ha='right', va='top',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
    )
    
    plt.suptitle('Statistical Analysis Dashboard', fontsize=16, fontweight='bold', y=0.995)
    plt.savefig('statistical_summary_dashboard.png', dpi=300, bbox_inches='tight')
    print("Saved statistical summary dashboard to statistical_summary_dashboard.png")
    plt.show()
    
    # ============================================================================
    # PART 5: GENERATE REPORT
    # ============================================================================
    print("\n" + "="*80)
    print("PART 5: GENERATING STATISTICAL REPORT")
    print("="*80 + "\n")
    
    create_statistical_report(results_dict, 'lab4_statistical_report.txt')
    
    print("\n" + "="*80)
    print("LAB 4 COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\nGenerated files:")
    print("  - concrete_strength_distribution.png")
    print("  - material_comparison_boxplot.png")
    print("  - probability_distributions.png")
    print("  - distribution_fitting.png")
    print("  - statistical_summary_dashboard.png")
    print("  - lab4_statistical_report.txt")


if __name__ == "__main__":
    main()

