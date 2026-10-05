import pandas as pd
import numpy as np
from scipy import stats
import json

# Read the data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

print("="*80)
print("DATA EXPLORATION")
print("="*80)
print(f"\nData shape: {df.shape}")
print(f"\nFirst few rows:")
print(df.head())
print(f"\nData types:")
print(df.dtypes)
print(f"\nBasic statistics:")
print(df.describe())

# Check for missing values
print(f"\nMissing values: {df.isnull().sum().sum()}")

# Treatment counts
print(f"\nTreatment assignment:")
print(f"  Control (x=0): {(df['x']==0).sum()}")
print(f"  Treatment (x=1): {(df['x']==1).sum()}")

print("\n" + "="*80)
print("NAIVE COMPARISON (Biased)")
print("="*80)

# Naive comparison (biased due to selection)
control = df[df['x'] == 0]
treatment = df[df['x'] == 1]

z_control = control['z']
z_treatment = treatment['z']

naive_diff = z_treatment.mean() - z_control.mean()
print(f"\nMean score gain for control (no tutoring): {z_control.mean():.4f}")
print(f"Mean score gain for treatment (tutoring): {z_treatment.mean():.4f}")
print(f"Naive difference: {naive_diff:.4f}")

# T-test
t_stat, p_val = stats.ttest_ind(z_treatment, z_control)
print(f"\nT-test for difference in means:")
print(f"  t-statistic: {t_stat:.4f}")
print(f"  p-value: {p_val:.6f}")

# But this is biased! Let's check the confounding
print(f"\nStart-of-term score (y) by group:")
print(f"  Control mean y: {control['y'].mean():.4f}")
print(f"  Treatment mean y: {treatment['y'].mean():.4f}")
print(f"  Difference in y: {treatment['y'].mean() - control['y'].mean():.4f}")

# Correlation between y and z
print(f"\nCorrelation between start score (y) and score gain (z): {df['y'].corr(df['z']):.4f}")

print("\n" + "="*80)
print("APPROACH 1: Stratification by start score")
print("="*80)

# Stratify by start score and compute effect within strata
df['y_quintile'] = pd.qcut(df['y'], q=5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])

stratified_effects = []
for stratum in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
    subset = df[df['y_quintile'] == stratum]
    z_ctrl = subset[subset['x'] == 0]['z'].mean()
    z_trt = subset[subset['x'] == 1]['z'].mean()
    effect = z_trt - z_ctrl
    n_ctrl = (subset['x'] == 0).sum()
    n_trt = (subset['x'] == 1).sum()
    stratified_effects.append({
        'stratum': stratum,
        'effect': effect,
        'n_control': n_ctrl,
        'n_treatment': n_trt,
        'mean_y_control': subset[subset['x']==0]['y'].mean(),
        'mean_y_treatment': subset[subset['x']==1]['y'].mean()
    })
    print(f"\n{stratum}:")
    print(f"  Control n={n_ctrl}, mean z gain={z_ctrl:.4f}")
    print(f"  Treatment n={n_trt}, mean z gain={z_trt:.4f}")
    print(f"  Effect: {effect:.4f}")

# Stratified estimate (simple average across strata)
simple_stratified = np.mean([e['effect'] for e in stratified_effects])
print(f"\nSimple average of stratum-specific effects: {simple_stratified:.4f}")

# Stratified estimate weighted by stratum size
weights = [e['n_control'] + e['n_treatment'] for e in stratified_effects]
total_n = sum(weights)
weighted_stratified = sum(e['effect'] * w / total_n for e, w in zip(stratified_effects, weights))
print(f"Weighted average (by stratum size): {weighted_stratified:.4f}")

print("\n" + "="*80)
print("APPROACH 2: Linear regression adjusting for y")
print("="*80)

from sklearn.linear_model import LinearRegression

# Simple linear regression of z on x
X_simple = df[['x']].values
y_values = df['z'].values
model_simple = LinearRegression().fit(X_simple, y_values)
print(f"\nSimple regression z ~ x:")
print(f"  Coefficient on x: {model_simple.coef_[0]:.4f}")
print(f"  Intercept: {model_simple.intercept_:.4f}")

