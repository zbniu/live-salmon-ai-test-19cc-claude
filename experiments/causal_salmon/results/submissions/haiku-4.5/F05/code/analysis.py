import pandas as pd
import numpy as np
from scipy import stats
import json

# Load data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

print("=" * 70)
print("STUDY DATA ANALYSIS")
print("=" * 70)
print()

# 1. Check data structure and completeness
print("1. DATA STRUCTURE")
print("-" * 70)
print(f"Number of rows: {len(df)}")
print(f"Number of columns: {len(df.columns)}")
print(f"Column names: {list(df.columns)}")
print(f"Data types:\n{df.dtypes}")
print(f"Missing values:\n{df.isnull().sum()}")
print()

# 2. Summary statistics
print("2. SUMMARY STATISTICS")
print("-" * 70)
print(df.describe())
print()

# 3. Treatment allocation check
print("3. TREATMENT ALLOCATION")
print("-" * 70)
print(f"Total units: {len(df)}")
print(f"Units receiving arrangement Q (x=1): {(df['x'] == 1).sum()}")
print(f"Units not receiving arrangement Q (x=0): {(df['x'] == 0).sum()}")
print(f"Expected treated units: 600")
print()

# 4. Balance check - compare baseline (y) between treated and control
print("4. COVARIATE BALANCE CHECK (baseline y)")
print("-" * 70)
treated_y = df[df['x'] == 1]['y']
control_y = df[df['x'] == 0]['y']

print(f"Control group (x=0):")
print(f"  n = {len(control_y)}")
print(f"  mean y = {control_y.mean():.6f}")
print(f"  std y = {control_y.std():.6f}")
print()

print(f"Treated group (x=1):")
print(f"  n = {len(treated_y)}")
print(f"  mean y = {treated_y.mean():.6f}")
print(f"  std y = {treated_y.std():.6f}")
print()

# T-test for baseline balance
t_stat_y, p_val_y = stats.ttest_ind(treated_y, control_y)
print(f"t-test for baseline balance:")
print(f"  t-statistic: {t_stat_y:.6f}")
print(f"  p-value: {p_val_y:.6f}")
print(f"  Difference in means: {treated_y.mean() - control_y.mean():.6f}")
print()

# 5. MAIN ANALYSIS: Treatment effect on change z
print("5. PRIMARY ANALYSIS: TREATMENT EFFECT ON CHANGE z")
print("-" * 70)
treated_z = df[df['x'] == 1]['z']
control_z = df[df['x'] == 0]['z']

print(f"Control group (x=0):")
print(f"  n = {len(control_z)}")
print(f"  mean z = {control_z.mean():.6f}")
print(f"  std z = {control_z.std():.6f}")
print(f"  median z = {control_z.median():.6f}")
print(f"  min z = {control_z.min():.6f}")
print(f"  max z = {control_z.max():.6f}")
print()

print(f"Treated group (x=1):")
print(f"  n = {len(treated_z)}")
print(f"  mean z = {treated_z.mean():.6f}")
print(f"  std z = {treated_z.std():.6f}")
print(f"  median z = {treated_z.median():.6f}")
print(f"  min z = {treated_z.min():.6f}")
print(f"  max z = {treated_z.max():.6f}")
print()

# Average Treatment Effect (ATE)
ate = treated_z.mean() - control_z.mean()
print(f"AVERAGE TREATMENT EFFECT (ATE):")
print(f"  ATE = {ate:.6f}")
print()

# 6. Statistical significance testing
print("6. STATISTICAL SIGNIFICANCE")
print("-" * 70)

# Two-sample t-test
t_stat, p_val = stats.ttest_ind(treated_z, control_z)
print(f"Two-sample t-test (assuming unequal variances):")
print(f"  t-statistic: {t_stat:.6f}")
print(f"  p-value: {p_val:.6f}")
print()

# Welch's t-test (more robust)
t_stat_welch, p_val_welch = stats.ttest_ind(treated_z, control_z, equal_var=False)
print(f"Welch's t-test (unequal variance):")
print(f"  t-statistic: {t_stat_welch:.6f}")
print(f"  p-value: {p_val_welch:.6f}")
print()

