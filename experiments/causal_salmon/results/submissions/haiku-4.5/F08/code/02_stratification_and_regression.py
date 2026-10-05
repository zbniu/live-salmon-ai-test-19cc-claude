import pandas as pd
import numpy as np
from scipy import stats
import json

df = pd.read_csv('/mnt/user-data/uploads/data.csv')

print("="*80)
print("DETAILED STRATIFICATION ANALYSIS")
print("="*80)

# Quintile-based stratification
df['y_quintile'] = pd.qcut(df['y'], q=5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])

stratified_results = []

for stratum in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
    subset = df[df['y_quintile'] == stratum]
    
    control_subset = subset[subset['x'] == 0]
    treatment_subset = subset[subset['x'] == 1]
    
    n_c = len(control_subset)
    n_t = len(treatment_subset)
    
    if n_c > 0 and n_t > 0:
        z_c = control_subset['z'].values
        z_t = treatment_subset['z'].values
        
        mean_z_c = z_c.mean()
        mean_z_t = z_t.mean()
        effect = mean_z_t - mean_z_c
        
        # Standard error of difference
        var_c = z_c.var(ddof=1)
        var_t = z_t.var(ddof=1)
        se_diff = np.sqrt(var_c/n_c + var_t/n_t)
        
        # T-test
        t_stat, p_val = stats.ttest_ind(z_t, z_c)
        
        y_range = (subset['y'].min(), subset['y'].max())
        
        result = {
            'stratum': stratum,
            'n_control': n_c,
            'n_treatment': n_t,
            'y_min': float(y_range[0]),
            'y_max': float(y_range[1]),
            'y_mean_control': float(control_subset['y'].mean()),
            'y_mean_treatment': float(treatment_subset['y'].mean()),
            'z_mean_control': float(mean_z_c),
            'z_mean_treatment': float(mean_z_t),
            'effect': float(effect),
            'se': float(se_diff),
            't_stat': float(t_stat),
            'p_value': float(p_val),
            'stratum_weight': float((n_c + n_t) / len(df))
        }
        stratified_results.append(result)
        
        print(f"\n{stratum}: y ∈ [{y_range[0]:.2f}, {y_range[1]:.2f}]")
        print(f"  n_control={n_c}, n_treatment={n_t}")
        print(f"  z̄_control = {mean_z_c:.4f}, z̄_treatment = {mean_z_t:.4f}")
        print(f"  Effect (z_trt - z_ctrl) = {effect:.4f} (SE={se_diff:.4f})")
        print(f"  t={t_stat:.4f}, p={p_val:.6f}")
    else:
        print(f"\n{stratum}: Insufficient data")
        print(f"  n_control={n_c}, n_treatment={n_t}")

# Mantel-Haenszel type estimate (stratified estimate)
effects = []
weights = []

for result in stratified_results:
    effects.append(result['effect'])
    weight = (result['n_control'] + result['n_treatment']) / len(df)
    weights.append(weight)

if effects:
    weighted_effect = np.sum([e * w for e, w in zip(effects, weights)])
    simple_effect = np.mean(effects)
    
    print(f"\n" + "="*80)
    print("STRATIFIED ESTIMATES (controlling for y)")
    print("="*80)
    print(f"\nSimple unweighted average of stratum effects: {simple_effect:.4f}")
    print(f"Weighted average (by stratum size): {weighted_effect:.4f}")

# Regression approach for comparison
from sklearn.linear_model import LinearRegression

print(f"\n" + "="*80)
print("LINEAR REGRESSION ESTIMATES")
print("="*80)

X = df[['x', 'y']].values
y_vals = df['z'].values

model = LinearRegression().fit(X, y_vals)
effect_coef = model.coef_[0]
y_coef = model.coef_[1]

print(f"\nModel: z = {model.intercept_:.4f} + {effect_coef:.4f}*x + {y_coef:.4f}*y")
print(f"Effect of tutoring (coefficient on x): {effect_coef:.4f}")
print(f"Effect of baseline score (coefficient on y): {y_coef:.4f}")

# Compute R-squared and residual SE
predictions = model.predict(X)
ss_res = np.sum((y_vals - predictions)**2)
ss_tot = np.sum((y_vals - y_vals.mean())**2)
r_squared = 1 - (ss_res / ss_tot)
residual_se = np.sqrt(ss_res / (len(df) - 3))

print(f"R-squared: {r_squared:.4f}")
print(f"Residual standard error: {residual_se:.4f}")

# Confidence interval for effect
# Standard error of coefficient
x_centered = X - X.mean(axis=0)
var_covar_matrix = np.linalg.inv(x_centered.T @ x_centered) * residual_se**2
se_effect = np.sqrt(var_covar_matrix[0, 0])
ci_lower = effect_coef - 1.96 * se_effect
ci_upper = effect_coef + 1.96 * se_effect

print(f"95% CI for tutoring effect: [{ci_lower:.4f}, {ci_upper:.4f}]")

print(f"\n" + "="*80)
print("ANALYSIS OF TREATMENT ASSIGNMENT")
print("="*80)

# The assignment rule: students with highest (y + random) become applicants,
# then highest y among applicants are admitted
# This creates a sharp threshold

# Find the approximate threshold by looking at y distribution
y_sorted = np.sort(df['y'].values)
n_treatment = (df['x'] == 1).sum()

# Approximate threshold: where do we start seeing treatment?
treatment_y_min = df[df['x'] == 1]['y'].min()
treatment_y_max = df[df['x'] == 1]['y'].max()
control_y_max = df[df['x'] == 0]['y'].max()

print(f"\nScore ranges by treatment status:")
print(f"  Control: [{df[df['x']==0]['y'].min():.2f}, {df[df['x']==0]['y'].max():.2f}]")
print(f"  Treatment: [{treatment_y_min:.2f}, {treatment_y_max:.2f}]")
print(f"  Threshold appears to be around y ≈ {treatment_y_min:.2f}")

# Analysis below/above approximate threshold
threshold = 57.0
below_threshold = df[df['y'] < threshold]
above_threshold = df[df['y'] >= threshold]

print(f"\nAround y = {threshold}:")
print(f"  Below {threshold}: {len(below_threshold)} students, {(below_threshold['x']==1).sum()} treated")
print(f"  Above {threshold}: {len(above_threshold)} students, {(above_threshold['x']==1).sum()} treated")
print(f"  Treatment rate below: {100*(below_threshold['x']==1).sum()/len(below_threshold):.1f}%")
print(f"  Treatment rate above: {100*(above_threshold['x']==1).sum()/len(above_threshold):.1f}%")

print(f"\n" + "="*80)
print("INTERPRETATION")
print("="*80)

print(f"""
The naive comparison shows tutored students gained 3.45 more points than 
non-tutored students. However, tutored students had much higher baseline scores
(66.84 vs 57.23). 

When we account for baseline score differences:

1. STRATIFICATION (within students with similar baseline scores):
   - Within groups with similar baselines, the effect is much smaller
   - Q3 effect: ~0.62 points
   - Q4 effect: ~1.24 points
   - Q5 effect: ~1.78 points
   - Weighted average: ~1.1-1.2 points

2. LINEAR REGRESSION (assuming constant effect across baselines):
   - Adjusted effect of tutoring: ~1.11 points
   - For each point increase in baseline score, students gain ~0.24 more points
   - This adjustment accounts for the ~9.6 point difference in baseline scores

The regression-based estimate of 1.11 points appears most defensible because:
- It uses all the data efficiently
- It accounts for the strong baseline score confounding
- The linear assumption seems reasonable (similar effects across stratified groups)
""")

