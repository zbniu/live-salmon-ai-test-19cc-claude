#!/usr/bin/env python3
"""
Analysis 1: Exploratory Analysis of Treatment Assignment and Outcome
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Load data
data = pd.read_csv('/mnt/user-data/uploads/data.csv')

print("="*70)
print("EXPLORATORY ANALYSIS")
print("="*70)

# 1. Understand the assignment mechanism
print("\n1. TREATMENT ASSIGNMENT ANALYSIS")
print("-"*70)

# Sort by baseline to understand the assignment pattern
sorted_data = data.sort_values('y').reset_index(drop=True)

# Find where treatment transitions occur
treatment_by_y = sorted_data.groupby('x').agg({
    'y': ['min', 'max', 'mean', 'count'],
    'z': 'mean'
}).round(3)
print("\nTreatment by baseline (y) range:")
print(treatment_by_y)

# Check if there's a clear cutoff
y_min_treated = data[data['x']==1]['y'].min()
y_max_control = data[data['x']==0]['y'].max()

print(f"\nMinimum baseline for treated units: {y_min_treated:.3f}")
print(f"Maximum baseline for control units: {y_max_control:.3f}")
print(f"Overlap in baseline? {y_min_treated < y_max_control}")

# Visualize the distribution
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].hist(data[data['x']==0]['y'], bins=30, alpha=0.6, label='Control', color='blue')
axes[0].hist(data[data['x']==1]['y'], bins=30, alpha=0.6, label='Treatment', color='red')
axes[0].set_xlabel('Baseline Measurement (y)')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Baseline Distribution by Treatment Group')
axes[0].legend()
axes[0].grid(alpha=0.3)

axes[1].scatter(data[data['x']==0]['y'], data[data['x']==0]['z'], alpha=0.4, s=20, label='Control', color='blue')
axes[1].scatter(data[data['x']==1]['y'], data[data['x']==1]['z'], alpha=0.4, s=20, label='Treatment', color='red')
axes[1].set_xlabel('Baseline Measurement (y)')
axes[1].set_ylabel('Change (z)')
axes[1].set_title('Outcome vs Baseline by Treatment Group')
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('/home/claude/submission/results/01_assignment_and_outcome.png', dpi=100, bbox_inches='tight')
print("\n✓ Saved: 01_assignment_and_outcome.png")
plt.close()

# 2. Naive comparison (biased)
print("\n2. NAIVE COMPARISON (BIASED - confounded by baseline)")
print("-"*70)

mean_z_control = data[data['x']==0]['z'].mean()
mean_z_treated = data[data['x']==1]['z'].mean()
naive_diff = mean_z_treated - mean_z_control

print(f"Control group mean z: {mean_z_control:.4f}")
print(f"Treatment group mean z: {mean_z_treated:.4f}")
print(f"Naive difference: {naive_diff:.4f}")

# Test if significant
t_stat, p_val = stats.ttest_ind(data[data['x']==1]['z'], data[data['x']==0]['z'])
print(f"T-test p-value: {p_val:.6f}")
print("\nNote: This comparison is BIASED because treatment was assigned based on baseline (y),")
print("and baseline is strongly related to the outcome.")

# 3. Relationship between baseline and outcome
print("\n3. RELATIONSHIP BETWEEN BASELINE AND OUTCOME")
print("-"*70)

# Check relationship between y and z
correlation = data['y'].corr(data['z'])
print(f"Correlation between baseline (y) and change (z): {correlation:.4f}")

# Regression of z on y (ignoring treatment for now)
from sklearn.linear_model import LinearRegression
X_baseline = data[['y']].values
y_outcome = data['z'].values

model_baseline = LinearRegression()
model_baseline.fit(X_baseline, y_outcome)
coef_baseline = model_baseline.coef_[0]
intercept_baseline = model_baseline.intercept_

print(f"\nRegression: z = {intercept_baseline:.4f} + {coef_baseline:.4f} * y")
print(f"R-squared: {model_baseline.score(X_baseline, y_outcome):.4f}")

# Plot the relationship
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(data[data['x']==0]['y'], data[data['x']==0]['z'], 
           alpha=0.4, s=30, label='Control (x=0)', color='blue')
ax.scatter(data[data['x']==1]['y'], data[data['x']==1]['z'], 
           alpha=0.4, s=30, label='Treatment (x=1)', color='red')

# Add fitted line
y_line = np.linspace(data['y'].min(), data['y'].max(), 100)
z_line = intercept_baseline + coef_baseline * y_line
ax.plot(y_line, z_line, 'k--', linewidth=2, label='Fitted line: z = f(y)')

ax.set_xlabel('Baseline Measurement (y)', fontsize=11)
ax.set_ylabel('Change (z)', fontsize=11)
ax.set_title('Outcome vs Baseline with Fitted Line', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('/home/claude/submission/results/02_baseline_outcome_relationship.png', dpi=100, bbox_inches='tight')
print("\n✓ Saved: 02_baseline_outcome_relationship.png")
plt.close()
