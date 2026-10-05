"""
Analysis of treatment effect for arrangement Q
Research question: Did receiving arrangement Q increase change z? If so, by how much?
"""

import pandas as pd
import numpy as np
from scipy import stats

# Load data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

print("=" * 70)
print("ANALYSIS 1: NAIVE COMPARISON (UNADJUSTED)")
print("=" * 70)

# Simple difference in means
treated = df[df['x'] == 1]['z']
control = df[df['x'] == 0]['z']

naive_diff = treated.mean() - control.mean()
print(f"\nMean change for treated: {treated.mean():.4f}")
print(f"Mean change for control: {control.mean():.4f}")
print(f"Naive difference: {naive_diff:.4f}")

# T-test
t_stat, p_val = stats.ttest_ind(treated, control)
print(f"T-statistic: {t_stat:.4f}, p-value: {p_val:.6f}")

# Confidence interval
se = np.sqrt(treated.var()/len(treated) + control.var()/len(control))
ci_lower = naive_diff - 1.96 * se
ci_upper = naive_diff + 1.96 * se
print(f"95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")

print("\n" + "=" * 70)
print("ANALYSIS 2: REGRESSION ADJUSTMENT FOR BASELINE Y")
print("=" * 70)

# Implement OLS regression manually: z ~ x + y
# y = X * beta + e, where X = [1, x, y]

n = len(df)
X = np.column_stack([np.ones(n), df['x'].values, df['y'].values])
y = df['z'].values

# OLS: beta = (X'X)^{-1} X'y
XtX = X.T @ X
Xty = X.T @ y
beta = np.linalg.solve(XtX, Xty)

# Residuals and standard errors
y_pred = X @ beta
residuals = y - y_pred
rss = np.sum(residuals**2)
mse = rss / (n - 3)
var_beta = mse * np.linalg.inv(XtX)
se_beta = np.sqrt(np.diag(var_beta))

# t-statistics and p-values
t_stats = beta / se_beta
p_vals = 2 * (1 - stats.t.cdf(np.abs(t_stats), n - 3))

# R-squared
ss_tot = np.sum((y - y.mean())**2)
ss_res = rss
r_squared = 1 - ss_res / ss_tot

print("\nRegression: z ~ x + y")
print(f"{'Variable':<10} {'Coef':>12} {'Std Err':>12} {'t-stat':>12} {'p-value':>12}")
print("-" * 50)
print(f"{'Intercept':<10} {beta[0]:12.4f} {se_beta[0]:12.4f} {t_stats[0]:12.4f} {p_vals[0]:12.6f}")
print(f"{'x':<10} {beta[1]:12.4f} {se_beta[1]:12.4f} {t_stats[1]:12.4f} {p_vals[1]:12.6f}")
print(f"{'y':<10} {beta[2]:12.4f} {se_beta[2]:12.4f} {t_stats[2]:12.4f} {p_vals[2]:12.6f}")
print(f"\nR-squared: {r_squared:.4f}")

coef_x_adj1 = beta[1]
se_x_adj1 = se_beta[1]

print(f"\nCoefficient on x (adjusted for y): {coef_x_adj1:.4f}")
print(f"Standard error: {se_x_adj1:.4f}")
ci_lower_adj = coef_x_adj1 - 1.96 * se_x_adj1
ci_upper_adj = coef_x_adj1 + 1.96 * se_x_adj1
print(f"95% CI: [{ci_lower_adj:.4f}, {ci_upper_adj:.4f}]")

print("\n" + "=" * 70)
print("ANALYSIS 3: REGRESSION WITH INTERACTION (y effect may differ by treatment)")
print("=" * 70)

# z ~ x + y + x*y
# X = [1, x, y, x*y]
X_inter = np.column_stack([np.ones(n), df['x'].values, df['y'].values, 
                           (df['x'] * df['y']).values])

XtX_inter = X_inter.T @ X_inter
Xty_inter = X_inter.T @ y
beta_inter = np.linalg.solve(XtX_inter, Xty_inter)

y_pred_inter = X_inter @ beta_inter
residuals_inter = y - y_pred_inter
rss_inter = np.sum(residuals_inter**2)
mse_inter = rss_inter / (n - 4)
var_beta_inter = mse_inter * np.linalg.inv(XtX_inter)
se_beta_inter = np.sqrt(np.diag(var_beta_inter))
t_stats_inter = beta_inter / se_beta_inter
p_vals_inter = 2 * (1 - stats.t.cdf(np.abs(t_stats_inter), n - 4))
r_squared_inter = 1 - rss_inter / ss_tot

