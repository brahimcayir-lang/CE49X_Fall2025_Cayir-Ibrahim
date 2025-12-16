# Linear Regression Challenge 1: Real Estate Valuation
## CE49X - Machine Learning

**Instructor:** Dr. Eyuphan Koc  
**Institution:** Bogazici University  
**Semester:** Fall 2025

This challenge is designed to be completed during class time.

**Note:** The dataset is located in the `challenge/data/` folder.

---

## Dataset Overview

The Real Estate Valuation dataset contains information about real estate transactions in Taiwan. This dataset has 414 samples and 6 features related to property characteristics and location.

**Features:**
- `X1 transaction date`: Transaction date (e.g., 2012.916667 = December 2012)
- `X2 house age`: Age of the house in years
- `X3 distance to the nearest MRT station`: Distance to nearest metro station in meters
- `X4 number of convenience stores`: Number of convenience stores within walking distance
- `X5 latitude`: Latitude coordinate
- `X6 longitude`: Longitude coordinate

**Target Variable:**
- `Y house price of unit area`: House price per unit area (10,000 New Taiwan Dollar/Ping, where 1 Ping = 3.3 m²)

**Dataset Size:** 414 samples, 6 features

**File:** `Real estate valuation data set.xlsx`

---

## Challenge: Predicting House Prices

**Objective:** Build a linear regression model to predict house prices per unit area based on property and location features.

**Tasks:**

1. **Load the dataset:**
   ```python
   import pandas as pd
   df = pd.read_excel('challenge/data/Real estate valuation data set.xlsx')
   ```

2. **Explore the data:**
   - Print the shape of the dataset
   - Display the first few rows
   - Check for any missing values
   - Print basic statistics (mean, std) for the target variable

3. **Prepare the data:**
   - Remove the 'No' column (if present, it's just an index)
   - Separate features (X) and target (y = 'Y house price of unit area')
   - Select only the X1-X6 columns as features

4. **Split the data:**
   - Try different splits for training and testing
   - Set `random_state=42` for reproducibility

5. **Train a Linear Regression model:**
   - Fit the model on training data
   - Print the R² score on both training and test sets

6. **Interpret the model:**
   - Print the coefficients for each feature
   - Identify the top 3 features with the largest absolute coefficients
   - What do these coefficients tell you about house prices?
   - Does distance to MRT station have a positive or negative effect? Why?

7. **Make predictions:**
   - Predict the price for a property with these characteristics:
     - House age = 5 years
     - Distance to MRT = 500 meters
     - Number of convenience stores = 3
     - Transaction date = 2013.5
   - (Use median values for latitude and longitude)

**Expected Deliverables:**
- Training and test R² scores
- Top 3 most important features
- Interpretation of the distance to MRT coefficient
- Prediction for the given property

---

## General Instructions

### Required Libraries
```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
```

### Loading Excel Files
If you encounter issues loading Excel files, you may need to install:
```bash
pip install openpyxl  # For .xlsx files
pip install xlrd     # For .xls files
```

### Evaluation Metrics
- **R² Score**: Proportion of variance explained (higher is better, max = 1.0)
  - R² = 1.0 means perfect predictions
  - R² = 0.0 means model is no better than predicting the mean
  - Negative R² means model is worse than predicting the mean
- **MAE (Mean Absolute Error)**: Average absolute difference between predictions and actual values (in same units as target)
- **RMSE (Root Mean Squared Error)**: Square root of average squared differences (penalizes large errors more)

### Tips
1. **Always split your data before training** - Never evaluate on training data alone
2. **Check for missing values** - Handle them appropriately (drop or fill)
3. **Look at feature correlations** - Helps understand relationships before modeling
4. **Interpret coefficients carefully:**
   - Positive coefficient = feature increases target
   - Negative coefficient = feature decreases target
   - Larger absolute value = stronger effect
5. **Compare training and test scores** - Large gap indicates overfitting
6. **For categorical features** - You may need to encode them (one-hot encoding) or convert to numerical

### Common Issues and Solutions

**Issue:** Column names have extra spaces or special characters
```python
# Clean column names
df.columns = df.columns.str.strip()
```

**Issue:** Need to select specific columns
```python
# Select only numerical columns
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
X = df[numeric_cols].drop('target_column', axis=1)
```

**Issue:** Excel file has multiple sheets
```python
# Specify sheet name
df = pd.read_excel('file.xlsx', sheet_name='Sheet1')
```

### Submission
For this challenge, provide:
- Your complete code
- Training and test R² scores
- Answers to all interpretation questions
- Prediction for the given example
- Brief comments on what you learned from the model

---

## Quick Reference: Linear Regression Workflow

```python
# 1. Load and explore
df = pd.read_csv('data.csv')
print(df.head())
print(df.info())

# 2. Prepare data
X = df[['feature1', 'feature2', 'feature3']]
y = df['target']

# 3. Split data
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. Train model
from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X_train, y_train)

# 5. Evaluate
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)
print(f"Train R²: {train_score:.3f}")
print(f"Test R²: {test_score:.3f}")

# 6. Interpret
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)

# 7. Predict
predictions = model.predict(X_test)
```

---

**Good luck! Remember: Linear regression is about finding the best linear relationship between features and target. Keep it simple, focus on understanding what the model tells you, and don't forget to interpret your results in the context of the problem domain!**

