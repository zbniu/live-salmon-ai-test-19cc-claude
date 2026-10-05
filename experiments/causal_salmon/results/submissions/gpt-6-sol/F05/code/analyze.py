#!/usr/bin/env python3
"""Analysis of the complete randomized study data."""
import csv, json, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'upload' / 'data(20261004-071257).csv'
OUT = ROOT / 'submission' / 'results'
OUT.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(DATA)
assert list(df.columns) == ['x','y','z'] and len(df) == 2000
assert not df.isna().any().any() and set(df.x) == {0,1} and int(df.x.sum()) == 600
assert np.isfinite(df[['y','z']].to_numpy()).all()
assert ((df.y >= 0) & (df.y <= 100)).all()

summary = df.groupby('x')[['y','z']].agg(['count','mean','std','median','min','max'])
a, b = df.loc[df.x == 1,'z'].to_numpy(), df.loc[df.x == 0,'z'].to_numpy()
na, nb = len(a), len(b)
diff = float(a.mean()-b.mean())
se = math.sqrt(a.var(ddof=1)/na+b.var(ddof=1)/nb)
df_w = (a.var(ddof=1)/na+b.var(ddof=1)/nb)**2 / ((a.var(ddof=1)/na)**2/(na-1)+(b.var(ddof=1)/nb)**2/(nb-1))
ci = [diff-stats.t.ppf(.975,df_w)*se, diff+stats.t.ppf(.975,df_w)*se]
p_w = float(2*stats.t.sf(abs(diff/se),df_w))
y1, y0 = df.loc[df.x==1,'y'], df.loc[df.x==0,'y']
y_diff = float(y1.mean()-y0.mean())
y_se = math.sqrt(y1.var(ddof=1)/na+y0.var(ddof=1)/nb)

# Regression adjustment uses the baseline measured before randomization.
# The interaction permits the baseline relationship to differ by assignment.
df['yc'] = df.y - df.y.mean()
X = np.column_stack([np.ones(len(df)),df.x.to_numpy(),df.yc.to_numpy(),
                     (df.x*df.yc).to_numpy()])
Y = df.z.to_numpy()
xtx_inv = np.linalg.inv(X.T @ X)
coef = xtx_inv @ X.T @ Y
resid = Y - X @ coef
leverage = np.sum((X @ xtx_inv)*X,axis=1)
hc3_cov = xtx_inv @ (X.T @ (X*((resid/(1-leverage))**2)[:,None])) @ xtx_inv
# Average predicted Q-minus-control change over the actual treated baselines.
contrast = np.array([0.,1.,0.,float(df.loc[df.x==1,'yc'].mean())])
adj = float(contrast @ coef)
adj_se = float(np.sqrt(contrast @ hc3_cov @ contrast))
adj_ci = [adj-1.96*adj_se, adj+1.96*adj_se]

# Complete randomization sharp-null reference distribution: relabel 600 units.
# Fixed seed makes the Monte Carlo check exactly reproducible.
rng = np.random.default_rng(20261004)
z = df.z.to_numpy()
n_perm=20000
extreme = 0
for _ in range(n_perm):
    selected = rng.choice(len(z),size=na,replace=False)
    perm_diff = z[selected].mean() - (z.sum()-z[selected].sum())/nb
    extreme += abs(perm_diff) >= abs(diff)
p_perm = (extreme+1)/(n_perm+1)

out = {
    'source_rows': len(df), 'treated_n': na, 'control_n': nb,
    'groups': {str(k): {'y_mean':float(df[df.x==k].y.mean()),'y_sd':float(df[df.x==k].y.std()),
                        'z_mean':float(df[df.x==k].z.mean()),'z_sd':float(df[df.x==k].z.std()),
                        'z_median':float(df[df.x==k].z.median()),
                        'z_min':float(df[df.x==k].z.min()),'z_max':float(df[df.x==k].z.max())}
               for k in [0,1]},
    'unadjusted_difference_points': diff,
    'unadjusted_welch_se': se, 'unadjusted_welch_df': df_w,
    'unadjusted_95pct_ci':ci, 'unadjusted_two_sided_p':p_w,
    'baseline_mean_difference':y_diff,'baseline_difference_se':y_se,
    'adjusted_treated_baseline_effect_points':adj,
    'adjusted_robust_se':adj_se,'adjusted_95pct_ci':adj_ci,
    'adjustment_coefficients':dict(zip(['intercept','x','yc','x_by_yc'],map(float,coef))),
    'randomization_sharp_null_two_sided_monte_carlo_p':p_perm,
    'permutation_draws':n_perm,'permutation_extreme_draws':int(extreme),
    'treated_positive_observed_change_fraction':float((a>0).mean()),
    'control_positive_observed_change_fraction':float((b>0).mean())
}
(OUT/'analysis.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
(OUT/'group_summary.txt').write_text(summary.to_string()+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
