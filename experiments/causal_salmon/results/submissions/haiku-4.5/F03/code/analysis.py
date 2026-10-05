import pandas as pd
import numpy as np
from scipy import stats
import json

# Load the data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

# Basic data checks
print("="*70)
print("DATA OVERVIEW")
print("="*70)
print(f"Total number of students: {len(df)}")
print(f"Number of columns: {len(df.columns)}")
print(f"Column names: {list(df.columns)}")
print(f"\nData shape: {df.shape}")
print(f"Missing values: {df.isnull().sum().sum()}")
print(f"\nFirst few rows:\n{df.head()}")

# Separate treated and control groups
treated = df[df['x'] == 1]
control = df[df['x'] == 0]

print("\n" + "="*70)
print("GROUP COMPOSITION")
print("="*70)
print(f"Students who attended tutoring (x=1): {len(treated)}")
print(f"Students who did not attend (x=0): {len(control)}")
print(f"Total: {len(treated) + len(control)}")

# Descriptive statistics for score gain (z) by group
print("\n" + "="*70)
print("SCORE GAIN (z) BY GROUP - DESCRIPTIVE STATISTICS")
print("="*70)

print("\nTREATED GROUP (attended tutoring):")
print(f"  Mean score gain: {treated['z'].mean():.6f}")
print(f"  Median score gain: {treated['z'].median():.6f}")
print(f"  Std Dev: {treated['z'].std():.6f}")
print(f"  Min: {treated['z'].min():.6f}")
print(f"  Max: {treated['z'].max():.6f}")
print(f"  N: {len(treated)}")

print("\nCONTROL GROUP (did not attend tutoring):")
print(f"  Mean score gain: {control['z'].mean():.6f}")
print(f"  Median score gain: {control['z'].median():.6f}")
print(f"  Std Dev: {control['z'].std():.6f}")
print(f"  Min: {control['z'].min():.6f}")
print(f"  Max: {control['z'].max():.6f}")
print(f"  N: {len(control)}")

# Treatment effect (simple difference in means)
mean_diff = treated['z'].mean() - control['z'].mean()
print("\n" + "="*70)
print("TREATMENT EFFECT (DIFFERENCE IN MEANS)")
print("="*70)
print(f"Mean score gain (treated) - Mean score gain (control): {mean_diff:.6f}")

# Independent samples t-test
print("\n" + "="*70)
print("INDEPENDENT SAMPLES T-TEST")
print("="*70)
t_stat, p_value = stats.ttest_ind(treated['z'], control['z'])
print(f"t-statistic: {t_stat:.6f}")
print(f"p-value (two-tailed): {p_value:.6f}")

# Calculate 95% confidence interval for the difference
se_diff = np.sqrt(treated['z'].var(ddof=1)/len(treated) + control['z'].var(ddof=1)/len(control))
df_welch = ((treated['z'].var(ddof=1)/len(treated) + control['z'].var(ddof=1)/len(control))**2) / \
           ((treated['z'].var(ddof=1)/len(treated))**2/(len(treated)-1) + 
            (control['z'].var(ddof=1)/len(control))**2/(len(control)-1))
t_crit = stats.t.ppf(0.975, df_welch)
ci_lower = mean_diff - t_crit * se_diff
ci_upper = mean_diff + t_crit * se_diff

print(f"Standard error of difference: {se_diff:.6f}")
print(f"95% Confidence Interval for treatment effect: [{ci_lower:.6f}, {ci_upper:.6f}]")

# Check statistical significance
if p_value < 0.05:
    print(f"\nStatistically significant at α = 0.05 level: YES")
else:
    print(f"\nStatistically significant at α = 0.05 level: NO")

# Effect size (Cohen's d)
pooled_std = np.sqrt(((len(treated)-1)*treated['z'].var(ddof=1) + 
                       (len(control)-1)*control['z'].var(ddof=1)) / 
                      (len(treated) + len(control) - 2))
cohens_d = mean_diff / pooled_std
print(f"Cohen's d (effect size): {cohens_d:.6f}")

# Store results for reporting
results = {
    'total_students': len(df),
    'treated_count': len(treated),
    'control_count': len(control),
    'treated_mean': treated['z'].mean(),
    'control_mean': control['z'].mean(),
    'treatment_effect': mean_diff,
    'ci_lower': ci_lower,
    'ci_upper': ci_upper,
    'p_value': p_value,
    'cohens_d': cohens_d,
    't_statistic': t_stat
}

# Save results as JSON
with open('/home/claude/analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "="*70)
print("Analysis complete. Results saved.")
print("="*70)
