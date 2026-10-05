"""Baseline-adjusted ATT via control-outcome standardization and sensitivity checks.

Only the complete attached CSV is used. Natural cubic regression splines allow
nonlinear untreated response; the treated response is never forced to have a
constant effect. Bootstrap intervals are approximate, not exact design intervals.
"""
import json
import pathlib
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = pathlib.Path.cwd()
out = root / 'submission/results'
df = pd.read_csv(root / 'upload/data(20261004-180826).csv')
t = df[df.x == 1]
c = df[df.x == 0]
yt, zt = t.y.to_numpy(), t.z.to_numpy()
yc, zc = c.y.to_numpy(), c.z.to_numpy()
lo, hi = df.y.min(), df.y.max()
def spline_basis(y, k):
    knots = np.linspace(lo, hi, k)
    return CubicSpline(knots, np.eye(k), bc_type='natural')(y)
def estimate(bt, bc):
    beta = np.linalg.lstsq(bc, zc, rcond=None)[0]
    return float(np.mean(zt - bt @ beta)), beta

rows = []
fits = {}
for k in [4,5,7,9]:
    bt, bc = spline_basis(yt,k), spline_basis(yc,k)
    att, beta = estimate(bt,bc)
    rows.append({'method': f'Natural cubic spline, {k} basis functions', 'att_points': att,
                 'mean_predicted_untreated_change_for_treated':float(np.mean(bt@beta))})
    fits[k] = (bt,bc,beta)
for degree in [1,2,3]:
    bt = np.vander((yt-60)/15,degree+1,increasing=True)
    bc = np.vander((yc-60)/15,degree+1,increasing=True)
    att, beta = estimate(bt,bc)
    rows.append({'method':f'Control regression, polynomial degree {degree}', 'att_points':att,
                 'mean_predicted_untreated_change_for_treated':float(np.mean(bt@beta))})

# Local stratification is a sensitivity estimate. All treated units are included.
edges = np.arange(45,76,1,dtype=float)
df['bin'] = pd.cut(df.y, edges, right=False)
strata = df.groupby(['bin','x'], observed=False).agg(n=('z','size'),mean_z=('z','mean'),mean_y=('y','mean')).reset_index()
strata.to_csv(out/'one_point_strata.csv',index=False)
wide = strata.pivot(index='bin',columns='x',values=['n','mean_z','mean_y'])
used = wide[wide['n'][1]>0].copy()
assert (used['n'][0]>0).all() and used['n'][1].sum()==len(t)
bin_att=float(np.sum(used['n'][1]*(used['mean_z'][1]-used['mean_z'][0]))/len(t))
rows.append({'method':'One-point baseline bins, weighted by treated counts','att_points':bin_att,
             'mean_predicted_untreated_change_for_treated':float(zt.mean()-bin_att)})
pd.DataFrame(rows).to_csv(out/'estimator_sensitivity.csv',index=False)

# Primary estimator: 7 basis functions with equally spaced knots fixed from the
# complete baseline range. Every control contributes to the fit; all recipients
# contribute to the target mean. Sampling is stratified to preserve group sizes.
bt,bc,beta=fits[7]
primary=float(np.mean(zt-bt@beta))
rng=np.random.default_rng(20261004)
B=3000
boot=np.empty(B)
for b in range(B):
    it=rng.integers(0,len(t),len(t))
    ic=rng.integers(0,len(c),len(c))
    beta_b=np.linalg.lstsq(bc[ic],zc[ic],rcond=None)[0]
    boot[b]=np.mean(zt[it]-bt[it]@beta_b)
pd.DataFrame({'replicate':np.arange(1,B+1),'att_points':boot}).to_csv(out/'bootstrap_att.csv',index=False)
ci=np.quantile(boot,[.025,.975])
result={
    'estimand':'Average effect of Q on change z for the 600 recipients (ATT)',
    'primary_method':'Untreated-outcome regression with natural cubic spline of baseline; standardized over all 600 treated baselines',
    'spline_basis_functions':7,'spline_knots':np.linspace(lo,hi,7).tolist(),
    'n_total':len(df),'n_treated':len(t),'n_control':len(c),
    'mean_observed_treated_change':float(zt.mean()),
    'estimated_mean_untreated_change_for_treated':float(np.mean(bt@beta)),
    'att_points':primary,'bootstrap_95_percentile_interval':ci.tolist(),
    'bootstrap_standard_error':float(boot.std(ddof=1)),
    'bootstrap_replicates':B,'bootstrap_seed':20261004,
    'bootstrap_nonpositive_replicates':int((boot<=0).sum()),
    'ci_interpretation':'Approximate stratified unit-bootstrap interval; model/sampling uncertainty, not an exact randomization interval for the fixed-quota design.',
    'sensitivity_min':min(r['att_points'] for r in rows),'sensitivity_max':max(r['att_points'] for r in rows),
    'crude_difference_points':float(zt.mean()-zc.mean()),
    'identification_assumptions':'Use supplied baseline-only assignment and independent selection randomness for conditional exchangeability; use empirical control overlap and smooth conditional outcome estimation. No treatment effect homogeneity imposed.'
}
(out/'att_estimate.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
pred=df[['x','y','z']].copy()
pred['estimated_untreated_mean_change']=spline_basis(df.y.to_numpy(),7)@beta
pred['observed_minus_estimated_untreated']=pred.z-pred.estimated_untreated_mean_change
pred.to_csv(out/'unit_predictions.csv',index=False)
grid=np.linspace(lo,hi,400)
fig,ax=plt.subplots(figsize=(9,5))
ax.scatter(yc,zc,s=8,alpha=.15,color='#2374AB',label='Untreated observed changes')
ax.plot(grid,spline_basis(grid,7)@beta,color='#2374AB',lw=2,label='Estimated untreated mean')
tb=spline_basis(yt,7)
treated_beta=np.linalg.lstsq(tb,zt,rcond=None)[0]
g=grid[grid>=yt.min()]
ax.plot(g,spline_basis(g,7)@treated_beta,color='#D45D00',lw=2,label='Treated mean curve (descriptive)')
ax.axvline(yt.min(),color='gray',ls=':',label='Lowest treated baseline')
ax.set(xlabel='Baseline y (points)',ylabel='Change z (points)',title=f'Baseline-standardized ATT: {primary:.2f} points')
ax.legend();ax.grid(alpha=.15);fig.tight_layout();fig.savefig(out/'adjusted_outcome_curves.png',dpi=160);plt.close(fig)
print(json.dumps(result,indent=2))
print(pd.DataFrame(rows).to_string(index=False))
print('Outputs: att_estimate.json, estimator_sensitivity.csv, one_point_strata.csv, bootstrap_att.csv, unit_predictions.csv, adjusted_outcome_curves.png')
