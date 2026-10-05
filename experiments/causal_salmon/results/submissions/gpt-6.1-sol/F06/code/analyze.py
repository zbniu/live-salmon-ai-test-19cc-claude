"""Analyze all supplied rows; no external data or internet access.

Primary estimator: randomized difference in mean score gains.
Sensitivity: fully interacted baseline-adjusted OLS, HC3 covariance,
standardized to the observed attendees' baseline scores (ATT target).
Polynomial degrees 1, 2, 3 are reported together, not significance-selected.
"""
from pathlib import Path
import hashlib
import json
import platform
import sys
import numpy as np
import pandas as pd
import scipy
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'submission/results'
DATA = ROOT / 'upload/data(20261004-180737).csv'
DESC = ROOT / 'upload/STUDY_DESCRIPTION(20261004-180737).md'
OUT.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(DATA)
assert list(df.columns) == ['x', 'y', 'z']
assert df.shape == (2000, 3)
assert df.notna().all().all()
assert np.isfinite(df.to_numpy()).all()
assert set(df.x.unique()) == {0, 1}
assert int(df.x.sum()) == 600
assert df.y.between(0, 100).all()

summary = df.groupby('x').agg(n=('z','size'), y_mean=('y','mean'),
    y_sd=('y','std'), y_min=('y','min'), y_max=('y','max'),
    z_mean=('z','mean'), z_sd=('z','std'), z_min=('z','min'), z_max=('z','max'))
summary.to_csv(OUT / 'group_summary.csv')
t = df.loc[df.x == 1, 'z'].to_numpy()
c = df.loc[df.x == 0, 'z'].to_numpy()
n1, n0 = len(t), len(c)
estimate = t.mean() - c.mean()
v1, v0 = t.var(ddof=1)/n1, c.var(ddof=1)/n0
se = np.sqrt(v1+v0)
dof = (v1+v0)**2/(v1**2/(n1-1)+v0**2/(n0-1))
critical = stats.t.ppf(.975, dof)
primary = dict(estimate=float(estimate), standard_error=float(se),
    ci95_low=float(estimate-critical*se), ci95_high=float(estimate+critical*se),
    welch_df=float(dof), t_statistic=float(estimate/se),
    p_two_sided=float(2*stats.t.sf(abs(estimate/se), dof)))
baseline = stats.ttest_ind(df.loc[df.x==1,'y'], df.loc[df.x==0,'y'], equal_var=False)

# Separate group outcome curves, evaluated over attendees' baseline distribution.
# Center/scale baseline for numerical stability. Each model uses all 2000 rows.
u = (df.y.to_numpy()-df.y.mean())/df.y.std(ddof=1)
x = df.x.to_numpy()
models = []
for degree in (1, 2, 3):
    basis = np.column_stack([u**k for k in range(1, degree+1)])
    X = np.column_stack([np.ones(len(df)), x, basis, x[:,None]*basis])
    outcome = df.z.to_numpy()
    coefficients, _, rank, _ = np.linalg.lstsq(X, outcome, rcond=None)
    assert rank == X.shape[1]
    bread = np.linalg.inv(X.T @ X)
    residuals = outcome - X @ coefficients
    leverage = np.einsum('ij,jk,ik->i', X, bread, X)
    weights = (residuals / (1-leverage))**2
    covariance = bread @ (X.T @ (X*weights[:,None])) @ bread
    r_squared = 1 - np.sum(residuals**2)/np.sum((outcome-outcome.mean())**2)
    contrast = np.zeros(X.shape[1])
    contrast[1] = 1
    contrast[2+degree:] = basis[x==1].mean(axis=0)
    adj = float(contrast @ coefficients)
    adjse = float(np.sqrt(contrast @ covariance @ contrast))
    models.append(dict(degree=degree, estimate=adj, standard_error=adjse,
        ci95_low=adj-1.959963984540054*adjse,
        ci95_high=adj+1.959963984540054*adjse,
        p_two_sided=float(2*stats.norm.sf(abs(adj/adjse))),
        r_squared=float(r_squared)))
    fit_details = dict(degree=degree, coefficients=coefficients.tolist(),
        hc3_covariance=covariance.tolist(), attendee_standardization_contrast=contrast.tolist(),
        baseline_center=float(df.y.mean()), baseline_scale=float(df.y.std(ddof=1)),
        design_columns=['intercept','x']+[f'u^{k}' for k in range(1,degree+1)]+[f'x*u^{k}' for k in range(1,degree+1)],
        residual_sum_squares=float(np.sum(residuals**2)), r_squared=float(r_squared))
    (OUT / f'ols_degree_{degree}.json').write_text(json.dumps(fit_details, indent=2)+'\n', encoding='utf-8')
pd.DataFrame(models).to_csv(OUT / 'adjusted_sensitivity.csv', index=False)

bins = pd.qcut(df.y, 10, duplicates='drop')
df.assign(baseline_decile=bins).groupby(['baseline_decile','x'], observed=True).agg(
    n=('z','size'), mean_y=('y','mean'), mean_z=('z','mean'), sd_z=('z','std')
).to_csv(OUT / 'baseline_deciles.csv')

results = dict(primary=primary, adjusted_sensitivity=models,
    validation=dict(rows=len(df), columns=list(df.columns), missing_values=int(df.isna().sum().sum()),
        attendees=n1, nonattendees=n0,
        end_score_outside_0_100=int((~(df.y+df.z).between(0,100)).sum())),
    baseline_mean_difference=float(summary.loc[1,'y_mean']-summary.loc[0,'y_mean']),
    baseline_welch_p=float(baseline.pvalue),
    input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [DATA, DESC]},
    environment=dict(python=sys.version, platform=platform.platform(), numpy=np.__version__,
        pandas=pd.__version__, scipy=scipy.__version__))
(OUT / 'analysis.json').write_text(json.dumps(results, indent=2)+'\n', encoding='utf-8')
print('Complete-data validation: PASSED; 2000 rows, 600 attendees, 1400 nonattendees.')
print(summary.to_string())
print('\nPRIMARY RANDOMIZED DIFFERENCE IN MEANS')
print(json.dumps(primary, indent=2))
print('\nBASELINE-ADJUSTED ATT SENSITIVITY (HC3; conditional on observed baseline scores)')
print(pd.DataFrame(models).to_string(index=False))
print('\nBaseline mean difference:', results['baseline_mean_difference'])
print('End scores outside 0-100:', results['validation']['end_score_outside_0_100'])
print('Outputs:', ', '.join(sorted(p.name for p in OUT.iterdir())))