# 7. Confidence intervals
print("7. CONFIDENCE INTERVALS FOR ATE (95%)")
print("-" * 70)

# Standard error calculation
n_treated = len(treated_z)
n_control = len(control_z)
var_treated = treated_z.var(ddof=1)
var_control = control_z.var(ddof=1)
se = np.sqrt(var_treated / n_treated + var_control / n_control)

# 95% CI using t-distribution
df_welch = ((var_treated/n_treated + var_control/n_control)**2) / \
           ((var_treated/n_treated)**2/(n_treated-1) + (var_control/n_control)**2/(n_control-1))
t_critical = stats.t.ppf(0.975, df_welch)
ci_lower = ate - t_critical * se
ci_upper = ate + t_critical * se

print(f"Standard error of ATE: {se:.6f}")
print(f"Degrees of freedom (Welch): {df_welch:.2f}")
print(f"t-critical value (95%, two-tailed): {t_critical:.6f}")
print(f"95% CI for ATE: [{ci_lower:.6f}, {ci_upper:.6f}]")
print()

# 8. Effect size
print("8. EFFECT SIZE METRICS")
print("-" * 70)
pooled_std = np.sqrt(((n_treated-1)*var_treated + (n_control-1)*var_control) / (n_treated + n_control - 2))
cohens_d = ate / pooled_std
print(f"Cohen's d: {cohens_d:.6f}")
print()

# 9. Regression analysis (simple and with baseline covariate)
print("9. REGRESSION ANALYSIS")
print("-" * 70)

# Simple regression
X_simple = df[['x']]
X_simple = np.column_stack([np.ones(len(X_simple)), X_simple])
y = df['z'].values
beta_simple = np.linalg.lstsq(X_simple, y, rcond=None)[0]
print(f"Simple regression: z = β₀ + β₁*x")
print(f"  β₀ (intercept/control mean): {beta_simple[0]:.6f}")
print(f"  β₁ (treatment effect): {beta_simple[1]:.6f}")
print()

# With baseline covariate
X_cov = df[['x', 'y']]
X_cov = np.column_stack([np.ones(len(X_cov)), X_cov])
beta_cov = np.linalg.lstsq(X_cov, y, rcond=None)[0]
residuals = y - X_cov @ beta_cov
rss = np.sum(residuals**2)
mse = rss / (len(y) - X_cov.shape[1])

print(f"Regression with baseline covariate: z = β₀ + β₁*x + β₂*y")
print(f"  β₀ (intercept): {beta_cov[0]:.6f}")
print(f"  β₁ (treatment effect): {beta_cov[1]:.6f}")
print(f"  β₂ (baseline coefficient): {beta_cov[2]:.6f}")
print(f"  MSE: {mse:.6f}")
print()

print("=" * 70)
print("SUMMARY AND CONCLUSION")
print("=" * 70)
print()
print(f"Average Treatment Effect: {ate:.6f}")
print(f"95% Confidence Interval: [{ci_lower:.6f}, {ci_upper:.6f}]")
print(f"p-value (Welch's t-test): {p_val_welch:.10f}")
print()

if p_val_welch < 0.05:
    direction = "positive" if ate > 0 else "negative"
    print(f"CONCLUSION: Arrangement Q had a statistically significant {direction} effect on change z.")
    print(f"The effect is approximately {ate:.2f} points on the 0-100 scale.")
else:
    print(f"CONCLUSION: No statistically significant effect detected at the 0.05 level.")
    print(f"The estimated effect is {ate:.6f}, but this could plausibly be zero.")
print()

# Save results to JSON
results = {
    "ate": float(ate),
    "ate_ci_lower": float(ci_lower),
    "ate_ci_upper": float(ci_upper),
    "p_value": float(p_val_welch),
    "t_statistic": float(t_stat_welch),
    "se": float(se),
    "cohens_d": float(cohens_d),
    "control_mean": float(control_z.mean()),
    "treated_mean": float(treated_z.mean()),
    "n_treated": int(n_treated),
    "n_control": int(n_control),
    "significant_at_0_05": bool(p_val_welch < 0.05)
}

with open('/home/claude/submission/results/ate_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Results saved to ate_results.json")
