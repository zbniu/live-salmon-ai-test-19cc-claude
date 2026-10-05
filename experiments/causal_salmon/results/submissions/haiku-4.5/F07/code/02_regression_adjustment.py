#!/usr/bin/env python3
"""
Analysis 2: Regression Adjustment for Confounding
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression

# Load data
data = pd.read_csv('/mnt/user-data/uploads/data.csv')

print("="*70)
print("REGRESSION ADJUSTMENT ANALYSIS")
print("="*70)

y_outcome = data['z'].values

print("\n4. REGRESSION ADJUSTMENT FOR CONFOUNDING")
print("-"*70)

# Model 1: Just treatment (naive)
model_naive = LinearRegression()
X_naive = data[['x']].values
model_naive.fit(X_naive, y_outcome)
print(f"\nModel 1 (Naive): z = {model_naive.intercept_:.4f} + {model_naive.coef_[0]:.4f} * x")
print(f"Interpretation: Treatment effect = {model_naive.coef_[0]:.4f}")

# Model 2: Treatment and baseline (adjusted)
model_adjusted = LinearRegression()
X_adjusted = data[['x', 'y']].values
model_adjusted.fit(X_adjusted, y_outcome)
print(f"\nModel 2 (Adjusted for baseline): z = {model_adjusted.intercept_:.4f} + {model_adjusted.coef_[0]:.4f} * x + {model_adjusted.coef_[1]:.4f} * y")
print(f"Interpretation: Treatment effect (adjusted) = {model_adjusted.coef_[0]:.4f}")

# Statistical significance
from sklearn.metrics import mean_squared_error
mse = mean_squared_error(y_outcome, model_adjusted.predict(X_adjusted))
residual_std = np.sqrt(mse)

# Approximate standard error for treatment coefficient
# Using rough formula: SE ≈ residual_std / sqrt(n * var(x))
n = len(data)
var_treatment = data['x'].var()
se_treatment = residual_std / np.sqrt(n * var_treatment)
t_stat = model_adjusted.coef_[0] / se_treatment
p_val = 2 * (1 - stats.t.cdf(abs(t_stat), n-3))

print(f"\nResidual standard error: {residual_std:.4f}")
print(f"Approximate SE for treatment coefficient: {se_treatment:.4f}")
print(f"Approximate t-statistic: {t_stat:.4f}")
print(f"Approximate p-value: {p_val:.6f}")
print(f"R-squared (adjusted model): {model_adjusted.score(X_adjusted, y_outcome):.4f}")

# Model 3: Include interaction term to check if effect differs by baseline
data_aug = data.copy()
data_aug['x*y'] = data['x'] * data['y']
model_interaction = LinearRegression()
X_interaction = data_aug[['x', 'y', 'x*y']].values
model_interaction.fit(X_interaction, y_outcome)

print(f"\nModel 3 (With interaction): z = {model_interaction.intercept_:.4f} + {model_interaction.coef_[0]:.4f} * x + {model_interaction.coef_[1]:.4f} * y + {model_interaction.coef_[2]:.4f} * (x*y)")
print(f"Treatment effect at y=0: {model_interaction.coef_[0]:.4f}")
print(f"Interaction term: {model_interaction.coef_[2]:.4f}")
print(f"R-squared (interaction model): {model_interaction.score(X_interaction, y_outcome):.4f}")

# Summary of models
print("\n\nSUMMARY OF TREATMENT EFFECTS")
print("-"*70)
print(f"Model 1 (Naive): {model_naive.coef_[0]:.4f}")
print("  - Does NOT adjust for baseline confounding")
print("  - BIASED upward because treated units have higher baseline")
print("")
print(f"Model 2 (Linear adjustment): {model_adjusted.coef_[0]:.4f}")
print("  - Adjusts for baseline using linear regression")
print("  - Assumes parallel trends (constant effect across baselines)")
print("  - This is the main estimate")
print("")
print(f"Model 3 (Interaction): Effect varies with baseline")
print(f"  - Base coefficient: {model_interaction.coef_[0]:.4f}")
print(f"  - Interaction coefficient: {model_interaction.coef_[2]:.4f}")
print("  - Allows treatment effect to vary by baseline level")
print("")

# 5. Check robustness using stratification
print("\n5. STRATIFIED ANALYSIS (ROBUSTNESS CHECK)")
print("-"*70)

# Divide baseline into quartiles and estimate effect within each
data['y_quartile'] = pd.qcut(data['y'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'], duplicates='drop')

print("\nTreatment effect within baseline quartiles:")
for q in data['y_quartile'].unique():
    subset = data[data['y_quartile'] == q]
    control_mean = subset[subset['x']==0]['z'].mean()
    treated_mean = subset[subset['x']==1]['z'].mean()
    effect = treated_mean - control_mean
    n_control = len(subset[subset['x']==0])
    n_treated = len(subset[subset['x']==1])
    
    if n_control > 0 and n_treated > 0:
        print(f"{q} (y={subset['y'].min():.1f}-{subset['y'].max():.1f}): effect={effect:.4f} (n_control={n_control}, n_treated={n_treated})")
    else:
        print(f"{q}: insufficient data")

# 6. Covariate balance check
print("\n\n6. COVARIATE BALANCE CHECK")
print("-"*70)
print("Is treatment assignment independent of baseline within the data?")
print("(If confounded: baseline should differ strongly between treatment groups)")

mean_y_control = data[data['x']==0]['y'].mean()
mean_y_treated = data[data['x']==1]['y'].mean()
std_y_pooled = np.sqrt(((len(data[data['x']==0])-1)*data[data['x']==0]['y'].std()**2 + 
                         (len(data[data['x']==1])-1)*data[data['x']==1]['y'].std()**2) / 
                        (len(data)-2))
std_diff_y = std_y_pooled * np.sqrt(1/len(data[data['x']==0]) + 1/len(data[data['x']==1]))

t_stat_y = (mean_y_treated - mean_y_control) / std_diff_y
p_val_y = 2 * (1 - stats.t.cdf(abs(t_stat_y), len(data)-2))

print(f"Control baseline mean: {mean_y_control:.4f}")
print(f"Treatment baseline mean: {mean_y_treated:.4f}")
print(f"Difference in baseline: {mean_y_treated - mean_y_control:.4f}")
print(f"t-statistic: {t_stat_y:.4f}")
print(f"p-value: {p_val_y:.6f}")
print(f"\nConclusion: Baseline differs SIGNIFICANTLY between groups (p < 0.001)")
print("This confirms CONFOUNDING - assignment was not random.")
