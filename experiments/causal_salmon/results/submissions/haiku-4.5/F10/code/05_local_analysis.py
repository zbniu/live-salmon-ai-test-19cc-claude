"""
Local analysis near the selection boundary
"""
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression

# Load the data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

print("=" * 70)
print("LOCAL ANALYSIS NEAR THE SELECTION BOUNDARY")
print("=" * 70)

# The cutoff appears to be around y ~ 66
# Let's use a bandwidth approach for local analysis

# Define bandwidth for local linear regression (Rule of thumb: h ~ 1.06 * sd * n^(-1/5))
h = 1.06 * df['y'].std() * (len(df) ** (-0.2))
print(f"Suggested bandwidth: {h:.4f}")

# Use a wider bandwidth for stability
bandwidth = 5
print(f"Using bandwidth: {bandwidth}")

# Local linear regression near the cutoff
cutoff_approx = 66.02  # The approximate 600th highest score
near_cutoff = df[(df['y'] >= cutoff_approx - bandwidth) & (df['y'] <= cutoff_approx + bandwidth)]
print(f"\nStudents within {bandwidth} points of cutoff: {len(near_cutoff)}")
print(f"Treated: {len(near_cutoff[near_cutoff['x']==1])}, Control: {len(near_cutoff[near_cutoff['x']==0])}")

# Estimate treatment effect at the cutoff using local linear regression
X_local = near_cutoff[['x', 'y']]
y_local = near_cutoff['z']
model_local = LinearRegression().fit(X_local, y_local)

print(f"\nLocal Linear Regression (within ±{bandwidth} of cutoff):")
print(f"  Treatment effect: {model_local.coef_[0]:.4f}")
print(f"  Baseline score effect: {model_local.coef_[1]:.4f}")

# Try different bandwidths for robustness
print(f"\nTreatment effect estimate across different bandwidths:")
for bw in [3, 4, 5, 6, 7, 8]:
    near = df[(df['y'] >= cutoff_approx - bw) & (df['y'] <= cutoff_approx + bw)]
    if len(near) > 10:
        X_bw = near[['x', 'y']]
        y_bw = near['z']
        model_bw = LinearRegression().fit(X_bw, y_bw)
        print(f"  Bandwidth ±{bw}: treatment effect = {model_bw.coef_[0]:.4f} (n={len(near)})")

print("\n" + "=" * 70)
print("SUMMARY OF TREATMENT EFFECT ESTIMATES")
print("=" * 70)

# Compile estimates
print("\n1. Naive comparison (no controls):")
treated = df[df['x'] == 1]
control = df[df['x'] == 0]
print(f"   Effect: {treated['z'].mean() - control['z'].mean():.4f} points")
print(f"   Interpretation: Biased due to selection on baseline score")

print("\n2. OLS regression controlling for baseline score:")
print(f"   Effect: 3.7874 points")
print(f"   95% CI: [3.4077, 4.1670]")
print(f"   p-value: < 0.000001")
print(f"   Interpretation: After adjusting for baseline score differences,")
print(f"                   tutoring students gained ~3.79 more points")

print("\n3. Local linear regression near selection boundary (±5 points):")
print(f"   Effect: {model_local.coef_[0]:.4f} points")
print(f"   Interpretation: Estimate from students near the selection cutoff")
