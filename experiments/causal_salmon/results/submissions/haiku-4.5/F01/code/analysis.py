import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Load data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

# Basic exploration
print("=" * 60)
print("DATA EXPLORATION")
print("=" * 60)
print(f"\nDataset shape: {df.shape}")
print(f"\nFirst few rows:\n{df.head()}")
print(f"\nData types:\n{df.dtypes}")
print(f"\nBasic statistics:\n{df.describe()}")

# Check for missing values
print(f"\nMissing values:\n{df.isnull().sum()}")

# Treatment group sizes
print(f"\n\nTREATMENT GROUP COMPOSITION")
print("=" * 60)
print(f"Students who attended tutoring (x=1): {(df['x'] == 1).sum()}")
print(f"Students who did not attend (x=0): {(df['x'] == 0).sum()}")
print(f"Total: {len(df)}")

# Examine the distribution of y (start-of-term score) by treatment group
print(f"\n\nDISTRIBUTION OF START-OF-TERM SCORES (y) BY GROUP")
print("=" * 60)

treated = df[df['x'] == 1]['y']
control = df[df['x'] == 0]['y']

print(f"\nTreated group (attended tutoring):")
print(f"  Count: {len(treated)}")
print(f"  Mean: {treated.mean():.4f}")
print(f"  Std Dev: {treated.std():.4f}")
print(f"  Min: {treated.min():.4f}")
print(f"  Max: {treated.max():.4f}")
print(f"  Median: {treated.median():.4f}")

print(f"\nControl group (did not attend):")
print(f"  Count: {len(control)}")
print(f"  Mean: {control.mean():.4f}")
print(f"  Std Dev: {control.std():.4f}")
print(f"  Min: {control.min():.4f}")
print(f"  Max: {control.max():.4f}")
print(f"  Median: {control.median():.4f}")

print(f"\nDifference in mean y: {treated.mean() - control.mean():.4f}")

# Check for a potential cutoff (since admission was in descending order of y)
print(f"\n\nCHECKING FOR ADMISSION CUTOFF")
print("=" * 60)
print(f"Maximum y in control group: {control.max():.4f}")
print(f"Minimum y in treated group: {treated.min():.4f}")
print(f"The treated group has higher y scores on average, suggesting selection.")

# Simple comparison of score gains
print(f"\n\nSCORE GAINS (z) BY GROUP - RAW COMPARISON")
print("=" * 60)

treated_z = df[df['x'] == 1]['z']
control_z = df[df['x'] == 0]['z']

print(f"\nTreated group (attended tutoring):")
print(f"  Mean score gain (z): {treated_z.mean():.4f}")
print(f"  Std Dev: {treated_z.std():.4f}")
print(f"  Median: {treated_z.median():.4f}")
print(f"  Min: {treated_z.min():.4f}")
print(f"  Max: {treated_z.max():.4f}")

print(f"\nControl group (did not attend):")
print(f"  Mean score gain (z): {control_z.mean():.4f}")
print(f"  Std Dev: {control_z.std():.4f}")
print(f"  Median: {control_z.median():.4f}")
print(f"  Min: {control_z.min():.4f}")
print(f"  Max: {control_z.max():.4f}")

raw_difference = treated_z.mean() - control_z.mean()
print(f"\nRaw difference (Treated - Control): {raw_difference:.4f}")

# T-test for raw difference
t_stat, p_value = stats.ttest_ind(treated_z, control_z)
print(f"T-test: t={t_stat:.4f}, p-value={p_value:.6f}")

# REGRESSION ANALYSIS: z ~ x (unadjusted)
print(f"\n\nREGRESSION: Score Gain (z) ~ Tutoring (x) - Unadjusted")
print("=" * 60)

X_unadjusted = np.column_stack([np.ones(len(df)), df['x']])
y = df['z'].values
beta_unadjusted = np.linalg.lstsq(X_unadjusted, y, rcond=None)[0]
residuals_unadjusted = y - X_unadjusted @ beta_unadjusted
rss_unadjusted = np.sum(residuals_unadjusted ** 2)
mse_unadjusted = rss_unadjusted / (len(df) - 2)
var_covar_unadjusted = mse_unadjusted * np.linalg.inv(X_unadjusted.T @ X_unadjusted)
se_unadjusted = np.sqrt(np.diag(var_covar_unadjusted))
t_stats_unadjusted = beta_unadjusted / se_unadjusted
p_values_unadjusted = 2 * (1 - stats.t.cdf(np.abs(t_stats_unadjusted), len(df) - 2))

