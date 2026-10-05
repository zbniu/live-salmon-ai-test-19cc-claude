"""
Analysis of the effect of arrangement Q on change z
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

print("="*70)
print("DATA SUMMARY")
print("="*70)
print(f"\nDataset shape: {df.shape}")
print(f"\nFirst few rows:\n{df.head()}")
print(f"\nData types:\n{df.dtypes}")
print(f"\nBasic statistics:\n{df.describe()}")

# Check for missing values
print(f"\nMissing values: {df.isnull().sum().sum()}")

# Distribution of x (treatment assignment)
print(f"\nTreatment assignment (x):")
print(df['x'].value_counts().sort_index())
print(f"Proportion receiving Q: {df['x'].mean():.4f}")

print("\n" + "="*70)
print("ANALYSIS 1: NAIVE COMPARISON (BIASED)")
print("="*70)

# Separate by treatment group
q_group = df[df['x'] == 1]
no_q_group = df[df['x'] == 0]

print(f"\nArrangement Q group (x=1): n={len(q_group)}")
print(f"  Mean z: {q_group['z'].mean():.4f}")
print(f"  Std z: {q_group['z'].std():.4f}")
print(f"  Mean y (baseline): {q_group['y'].mean():.4f}")

print(f"\nNo arrangement Q group (x=0): n={len(no_q_group)}")
print(f"  Mean z: {no_q_group['z'].mean():.4f}")
print(f"  Std z: {no_q_group['z'].std():.4f}")
print(f"  Mean y (baseline): {no_q_group['y'].mean():.4f}")

naive_diff = q_group['z'].mean() - no_q_group['z'].mean()
print(f"\nNaive difference in z (Q vs No Q): {naive_diff:.4f}")

# Statistical test
t_stat, p_value = stats.ttest_ind(q_group['z'], no_q_group['z'])
print(f"T-test: t={t_stat:.4f}, p-value={p_value:.6f}")

print("\n" + "="*70)
print("ANALYSIS 2: REGRESSION ADJUSTMENT FOR BASELINE")
print("="*70)

from sklearn.linear_model import LinearRegression

# Simple regression: z ~ x
X_simple = df[['x']]
y = df['z']
model_simple = LinearRegression().fit(X_simple, y)
print(f"\nModel 1: z ~ x")
print(f"  Intercept: {model_simple.intercept_:.4f}")
print(f"  Coefficient for x: {model_simple.coef_[0]:.4f}")
print(f"  R-squared: {model_simple.score(X_simple, y):.6f}")

# Regression with baseline adjustment: z ~ x + y
X_adjusted = df[['x', 'y']]
model_adjusted = LinearRegression().fit(X_adjusted, y)
print(f"\nModel 2: z ~ x + y (baseline-adjusted)")
print(f"  Intercept: {model_adjusted.intercept_:.4f}")
print(f"  Coefficient for x: {model_adjusted.coef_[0]:.4f}")
print(f"  Coefficient for y: {model_adjusted.coef_[1]:.4f}")
print(f"  R-squared: {model_adjusted.score(X_adjusted, y):.6f}")

# Model with interaction: z ~ x + y + x*y
df_temp = df.copy()
df_temp['x_y'] = df_temp['x'] * df_temp['y']
X_interaction = df_temp[['x', 'y', 'x_y']]
model_interaction = LinearRegression().fit(X_interaction, y)
print(f"\nModel 3: z ~ x + y + x*y (with interaction)")
print(f"  Intercept: {model_interaction.intercept_:.4f}")
print(f"  Coefficient for x: {model_interaction.coef_[0]:.4f}")
print(f"  Coefficient for y: {model_interaction.coef_[1]:.4f}")
print(f"  Coefficient for x*y: {model_interaction.coef_[2]:.4f}")
print(f"  R-squared: {model_interaction.score(X_interaction, y):.6f}")

# Get standard errors for Model 2
from scipy.stats import t as t_dist
residuals = y - model_adjusted.predict(X_adjusted)
mse = np.sum(residuals**2) / (len(df) - X_adjusted.shape[1] - 1)
X_with_const = np.column_stack([np.ones(len(df)), X_adjusted])
var_covar = mse * np.linalg.inv(X_with_const.T @ X_with_const)
se = np.sqrt(np.diag(var_covar))

print(f"\nStandard errors for Model 2:")
print(f"  SE for x coefficient: {se[1]:.6f}")
coef_x = model_adjusted.coef_[0]
t_stat_x = coef_x / se[1]
df_residual = len(df) - X_adjusted.shape[1] - 1
p_value_x = 2 * (1 - t_dist.cdf(abs(t_stat_x), df_residual))
print(f"  t-statistic for x: {t_stat_x:.4f}")
print(f"  p-value for x: {p_value_x:.6f}")
ci_lower = coef_x - t_dist.ppf(0.975, df_residual) * se[1]
ci_upper = coef_x + t_dist.ppf(0.975, df_residual) * se[1]
print(f"  95% CI for x: [{ci_lower:.4f}, {ci_upper:.4f}]")

print("\n" + "="*70)
print("ANALYSIS 3: STRATIFIED ANALYSIS BY BASELINE")
print("="*70)

# Create baseline quartiles
df['y_quartile'] = pd.qcut(df['y'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'], duplicates='drop')

print("\nMean z by treatment group within each baseline quartile:")
for q in sorted(df['y_quartile'].unique()):
    q_data = df[df['y_quartile'] == q]
    q1 = q_data[q_data['x'] == 1]['z'].mean()
    q0 = q_data[q_data['x'] == 0]['z'].mean()
    n1 = len(q_data[q_data['x'] == 1])
    n0 = len(q_data[q_data['x'] == 0])
    diff = q1 - q0
    y_range = f"[{q_data['y'].min():.2f}, {q_data['y'].max():.2f}]"
    print(f"\n{q}: y {y_range}")
    print(f"  Q group (x=1): mean z = {q1:.4f} (n={n1})")
    print(f"  No Q group (x=0): mean z = {q0:.4f} (n={n0})")
    print(f"  Difference: {diff:.4f}")

print("\n" + "="*70)
print("ANALYSIS 4: INVERSE PROBABILITY WEIGHTING")
print("="*70)

# Estimate propensity scores (probability of receiving Q given baseline)
from sklearn.linear_model import LogisticRegression
X_propensity = df[['y']]
propensity_model = LogisticRegression().fit(X_propensity, df['x'])
propensity_scores = propensity_model.predict_proba(X_propensity)[:, 1]

print(f"\nPropensity score statistics:")
print(f"  Mean: {propensity_scores.mean():.4f}")
print(f"  Min: {propensity_scores.min():.4f}")
print(f"  Max: {propensity_scores.max():.4f}")

# IPW: weight by 1/p for treated, 1/(1-p) for control
df['weight'] = np.where(df['x'] == 1, 1/propensity_scores, 1/(1-propensity_scores))

# Weighted mean difference
weighted_treated = (df[df['x'] == 1]['z'] * df[df['x'] == 1]['weight']).sum() / df[df['x'] == 1]['weight'].sum()
weighted_control = (df[df['x'] == 0]['z'] * df[df['x'] == 0]['weight']).sum() / df[df['x'] == 0]['weight'].sum()
weighted_diff = weighted_treated - weighted_control

print(f"\nWeighted comparison:")
print(f"  Weighted mean z (Q group): {weighted_treated:.4f}")
print(f"  Weighted mean z (No Q group): {weighted_control:.4f}")
print(f"  Weighted difference: {weighted_diff:.4f}")

print("\n" + "="*70)
print("SUMMARY OF ESTIMATES")
print("="*70)

print(f"\nDifferent estimates of the effect of arrangement Q on z:")
print(f"  1. Naive difference (unadjusted): {naive_diff:.4f}")
print(f"  2. Regression adjustment (Model 2): {coef_x:.4f} (95% CI: [{ci_lower:.4f}, {ci_upper:.4f}])")
print(f"  3. Inverse probability weighting: {weighted_diff:.4f}")

# Also report model 3 coefficient
print(f"  4. Regression with interaction: {model_interaction.coef_[0]:.4f}")

print("\n" + "="*70)
print("RELATIONSHIP BETWEEN BASELINE AND OUTCOME")
print("="*70)

# Correlation
corr = df[['y', 'z']].corr().iloc[0, 1]
print(f"\nCorrelation between baseline (y) and change (z): {corr:.4f}")

# Regression of z on y
print(f"\nEffect of baseline on change (from Model 2):")
print(f"  For each unit increase in baseline, change increases by {model_adjusted.coef_[1]:.4f}")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