# Linear regression of z on x and y
X_adjusted = df[['x', 'y']].values
model_adjusted = LinearRegression().fit(X_adjusted, y_values)
print(f"\nAdjusted regression z ~ x + y:")
print(f"  Coefficient on x: {model_adjusted.coef_[0]:.4f}")
print(f"  Coefficient on y: {model_adjusted.coef_[1]:.4f}")
print(f"  Intercept: {model_adjusted.intercept_:.4f}")

# R-squared
from sklearn.metrics import r2_score
r2_simple = r2_score(y_values, model_simple.predict(X_simple))
r2_adjusted = r2_score(y_values, model_adjusted.predict(X_adjusted))
print(f"\nR-squared:")
print(f"  Simple model: {r2_simple:.4f}")
print(f"  Adjusted model: {r2_adjusted:.4f}")

print("\n" + "="*80)
print("APPROACH 3: Examining the treatment assignment mechanism")
print("="*80)

# The selection rule: top 900 got application scores (y + random), 
# then top 600 of those by y got admitted.
# Let's see if we can detect the cutoff

# Group students by treatment
sorted_y_control = sorted(df[df['x']==0]['y'].values)
sorted_y_treatment = sorted(df[df['x']==1]['y'].values)

print(f"\nStart score (y) distribution:")
print(f"  Control: min={sorted_y_control[0]:.2f}, max={sorted_y_control[-1]:.2f}, median={np.median(sorted_y_control):.2f}")
print(f"  Treatment: min={sorted_y_treatment[0]:.2f}, max={sorted_y_treatment[-1]:.2f}, median={np.median(sorted_y_treatment):.2f}")

# There should be a threshold around where treatment starts
threshold_candidates = np.linspace(50, 70, 20)
print(f"\nChecking for treatment threshold:")
for threshold in threshold_candidates:
    above = (df['y'] >= threshold).sum()
    above_treated = ((df['y'] >= threshold) & (df['x'] == 1)).sum()
    if above > 0:
        pct_treated = 100 * above_treated / above
        print(f"  y >= {threshold:.1f}: {above} students, {pct_treated:.1f}% treated")

print("\n" + "="*80)
print("APPROACH 4: Regression discontinuity (if threshold exists)")
print("="*80)

# The selection rule was: top 900 applicants by (y + random noise) and 
# top 600 of them by y. This is complex, but there should be a discontinuity.
# Let's use local linear regression around potential thresholds

from scipy.ndimage import uniform_filter1d

# Sort by y
df_sorted = df.sort_values('y').reset_index(drop=True)

# Compute local means around each y value
window_size = 50
z_smooth = uniform_filter1d(df_sorted['z'].values, size=window_size, mode='nearest')

# Check for discontinuity
print(f"\nLooking for discontinuity in score gains...")

# For each unique treatment value, check where it clusters
y_at_treatment_change = df_sorted.loc[df_sorted['x'].diff() != 0, 'y'].values
print(f"Y values where treatment status changes: {sorted(y_at_treatment_change)[:20]}...")

print("\n" + "="*80)
print("SUMMARY STATISTICS FOR REPORT")
print("="*80)

results_summary = {
    'naive_difference': float(naive_diff),
    'naive_t_stat': float(t_stat),
    'naive_p_value': float(p_val),
    'simple_linear_x_coeff': float(model_simple.coef_[0]),
    'adjusted_linear_x_coeff': float(model_adjusted.coef_[0]),
    'adjusted_linear_y_coeff': float(model_adjusted.coef_[1]),
    'stratified_simple_avg': float(simple_stratified),
    'stratified_weighted_avg': float(weighted_stratified),
    'control_mean_z': float(z_control.mean()),
    'treatment_mean_z': float(z_treatment.mean()),
    'control_mean_y': float(control['y'].mean()),
    'treatment_mean_y': float(treatment['y'].mean()),
    'correlation_y_z': float(df['y'].corr(df['z'])),
    'n_control': int((df['x']==0).sum()),
    'n_treatment': int((df['x']==1).sum())
}

print("\nKey Results:")
for key, value in results_summary.items():
    print(f"  {key}: {value}")

# Save results
with open('/home/claude/analysis_results.json', 'w') as f:
    json.dump(results_summary, f, indent=2)

