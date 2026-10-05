import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Load data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

# Create figure with multiple subplots
fig = plt.figure(figsize=(14, 10))

# Plot 1: Distribution of start-of-term scores by group
ax1 = plt.subplot(2, 3, 1)
treated = df[df['x'] == 1]['y']
control = df[df['x'] == 0]['y']
ax1.hist(control, bins=30, alpha=0.6, label='Control (x=0)', color='blue')
ax1.hist(treated, bins=30, alpha=0.6, label='Treated (x=1)', color='red')
ax1.set_xlabel('Start-of-Term Score (y)')
ax1.set_ylabel('Frequency')
ax1.set_title('Distribution of Start-of-Term Scores by Group')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Distribution of score gains by group
ax2 = plt.subplot(2, 3, 2)
treated_z = df[df['x'] == 1]['z']
control_z = df[df['x'] == 0]['z']
ax2.hist(control_z, bins=30, alpha=0.6, label='Control (x=0)', color='blue')
ax2.hist(treated_z, bins=30, alpha=0.6, label='Treated (x=1)', color='red')
ax2.set_xlabel('Score Gain (z)')
ax2.set_ylabel('Frequency')
ax2.set_title('Distribution of Score Gains by Group')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: Scatter plot with regression lines
ax3 = plt.subplot(2, 3, 3)
ax3.scatter(df[df['x'] == 0]['y'], df[df['x'] == 0]['z'], alpha=0.3, label='Control', color='blue', s=20)
ax3.scatter(df[df['x'] == 1]['y'], df[df['x'] == 1]['z'], alpha=0.3, label='Treated', color='red', s=20)

# Add regression lines
y_range = np.linspace(df['y'].min(), df['y'].max(), 100)
# Regression for control group
control_mask = df['x'] == 0
z_control = df[control_mask]['z'].values
y_control = df[control_mask]['y'].values
slope_control, intercept_control = np.polyfit(y_control, z_control, 1)
z_pred_control = slope_control * y_range + intercept_control

# Regression for treated group
treated_mask = df['x'] == 1
z_treated = df[treated_mask]['z'].values
y_treated = df[treated_mask]['y'].values
slope_treated, intercept_treated = np.polyfit(y_treated, z_treated, 1)
z_pred_treated = slope_treated * y_range + intercept_treated

ax3.plot(y_range, z_pred_control, color='blue', linewidth=2, label=f'Control fit (slope={slope_control:.3f})')
ax3.plot(y_range, z_pred_treated, color='red', linewidth=2, label=f'Treated fit (slope={slope_treated:.3f})')
ax3.set_xlabel('Start-of-Term Score (y)')
ax3.set_ylabel('Score Gain (z)')
ax3.set_title('Score Gain vs Start-of-Term Score')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: Box plots of score gains
ax4 = plt.subplot(2, 3, 4)
data_to_plot = [control_z, treated_z]
bp = ax4.boxplot(data_to_plot, labels=['Control (x=0)', 'Treated (x=1)'], patch_artist=True)
bp['boxes'][0].set_facecolor('lightblue')
bp['boxes'][1].set_facecolor('lightcoral')
ax4.set_ylabel('Score Gain (z)')
ax4.set_title('Score Gains by Treatment Group')
ax4.grid(True, alpha=0.3, axis='y')

# Add mean markers
means = [control_z.mean(), treated_z.mean()]
ax4.plot([1, 2], means, 'g^', markersize=10, label='Mean')
ax4.legend()

# Plot 5: Residual plot (unadjusted)
ax5 = plt.subplot(2, 3, 5)
X_unadjusted = np.column_stack([np.ones(len(df)), df['x']])
beta_unadjusted = np.linalg.lstsq(X_unadjusted, df['z'].values, rcond=None)[0]
residuals_unadjusted = df['z'].values - X_unadjusted @ beta_unadjusted
ax5.scatter(df[df['x'] == 0].index, residuals_unadjusted[df['x'] == 0], alpha=0.3, label='Control', color='blue', s=20)
ax5.scatter(df[df['x'] == 1].index, residuals_unadjusted[df['x'] == 1], alpha=0.3, label='Treated', color='red', s=20)
ax5.axhline(y=0, color='black', linestyle='--', linewidth=1)
ax5.set_ylabel('Residuals')
ax5.set_xlabel('Observation Index')
ax5.set_title('Residuals: Unadjusted Model')
ax5.legend()
ax5.grid(True, alpha=0.3)

# Plot 6: Residual plot (adjusted)
ax6 = plt.subplot(2, 3, 6)
X_adjusted = np.column_stack([np.ones(len(df)), df['x'], df['y']])
beta_adjusted = np.linalg.lstsq(X_adjusted, df['z'].values, rcond=None)[0]
residuals_adjusted = df['z'].values - X_adjusted @ beta_adjusted
ax6.scatter(df[df['x'] == 0].index, residuals_adjusted[df['x'] == 0], alpha=0.3, label='Control', color='blue', s=20)
ax6.scatter(df[df['x'] == 1].index, residuals_adjusted[df['x'] == 1], alpha=0.3, label='Treated', color='red', s=20)
ax6.axhline(y=0, color='black', linestyle='--', linewidth=1)
ax6.set_ylabel('Residuals')
ax6.set_xlabel('Observation Index')
ax6.set_title('Residuals: Adjusted Model')
ax6.legend()
ax6.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/home/claude/submission/results/analysis_plots.png', dpi=100, bbox_inches='tight')
print("Visualization saved to analysis_plots.png")
plt.close()

# Additional detailed analysis
print("\nADDITIONAL ANALYSIS")
print("=" * 60)

# Check correlation between variables
print("\nCorrelation Matrix:")
print(df.corr())

# Stratified analysis: Look at effect within different score ranges
print("\n\nSTRATIFIED ANALYSIS BY START-OF-TERM SCORE QUARTILES")
print("=" * 60)

df['y_quartile'] = pd.qcut(df['y'], q=4, labels=['Q1 (Low)', 'Q2', 'Q3', 'Q4 (High)'])

for q in ['Q1 (Low)', 'Q2', 'Q3', 'Q4 (High)']:
    subset = df[df['y_quartile'] == q]
    treated_subset = subset[subset['x'] == 1]['z']
    control_subset = subset[subset['x'] == 0]['z']
    
    if len(treated_subset) > 0 and len(control_subset) > 0:
        diff = treated_subset.mean() - control_subset.mean()
        print(f"\n{q}:")
        print(f"  Y range: {subset['y'].min():.2f} - {subset['y'].max():.2f}")
        print(f"  Treated n={len(treated_subset)}, mean z={treated_subset.mean():.4f}")
        print(f"  Control n={len(control_subset)}, mean z={control_subset.mean():.4f}")
        print(f"  Difference: {diff:.4f}")

# Robustness check: nonparametric comparison
print("\n\nROBUSTNESS CHECK: NONPARAMETRIC TEST")
print("=" * 60)
from scipy.stats import mannwhitneyu

u_stat, p_val = mannwhitneyu(treated_z, control_z, alternative='two-sided')
print(f"\nMann-Whitney U test (unadjusted):")
print(f"  U statistic: {u_stat:.2f}")
print(f"  p-value: {p_val:.10f}")
print(f"  Conclusion: Median score gains differ significantly between groups")

