"""
Investigate the selection mechanism and potential for discontinuity design
"""
import pandas as pd
import numpy as np

# Load the data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

print("=" * 70)
print("INVESTIGATING THE SELECTION MECHANISM")
print("=" * 70)

# Look for a sharp cutoff in baseline score
df_sorted = df.sort_values('y')

print("\nDistribution of start-of-term scores (y) by treatment:")
print("\nQuantiles of y for treated group:")
print(df[df['x']==1]['y'].describe())
print("\nQuantiles of y for control group:")
print(df[df['x']==0]['y'].describe())

# Check if there's a cutoff
min_treated_y = df[df['x']==1]['y'].min()
max_control_y = df[df['x']==0]['y'].max()

print(f"\nMinimum y among treated: {min_treated_y:.4f}")
print(f"Maximum y among control: {max_control_y:.4f}")
print(f"Overlap: {max_control_y >= min_treated_y}")

# If there's overlap, let's look at the density near the boundary
# Find 600th highest score (the cutoff)
sorted_y = np.sort(df['y'].values)[::-1]  # Sort descending
cutoff_approx = sorted_y[599]  # 600 students at or above this
print(f"\nApproximate 600th highest y score: {cutoff_approx:.4f}")

# Look at distribution around this
near_boundary = df[(df['y'] >= cutoff_approx - 2) & (df['y'] <= cutoff_approx + 2)]
print(f"Students within 2 points of {cutoff_approx:.4f}: {len(near_boundary)}")
print(f"  Treated: {len(near_boundary[near_boundary['x']==1])}")
print(f"  Control: {len(near_boundary[near_boundary['x']==0])}")

# Check if assignment is deterministic at high baseline scores
high_score_students = df[df['y'] >= 68]
print(f"\nStudents with y >= 68: {len(high_score_students)}")
print(f"  Fraction treated: {high_score_students['x'].mean():.4f}")

very_high_score = df[df['y'] >= 70]
print(f"\nStudents with y >= 70: {len(very_high_score)}")
print(f"  Fraction treated: {very_high_score['x'].mean():.4f}")

very_low_score = df[df['y'] <= 52]
print(f"\nStudents with y <= 52: {len(very_low_score)}")
print(f"  Fraction treated: {very_low_score['x'].mean():.4f}")

# Look at treatment probability by score bin
df['y_bin'] = pd.cut(df['y'], bins=20)
treatment_by_bin = df.groupby('y_bin', observed=True).agg({
    'x': ['count', 'sum', 'mean'],
    'z': 'mean'
})
print("\nTreatment rate and mean z by baseline score bins:")
print(treatment_by_bin)
