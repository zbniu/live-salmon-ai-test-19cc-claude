"""
Analysis of the randomized study on the effect of arrangement Q on change z.

Research question: For the units that received arrangement Q, did receiving 
arrangement Q increase their change z? If so, by how much?
"""

import pandas as pd
import numpy as np
from scipy import stats
import json

# Load data
data = pd.read_csv('/mnt/user-data/uploads/data.csv')

print("=" * 70)
print("DATA SUMMARY")
print("=" * 70)
print(f"Total rows: {len(data)}")
print(f"Columns: {list(data.columns)}")
print(f"\nFirst few rows:")
print(data.head())
print(f"\nData shape: {data.shape}")
print(f"Missing values: {data.isnull().sum().sum()}")

# Check randomization
print("\n" + "=" * 70)
print("RANDOMIZATION CHECK")
print("=" * 70)

treatment_count = (data['x'] == 1).sum()
control_count = (data['x'] == 0).sum()

print(f"Treatment group (x=1): {treatment_count}")
print(f"Control group (x=0): {control_count}")
print(f"Expected treatment group: 600")
print(f"Expected control group: 1400")

# Check balance on baseline covariate y
print("\n" + "=" * 70)
print("COVARIATE BALANCE (Baseline y)")
print("=" * 70)

y_treatment = data[data['x'] == 1]['y']
y_control = data[data['x'] == 0]['y']

print(f"\nTreatment group (x=1):")
print(f"  Mean: {y_treatment.mean():.6f}")
print(f"  SD: {y_treatment.std():.6f}")
print(f"  N: {len(y_treatment)}")

print(f"\nControl group (x=0):")
print(f"  Mean: {y_control.mean():.6f}")
print(f"  SD: {y_control.std():.6f}")
print(f"  N: {len(y_control)}")

# t-test for balance
t_stat_y, p_val_y = stats.ttest_ind(y_treatment, y_control)
print(f"\nt-test for balance on y:")
print(f"  t-statistic: {t_stat_y:.6f}")
print(f"  p-value: {p_val_y:.6f}")
print(f"  Difference in means: {y_treatment.mean() - y_control.mean():.6f}")

# PRIMARY ANALYSIS: Effect on z
print("\n" + "=" * 70)
print("PRIMARY ANALYSIS: EFFECT OF ARRANGEMENT Q ON CHANGE z")
print("=" * 70)

z_treatment = data[data['x'] == 1]['z']
z_control = data[data['x'] == 0]['z']

print(f"\nTreatment group (x=1):")
print(f"  Mean z: {z_treatment.mean():.6f}")
print(f"  SD: {z_treatment.std():.6f}")
print(f"  Median: {z_treatment.median():.6f}")
print(f"  Min: {z_treatment.min():.6f}")
print(f"  Max: {z_treatment.max():.6f}")
print(f"  N: {len(z_treatment)}")

print(f"\nControl group (x=0):")
print(f"  Mean z: {z_control.mean():.6f}")
print(f"  SD: {z_control.std():.6f}")
print(f"  Median: {z_control.median():.6f}")
print(f"  Min: {z_control.min():.6f}")
print(f"  Max: {z_control.max():.6f}")
print(f"  N: {len(z_control)}")

# Average Treatment Effect (ATE)
ate = z_treatment.mean() - z_control.mean()
print(f"\n" + "=" * 70)
print(f"AVERAGE TREATMENT EFFECT (ATE)")
print("=" * 70)
print(f"\nATE = Mean(z | x=1) - Mean(z | x=0)")
print(f"ATE = {z_treatment.mean():.6f} - {z_control.mean():.6f}")
print(f"ATE = {ate:.6f}")

# Confidence interval and statistical test for the effect
# Using two-sample t-test
t_stat_z, p_val_z = stats.ttest_ind(z_treatment, z_control)

# Calculate standard error
n_t = len(z_treatment)
n_c = len(z_control)
s_t = z_treatment.std(ddof=1)
s_c = z_control.std(ddof=1)

# Pooled standard error
se_ate = np.sqrt((s_t**2 / n_t) + (s_c**2 / n_c))

# 95% CI
ci_lower = ate - 1.96 * se_ate
ci_upper = ate + 1.96 * se_ate

print(f"\nTwo-sample t-test:")
print(f"  t-statistic: {t_stat_z:.6f}")
print(f"  p-value: {p_val_z:.6f}")
print(f"  Standard error of ATE: {se_ate:.6f}")
print(f"  95% CI: [{ci_lower:.6f}, {ci_upper:.6f}]")

# Interpret the result
print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

if p_val_z < 0.05:
    significance = "statistically significant at the 0.05 level"
else:
    significance = "not statistically significant at the 0.05 level"

if ate > 0:
    direction = "increased"
elif ate < 0:
    direction = "decreased"
else:
    direction = "had no effect on"

print(f"\nArrangement Q {direction} the average change z by {abs(ate):.6f} points.")
print(f"This effect is {significance} (p = {p_val_z:.4f}).")
print(f"\nWith 95% confidence, the true effect lies between {ci_lower:.6f} and {ci_upper:.6f}.")

# Store results for the report
results = {
    'treatment_group_size': int(treatment_count),
    'control_group_size': int(control_count),
    'mean_z_treatment': float(z_treatment.mean()),
    'mean_z_control': float(z_control.mean()),
    'ate': float(ate),
    'standard_error': float(se_ate),
    'ci_lower': float(ci_lower),
    'ci_upper': float(ci_upper),
    't_statistic': float(t_stat_z),
    'p_value': float(p_val_z),
}

# Save results to JSON
with open('/home/claude/submission/results/analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print("Results saved to analysis_results.json")
print("=" * 70)
