import pandas as pd
import numpy as np
from scipy import stats

# Read the data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

# Display basic information
print("=" * 70)
print("DATA OVERVIEW")
print("=" * 70)
print(f"Total number of students: {len(df)}")
print(f"Number who attended tutoring (x=1): {(df['x'] == 1).sum()}")
print(f"Number who did not attend (x=0): {(df['x'] == 0).sum()}")
print()

# Separate groups
treated = df[df['x'] == 1]['z']
control = df[df['x'] == 0]['z']

print("=" * 70)
print("DESCRIPTIVE STATISTICS FOR SCORE GAINS (z)")
print("=" * 70)
print("\nTreated group (attended tutoring, x=1):")
print(f"  n = {len(treated)}")
print(f"  Mean gain = {treated.mean():.4f}")
print(f"  Std Dev = {treated.std():.4f}")
print(f"  Min = {treated.min():.4f}")
print(f"  Max = {treated.max():.4f}")
print(f"  Median = {treated.median():.4f}")

print("\nControl group (did not attend tutoring, x=0):")
print(f"  n = {len(control)}")
print(f"  Mean gain = {control.mean():.4f}")
print(f"  Std Dev = {control.std():.4f}")
print(f"  Min = {control.min():.4f}")
print(f"  Max = {control.max():.4f}")
print(f"  Median = {control.median():.4f}")

print("\n" + "=" * 70)
print("TREATMENT EFFECT ESTIMATE")
print("=" * 70)
difference = treated.mean() - control.mean()
print(f"\nMean score gain (treated) - Mean score gain (control):")
print(f"  {treated.mean():.4f} - {control.mean():.4f} = {difference:.4f}")

print("\n" + "=" * 70)
print("INDEPENDENT SAMPLES T-TEST")
print("=" * 70)
t_stat, p_value = stats.ttest_ind(treated, control)
print(f"t-statistic: {t_stat:.4f}")
print(f"p-value: {p_value:.6f}")
print(f"Statistical significance at 0.05 level: {'YES' if p_value < 0.05 else 'NO'}")

# Calculate 95% confidence interval for the difference
pooled_std = np.sqrt(((len(treated)-1)*treated.std()**2 + (len(control)-1)*control.std()**2) / (len(treated) + len(control) - 2))
se_diff = pooled_std * np.sqrt(1/len(treated) + 1/len(control))
df_denom = len(treated) + len(control) - 2
t_crit = stats.t.ppf(0.975, df_denom)
ci_lower = difference - t_crit * se_diff
ci_upper = difference + t_crit * se_diff

print(f"\n95% Confidence Interval for the difference:")
print(f"  [{ci_lower:.4f}, {ci_upper:.4f}]")

print("\n" + "=" * 70)
print("DATA QUALITY CHECKS")
print("=" * 70)
print(f"Missing values in x: {df['x'].isna().sum()}")
print(f"Missing values in y: {df['y'].isna().sum()}")
print(f"Missing values in z: {df['z'].isna().sum()}")
print(f"Valid rows: {len(df)}")

# Save results to file
with open('/home/claude/submission/results/analysis_results.txt', 'w') as f:
    f.write("TUTORING STUDY ANALYSIS\n")
    f.write("="*70 + "\n\n")
    f.write(f"Total students: {len(df)}\n")
    f.write(f"Treated (attended tutoring): {len(treated)}\n")
    f.write(f"Control (no tutoring): {len(control)}\n\n")
    f.write("DESCRIPTIVE STATISTICS\n")
    f.write("-"*70 + "\n")
    f.write(f"Treated group mean score gain: {treated.mean():.4f}\n")
    f.write(f"Control group mean score gain: {control.mean():.4f}\n")
    f.write(f"Difference in means: {difference:.4f}\n\n")
    f.write("STATISTICAL TEST\n")
    f.write("-"*70 + "\n")
    f.write(f"t-statistic: {t_stat:.4f}\n")
    f.write(f"p-value: {p_value:.6f}\n")
    f.write(f"95% CI for difference: [{ci_lower:.4f}, {ci_upper:.4f}]\n")