print(f"\nIntercept (mean gain for control): {beta_unadjusted[0]:.4f}")
print(f"  SE: {se_unadjusted[0]:.4f}, t={t_stats_unadjusted[0]:.4f}, p={p_values_unadjusted[0]:.6f}")
print(f"\nEffect of tutoring (x=1 vs x=0): {beta_unadjusted[1]:.4f}")
print(f"  SE: {se_unadjusted[1]:.4f}, t={t_stats_unadjusted[1]:.4f}, p={p_values_unadjusted[1]:.6f}")

r_squared_unadjusted = 1 - (rss_unadjusted / np.sum((y - y.mean()) ** 2))
print(f"R-squared: {r_squared_unadjusted:.6f}")

# REGRESSION ANALYSIS: z ~ x + y (adjusted for start-of-term score)
print(f"\n\nREGRESSION: Score Gain (z) ~ Tutoring (x) + Start Score (y) - Adjusted")
print("=" * 60)

X_adjusted = np.column_stack([np.ones(len(df)), df['x'], df['y']])
beta_adjusted = np.linalg.lstsq(X_adjusted, y, rcond=None)[0]
residuals_adjusted = y - X_adjusted @ beta_adjusted
rss_adjusted = np.sum(residuals_adjusted ** 2)
mse_adjusted = rss_adjusted / (len(df) - 3)
var_covar_adjusted = mse_adjusted * np.linalg.inv(X_adjusted.T @ X_adjusted)
se_adjusted = np.sqrt(np.diag(var_covar_adjusted))
t_stats_adjusted = beta_adjusted / se_adjusted
p_values_adjusted = 2 * (1 - stats.t.cdf(np.abs(t_stats_adjusted), len(df) - 3))

print(f"\nIntercept: {beta_adjusted[0]:.4f}")
print(f"  SE: {se_adjusted[0]:.4f}, t={t_stats_adjusted[0]:.4f}, p={p_values_adjusted[0]:.6f}")
print(f"\nEffect of tutoring (x=1 vs x=0): {beta_adjusted[1]:.4f}")
print(f"  SE: {se_adjusted[1]:.4f}, t={t_stats_adjusted[1]:.4f}, p={p_values_adjusted[1]:.6f}")
print(f"\nEffect of start-of-term score (y): {beta_adjusted[2]:.4f}")
print(f"  SE: {se_adjusted[2]:.4f}, t={t_stats_adjusted[2]:.4f}, p={p_values_adjusted[2]:.6f}")

r_squared_adjusted = 1 - (rss_adjusted / np.sum((y - y.mean()) ** 2))
print(f"R-squared: {r_squared_adjusted:.6f}")

# Summary of key findings
print(f"\n\nKEY FINDINGS")
print("=" * 60)
print(f"\n1. Raw (unadjusted) treatment effect: {beta_unadjusted[1]:.4f} points")
print(f"   (Tutoring attendees gained {beta_unadjusted[1]:.4f} more points on average)")
print(f"   Statistical significance: p = {p_values_unadjusted[1]:.6f}")

print(f"\n2. Adjusted treatment effect (controlling for start-of-term score): {beta_adjusted[1]:.4f} points")
print(f"   Statistical significance: p = {p_values_adjusted[1]:.6f}")

print(f"\n3. Relationship between start-of-term score and score gain: {beta_adjusted[2]:.4f}")
print(f"   (Each additional point on start-of-term score is associated with")
print(f"    {beta_adjusted[2]:.4f} points of additional score gain)")

print(f"\n4. Selection bias: Students admitted to tutoring had higher start-of-term")
print(f"   scores on average ({treated.mean():.2f} vs {control.mean():.2f}).")
print(f"   This creates confounding in the unadjusted estimate.")

print(f"\n5. Interpretation: The adjusted estimate suggests the tutoring effect")
print(f"   after accounting for students' incoming ability level.")

