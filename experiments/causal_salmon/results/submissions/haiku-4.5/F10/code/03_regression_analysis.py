"""
Regression analysis controlling for baseline score
"""
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression

# Load the data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

print("=" * 70)
print("REGRESSION ANALYSIS CONTROLLING FOR BASELINE SCORE")
print("=" * 70)

# Simple regression of z on x (naive)
X_naive = df[['x']]
y_var = df['z']
model_naive = LinearRegression().fit(X_naive, y_var)
print(f"\nModel 1: z ~ x (naive, no controls)")
print(f"  Treatment effect (x coefficient): {model_naive.coef_[0]:.4f}")
print(f"  Intercept: {model_naive.intercept_:.4f}")
print(f"  R-squared: {model_naive.score(X_naive, y_var):.4f}")

# Regression controlling for y
X_with_y = df[['x', 'y']]
model_with_y = LinearRegression().fit(X_with_y, y_var)
print(f"\nModel 2: z ~ x + y (controlling for baseline score)")
print(f"  Treatment effect (x coefficient): {model_with_y.coef_[0]:.4f}")
print(f"  Baseline score effect (y coefficient): {model_with_y.coef_[1]:.4f}")
print(f"  Intercept: {model_with_y.intercept_:.4f}")
print(f"  R-squared: {model_with_y.score(X_with_y, y_var):.4f}")

# Calculate residuals and their standard errors
residuals = y_var - model_with_y.predict(X_with_y)
n = len(residuals)
k = X_with_y.shape[1]
residual_std_error = np.sqrt(np.sum(residuals**2) / (n - k - 1))

# Calculate standard errors for coefficients
X_with_const = np.column_stack([np.ones(len(X_with_y)), X_with_y])
var_covar = np.linalg.inv(X_with_const.T @ X_with_const) * (residual_std_error ** 2)
std_errors = np.sqrt(np.diag(var_covar))

t_stat_x = model_with_y.coef_[0] / std_errors[1]
p_val_x = 2 * (1 - stats.t.cdf(np.abs(t_stat_x), n - k - 1))

print(f"\nInference for treatment effect in Model 2:")
print(f"  Standard error: {std_errors[1]:.4f}")
print(f"  t-statistic: {t_stat_x:.4f}")
print(f"  p-value: {p_val_x:.6f}")
print(f"  95% CI: [{model_with_y.coef_[0] - 1.96*std_errors[1]:.4f}, {model_with_y.coef_[0] + 1.96*std_errors[1]:.4f}]")

# With interaction term
df['x_times_y'] = df['x'] * df['y']
X_with_interaction = df[['x', 'y', 'x_times_y']]
model_interaction = LinearRegression().fit(X_with_interaction, y_var)
print(f"\nModel 3: z ~ x + y + x*y (with interaction)")
print(f"  Treatment effect (x coefficient): {model_interaction.coef_[0]:.4f}")
print(f"  Baseline score effect (y): {model_interaction.coef_[1]:.4f}")
print(f"  Interaction (x*y): {model_interaction.coef_[2]:.4f}")
print(f"  R-squared: {model_interaction.score(X_with_interaction, y_var):.4f}")