print("\nRegression: z ~ x + y + x:y (with interaction)")
print(f"{'Variable':<10} {'Coef':>12} {'Std Err':>12} {'t-stat':>12} {'p-value':>12}")
print("-" * 50)
print(f"{'Intercept':<10} {beta_inter[0]:12.4f} {se_beta_inter[0]:12.4f} {t_stats_inter[0]:12.4f} {p_vals_inter[0]:12.6f}")
print(f"{'x':<10} {beta_inter[1]:12.4f} {se_beta_inter[1]:12.4f} {t_stats_inter[1]:12.4f} {p_vals_inter[1]:12.6f}")
print(f"{'y':<10} {beta_inter[2]:12.4f} {se_beta_inter[2]:12.4f} {t_stats_inter[2]:12.4f} {p_vals_inter[2]:12.6f}")
print(f"{'x:y':<10} {beta_inter[3]:12.4f} {se_beta_inter[3]:12.4f} {t_stats_inter[3]:12.4f} {p_vals_inter[3]:12.6f}")
print(f"\nR-squared: {r_squared_inter:.4f}")

coef_x_inter = beta_inter[1]
print(f"\nCoefficient on x (main effect, with interaction): {coef_x_inter:.4f}")

print("\n" + "=" * 70)
print("ANALYSIS 4: COVARIATE BALANCE CHECK")
print("=" * 70)

print(f"\nDifference in baseline y by treatment:")
diff_y = df[df['x']==1]['y'].mean() - df[df['x']==0]['y'].mean()
print(f"Mean y treated: {df[df['x']==1]['y'].mean():.4f}")
print(f"Mean y control: {df[df['x']==0]['y'].mean():.4f}")
print(f"Difference: {diff_y:.4f}")

var_treated_y = df[df['x']==1]['y'].var()
var_control_y = df[df['x']==0]['y'].var()
pooled_sd_y = np.sqrt((var_treated_y + var_control_y) / 2)
d_y = diff_y / pooled_sd_y
print(f"Cohen's d for baseline y: {d_y:.4f}")

print("\n" + "=" * 70)
print("ANALYSIS 5: CORRELATION BETWEEN Y AND Z")
print("=" * 70)

corr_y_z = np.corrcoef(df['y'], df['z'])[0, 1]
print(f"\nCorrelation between y and z (overall): {corr_y_z:.4f}")

corr_y_z_treated = np.corrcoef(df[df['x']==1]['y'], df[df['x']==1]['z'])[0, 1]
corr_y_z_control = np.corrcoef(df[df['x']==0]['y'], df[df['x']==0]['z'])[0, 1]
print(f"Correlation between y and z (treated): {corr_y_z_treated:.4f}")
print(f"Correlation between y and z (control): {corr_y_z_control:.4f}")

print("\n" + "=" * 70)
print("ANALYSIS 6: STRATIFIED ANALYSIS BY BASELINE Y QUINTILES")
print("=" * 70)

df['y_quintile'] = pd.qcut(df['y'], q=5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])

print("\nTreatment effect by baseline y quintile:")
print(f"{'Quintile':<10} {'Effect':>10} {'n_treated':>12} {'n_control':>12}")
print("-" * 50)
quintile_effects = []
for quintile in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
    subset = df[df['y_quintile'] == quintile]
    treated_subset = subset[subset['x'] == 1]['z'].mean() if len(subset[subset['x']==1]) > 0 else 0
    control_subset = subset[subset['x'] == 0]['z'].mean() if len(subset[subset['x']==0]) > 0 else 0
    diff = treated_subset - control_subset
    n_treated = len(subset[subset['x'] == 1])
    n_control = len(subset[subset['x'] == 0])
    quintile_effects.append(diff)
    print(f"{quintile:<10} {diff:10.4f} {n_treated:12d} {n_control:12d}")

print("\n" + "=" * 70)
print("SUMMARY OF KEY FINDINGS")
print("=" * 70)
print(f"\nNaive difference (biased): {naive_diff:.4f}")
print(f"Adjusted for baseline y: {coef_x_adj1:.4f}")
print(f"With interaction: {coef_x_inter:.4f}")
print(f"\nStratified effects (Q3-Q5 where treatment exists):")
print(f"  Q3: {quintile_effects[2]:.4f}")
print(f"  Q4: {quintile_effects[3]:.4f}")
print(f"  Q5: {quintile_effects[4]:.4f}")
print(f"  Average of Q3-Q5: {np.mean(quintile_effects[2:]):.4f}")
