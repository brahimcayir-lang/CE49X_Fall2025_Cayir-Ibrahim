import numpy as np
from sklearn.linear_model import LinearRegression

# Data: Age vs Concrete Strength
age = np.array([3, 7, 14, 28, 56, 90])
strength = np.array([20, 32, 38, 45, 50, 52])

X = age.reshape(-1, 1)
y = strength

# Fit model
model = LinearRegression()
model.fit(X, y)

# Coefficients
print(f"Slope: {model.coef_[0]:.2f}")
print(f"Intercept: {model.intercept_:.2f}")
print(f"R^2: {model.score(X, y):.3f}")

# Predict
age_new = np.array([[21], [42]])
pred = model.predict(age_new)
print(f"Predictions for ages 21 and 42: {pred}")