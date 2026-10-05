"""
Basic comparison of score gains by treatment group and analysis of confounding
"""
import pandas as pd
import numpy as np
from scipy import stats

# Load the data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

print("=" * 70)
print("BASIC COMPARISON OF SCORE GAINS BY TREATMENT GROUP")
print("=" * 70)

# Naive comparison
treated = df[df['x'] == 1]
control = df[df['x'] == 0]

print(f"\nTutoring attended (n={len(treated)}):")
print(f"  Mean score gain (z): {treated['z'].mean():.4f}")
print(f"  Std dev: {treated['z'].std():.4f}")
print(f"  Min: {treated['z'].min():.4f}, Max: {treated['z'].max():.4f}")

print(f"\nNo tutoring (n={len(control)}):")
print(f"  Mean score gain (z): {control['z'].mean():.4f}")
print(f"  Std dev: {control['z'].std():.4f}")
print(f"  Min: {control['z'].min():.4f}, Max: {control['z'].max():.4f}")

print(f"\nNaive difference in means (treated - control): {treated['z'].mean() - control['z'].mean():.4f}")

# T-test
t_stat, p_val = stats.ttest_ind(treated['z'], control['z'])
print(f"T-test: t = {t_stat:.4f}, p-value = {p_val:.6f}")

print("\n" + "=" * 70)
print("CONFOUNDING DUE TO SELECTION ON START-OF-TERM SCORES")
print("=" * 70)

print(f"\nStart-of-term scores (y):")
print(f"  Tutoring: mean = {treated['y'].mean():.4f}, std = {treated['y'].std():.4f}")
print(f"  No tutoring: mean = {control['y'].mean():.4f}, std = {control['y'].std():.4f}")
print(f"  Difference: {treated['y'].mean() - control['y'].mean():.4f}")

# Test if mean y differs between groups
t_stat_y, p_val_y = stats.ttest_ind(treated['y'], control['y'])
print(f"  T-test: t = {t_stat_y:.4f}, p-value = {p_val_y:.6e}")

print(f"\nCorrelation between y and z (overall): {df['y'].corr(df['z']):.4f}")
print(f"Correlation between y and z (tutoring): {treated['y'].corr(treated['z']):.4f}")
print(f"Correlation between y and z (no tutoring): {control['y'].corr(control['z']):.4f}")
