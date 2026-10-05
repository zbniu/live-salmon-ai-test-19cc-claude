"""
Create visualization plots
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Load the data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Score gains by treatment group
ax1 = axes[0, 0]
ax1.boxplot([df[df['x']==0]['z'], df[df['x']==1]['z']], 
            tick_labels=['No tutoring', 'Tutoring'])
ax1.set_ylabel('Score gain (z)')
ax1.set_title('Distribution of Score Gains by Group')
ax1.grid(alpha=0.3)

# Plot 2: Baseline scores by treatment group
ax2 = axes[0, 1]
ax2.boxplot([df[df['x']==0]['y'], df[df['x']==1]['y']], 
            tick_labels=['No tutoring', 'Tutoring'])
ax2.set_ylabel('Baseline score (y)')
ax2.set_title('Distribution of Baseline Scores by Group')
ax2.grid(alpha=0.3)

# Plot 3: Scatter plot with regression lines
ax3 = axes[1, 0]
control_data = df[df['x']==0]
treated_data = df[df['x']==1]
ax3.scatter(control_data['y'], control_data['z'], alpha=0.3, s=20, label='No tutoring')
ax3.scatter(treated_data['y'], treated_data['z'], alpha=0.3, s=20, color='red', label='Tutoring')

# Add regression lines
X_control = control_data[['y']].values
y_control = control_data['z'].values
model_control = LinearRegression().fit(X_control, y_control)
y_line = np.array([50, 75])
ax3.plot(y_line, model_control.predict(y_line.reshape(-1,1)), 'b-', linewidth=2, label='Control trend')

X_treated = treated_data[['y']].values
y_treated = treated_data['z'].values
model_treated = LinearRegression().fit(X_treated, y_treated)
ax3.plot(y_line, model_treated.predict(y_line.reshape(-1,1)), 'r-', linewidth=2, label='Treated trend')

ax3.set_xlabel('Baseline score (y)')
ax3.set_ylabel('Score gain (z)')
ax3.set_title('Relationship Between Baseline Score and Gains')
ax3.legend()
ax3.grid(alpha=0.3)

# Plot 4: Treatment rate by baseline score
ax4 = axes[1, 1]
bins = np.arange(45, 76, 2)
bin_centers = (bins[:-1] + bins[1:]) / 2
treatment_rates = []
mean_gains = []

for i in range(len(bins)-1):
    in_bin = df[(df['y'] >= bins[i]) & (df['y'] < bins[i+1])]
    if len(in_bin) > 0:
        treatment_rates.append(in_bin['x'].mean())
        mean_gains.append(in_bin['z'].mean())
    else:
        treatment_rates.append(np.nan)
        mean_gains.append(np.nan)

ax4_twin = ax4.twinx()
ax4.bar(bin_centers, treatment_rates, width=1.5, alpha=0.7, label='Treatment rate')
ax4_twin.plot(bin_centers, mean_gains, 'ro-', linewidth=2, markersize=6, label='Mean score gain')

ax4.set_xlabel('Baseline score (y)')
ax4.set_ylabel('Fraction treated', color='b')
ax4_twin.set_ylabel('Mean score gain (z)', color='r')
ax4.set_title('Treatment Rate and Mean Gains by Baseline Score')
ax4.tick_params(axis='y', labelcolor='b')
ax4_twin.tick_params(axis='y', labelcolor='r')
ax4.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('analysis_plots.png', dpi=100, bbox_inches='tight')
print("Plots saved to analysis_plots.png")
