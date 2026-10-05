"""
Analysis of tutoring class effect on score gains
Research question: Did attending the tutoring class increase score gain?
"""

import pandas as pd
import numpy as np
from scipy import stats
import json

# Load data
df = pd.read_csv('/mnt/user-data/uploads/data.csv')

# Create output file to log results
output_file = '/home/claude/submission/results/analysis_output.txt'

with open(output_file, 'w') as f:
    # ===== DATA OVERVIEW =====
    f.write("="*70 + "\n")
    f.write("DATA OVERVIEW\n")
    f.write("="*70 + "\n")
    
    f.write(f"\nTotal number of students: {len(df)}\n")
    f.write(f"Number who attended tutoring (x=1): {(df['x'] == 1).sum()}\n")
    f.write(f"Number who did NOT attend (x=0): {(df['x'] == 0).sum()}\n")
    
    f.write("\nFirst few rows of data:\n")
    f.write(df.head(10).to_string())
    
    f.write("\n\nData summary statistics:\n")
    f.write(df.describe().to_string())
    
    # ===== DESCRIPTIVE STATISTICS BY GROUP =====
    f.write("\n\n" + "="*70 + "\n")
    f.write("DESCRIPTIVE STATISTICS BY GROUP\n")
    f.write("="*70 + "\n")
    
    attended = df[df['x'] == 1]
    not_attended = df[df['x'] == 0]
    
    f.write(f"\nSTUDENTS WHO ATTENDED TUTORING (x=1): n={len(attended)}\n")
    f.write(f"  Start-of-term score (y):\n")
    f.write(f"    Mean: {attended['y'].mean():.4f}\n")
    f.write(f"    SD:   {attended['y'].std():.4f}\n")
    f.write(f"    Min:  {attended['y'].min():.4f}\n")
    f.write(f"    Max:  {attended['y'].max():.4f}\n")
    
    f.write(f"\n  Score gain (z):\n")
    f.write(f"    Mean: {attended['z'].mean():.4f}\n")
    f.write(f"    SD:   {attended['z'].std():.4f}\n")
    f.write(f"    Min:  {attended['z'].min():.4f}\n")
    f.write(f"    Max:  {attended['z'].max():.4f}\n")
    
    f.write(f"\n\nSTUDENTS WHO DID NOT ATTEND (x=0): n={len(not_attended)}\n")
    f.write(f"  Start-of-term score (y):\n")
    f.write(f"    Mean: {not_attended['y'].mean():.4f}\n")
    f.write(f"    SD:   {not_attended['y'].std():.4f}\n")
    f.write(f"    Min:  {not_attended['y'].min():.4f}\n")
    f.write(f"    Max:  {not_attended['y'].max():.4f}\n")
    
    f.write(f"\n  Score gain (z):\n")
    f.write(f"    Mean: {not_attended['z'].mean():.4f}\n")
    f.write(f"    SD:   {not_attended['z'].std():.4f}\n")
    f.write(f"    Min:  {not_attended['z'].min():.4f}\n")
    f.write(f"    Max:  {not_attended['z'].max():.4f}\n")
    
    # ===== SIMPLE COMPARISON =====
    f.write("\n\n" + "="*70 + "\n")
    f.write("SIMPLE DIFFERENCE IN SCORE GAINS (UNADJUSTED)\n")
    f.write("="*70 + "\n")
    
    mean_diff = attended['z'].mean() - not_attended['z'].mean()
    f.write(f"\nMean score gain (attended): {attended['z'].mean():.4f}\n")
    f.write(f"Mean score gain (not attended): {not_attended['z'].mean():.4f}\n")
    f.write(f"Difference (attended - not attended): {mean_diff:.4f}\n")
    
    # Independent samples t-test
    t_stat, p_value = stats.ttest_ind(attended['z'], not_attended['z'])
    f.write(f"\nIndependent samples t-test:\n")
    f.write(f"  t-statistic: {t_stat:.4f}\n")
    f.write(f"  p-value: {p_value:.6f}\n")
    
    # ===== CONFOUNDING ANALYSIS =====
    f.write("\n\n" + "="*70 + "\n")
    f.write("CONFOUNDING: START-OF-TERM SCORE DIFFERS BETWEEN GROUPS\n")
    f.write("="*70 + "\n")
    
    f.write(f"\nMean start-of-term score (attended): {attended['y'].mean():.4f}\n")
    f.write(f"Mean start-of-term score (not attended): {not_attended['y'].mean():.4f}\n")
    f.write(f"Difference: {attended['y'].mean() - not_attended['y'].mean():.4f}\n")
    
    # Check correlation between y and z
    corr = df[['y', 'z']].corr().iloc[0, 1]
    f.write(f"\nOverall correlation between start-of-term score (y) and gain (z): {corr:.4f}\n")
    f.write("Note: Since students with higher start-of-term scores were more likely\n")
    f.write("to attend tutoring, and there is a correlation between y and z,\n")
    f.write("there may be confounding. We need to adjust for y.\n")
    
    # ===== REGRESSION ANALYSIS (ADJUSTED) =====
    f.write("\n\n" + "="*70 + "\n")
    f.write("REGRESSION ANALYSIS: ADJUSTED FOR START-OF-TERM SCORE\n")
    f.write("="*70 + "\n")
    
    # Simple linear regression: z ~ x
    X_simple = np.column_stack([np.ones(len(df)), df['x']])
    beta_simple = np.linalg.lstsq(X_simple, df['z'], rcond=None)[0]
    residuals_simple = df['z'] - (X_simple @ beta_simple)
    rss_simple = np.sum(residuals_simple**2)
    mse_simple = rss_simple / (len(df) - 2)
    se_beta_simple = np.sqrt(np.diag(np.linalg.inv(X_simple.T @ X_simple) * mse_simple))
    
    f.write("\nModel 1: Score gain ~ Attendance only\n")
    f.write(f"z = {beta_simple[0]:.4f} + {beta_simple[1]:.4f} * x\n")
    f.write(f"\nInterpretation:\n")
    f.write(f"  Intercept (baseline gain for x=0): {beta_simple[0]:.4f}\n")
    f.write(f"  Attendance effect (x=1): {beta_simple[1]:.4f}\n")
    f.write(f"  Standard error of attendance effect: {se_beta_simple[1]:.4f}\n")
    f.write(f"  t-statistic: {beta_simple[1] / se_beta_simple[1]:.4f}\n")
    f.write(f"  p-value: {2 * (1 - stats.t.cdf(abs(beta_simple[1] / se_beta_simple[1]), len(df) - 2)):.6f}\n")
    
    # Multiple regression: z ~ x + y
    X_multiple = np.column_stack([np.ones(len(df)), df['x'], df['y']])
    beta_multiple = np.linalg.lstsq(X_multiple, df['z'], rcond=None)[0]
    residuals_multiple = df['z'] - (X_multiple @ beta_multiple)
    rss_multiple = np.sum(residuals_multiple**2)
    mse_multiple = rss_multiple / (len(df) - 3)
    se_beta_multiple = np.sqrt(np.diag(np.linalg.inv(X_multiple.T @ X_multiple) * mse_multiple))
    
    f.write("\n\nModel 2: Score gain ~ Attendance + Start-of-term score\n")
    f.write(f"z = {beta_multiple[0]:.4f} + {beta_multiple[1]:.4f} * x + {beta_multiple[2]:.4f} * y\n")
    f.write(f"\nInterpretation:\n")
    f.write(f"  Intercept: {beta_multiple[0]:.4f}\n")
    f.write(f"  Attendance effect (adjusted for y): {beta_multiple[1]:.4f}\n")
    f.write(f"  Standard error of attendance effect: {se_beta_multiple[1]:.4f}\n")
    f.write(f"  t-statistic: {beta_multiple[1] / se_beta_multiple[1]:.4f}\n")
    f.write(f"  p-value: {2 * (1 - stats.t.cdf(abs(beta_multiple[1] / se_beta_multiple[1]), len(df) - 3)):.6f}\n")
    f.write(f"\n  Start-of-term score effect: {beta_multiple[2]:.4f}\n")
    f.write(f"  Standard error: {se_beta_multiple[2]:.4f}\n")
    
    # Model comparison
    f.write("\n\nModel Comparison:\n")
    f.write(f"Model 1 (x only): RSS = {rss_simple:.2f}, R² = {1 - rss_simple / np.sum((df['z'] - df['z'].mean())**2):.6f}\n")
    f.write(f"Model 2 (x + y): RSS = {rss_multiple:.2f}, R² = {1 - rss_multiple / np.sum((df['z'] - df['z'].mean())**2):.6f}\n")
    
    # ===== SUMMARY AND ANSWER TO RESEARCH QUESTION =====
    f.write("\n\n" + "="*70 + "\n")
    f.write("SUMMARY AND ANSWER TO RESEARCH QUESTION\n")
    f.write("="*70 + "\n")
    
    f.write("\nResearch question: Did attending the tutoring class increase score gain?\n")
    f.write("If so, by how much?\n")
    
    f.write(f"\nKey findings:\n")
    f.write(f"1. Unadjusted difference in mean gains: {mean_diff:.4f} points\n")
    f.write(f"   (Students who attended gained {mean_diff:.4f} points more on average)\n")
    f.write(f"   p-value: {p_value:.6f}\n")
    
    f.write(f"\n2. Adjusted difference (accounting for start-of-term score):\n")
    f.write(f"   {beta_multiple[1]:.4f} points\n")
    f.write(f"   p-value: {2 * (1 - stats.t.cdf(abs(beta_multiple[1] / se_beta_multiple[1]), len(df) - 3)):.6f}\n")
    
    f.write(f"\n3. The groups differ in start-of-term scores by {attended['y'].mean() - not_attended['y'].mean():.4f} points,\n")
    f.write(f"   suggesting potential confounding in the selection process.\n")
    
    f.write(f"\n4. The relationship between start-of-term score and gain is:\n")
    f.write(f"   {beta_multiple[2]:.4f} points of gain per point of start-of-term score\n")
    
    f.write("\n" + "="*70 + "\n")
    f.write("CONCLUSION\n")
    f.write("="*70 + "\n")
    
    if beta_multiple[1] > 0 and 2 * (1 - stats.t.cdf(abs(beta_multiple[1] / se_beta_multiple[1]), len(df) - 3)) < 0.05:
        conclusion = f"YES: Attending the tutoring class increased score gains by approximately {beta_multiple[1]:.4f} points (statistically significant)."
    elif beta_multiple[1] > 0:
        conclusion = f"UNCLEAR: Attending the tutoring class appears to increase score gains by approximately {beta_multiple[1]:.4f} points, but this effect is NOT statistically significant (p > 0.05)."
    else:
        conclusion = f"NO: The data suggests attending the tutoring class did NOT increase score gains. The adjusted effect is {beta_multiple[1]:.4f} points."
    
    f.write(f"\n{conclusion}\n")

print("Analysis complete. Results saved to", output_file)
