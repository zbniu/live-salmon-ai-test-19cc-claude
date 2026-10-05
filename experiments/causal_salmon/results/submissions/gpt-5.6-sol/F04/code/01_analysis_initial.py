"""Analyze the complete supplied randomized study, without external sources."""
from pathlib import Path
import hashlib
import json
import platform
import sys
import numpy as np
import pandas as pd
import scipy
from scipy import stats
import statsmodels
import statsmodels.api as sm

root = Path(__file__).resolve().parents[1]
source = root.parent / 'upload' / 'data(5).csv'
out = root / 'results'
d = pd.read_csv(source)
assert list(d.columns) == ['x', 'y', 'z']
assert len(d) == 2000
assert d.isna().sum().sum() == 0
assert set(d.x.unique()) == {0, 1}
assert int(d.x.sum()) == 600
assert np.isfinite(d.to_numpy()).all()
assert d.y.between(0, 100).all()
audit = {
    'rows': len(d), 'columns': list(d.columns),
    'missing': d.isna().sum().to_dict(),
    'treatment_counts': d.x.value_counts().sort_index().to_dict(),
    'data_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'versions': {'python': sys.version, 'numpy': np.__version__,
                 'pandas': pd.__version__, 'scipy': scipy.__version__,
                 'statsmodels': statsmodels.__version__},
    'followup_min': float((d.y + d.z).min()),
    'followup_max': float((d.y + d.z).max()),
}
(out / 'data_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
summary = d.groupby('x').agg(n=('z','size'), baseline_mean=('y','mean'),
    baseline_sd=('y','std'), baseline_min=('y','min'), baseline_max=('y','max'),
    change_mean=('z','mean'), change_sd=('z','std'), change_min=('z','min'),
    change_max=('z','max'))
summary.to_csv(out / 'group_summary.csv')
print('Data audit:', json.dumps(audit, indent=2))
print('\nGroup summaries:\n', summary.to_string())

t = d.loc[d.x == 1, 'z'].to_numpy()
c = d.loc[d.x == 0, 'z'].to_numpy()
estimate = t.mean() - c.mean()
v1, v0 = t.var(ddof=1)/len(t), c.var(ddof=1)/len(c)
se = np.sqrt(v1 + v0)
df = (v1 + v0)**2 / (v1**2/(len(t)-1) + v0**2/(len(c)-1))
crit = stats.t.ppf(.975, df)
unadjusted = {'estimate': float(estimate), 'se': float(se), 'df': float(df),
 'ci95_lower': float(estimate-crit*se), 'ci95_upper': float(estimate+crit*se),
 'p_two_sided': float(2*stats.t.sf(abs(estimate/se), df)),
 'p_one_sided_increase': float(stats.t.sf(estimate/se, df))}
print('\nRandomized unadjusted mean contrast:', json.dumps(unadjusted, indent=2))

# Separate polynomial trends in each arm, centered at the treated units'
# baseline-feature means. The coefficient of x then averages the fitted
# treatment difference over the actual treated baseline distribution.
fits = []
for degree in [1, 2, 3]:
    u = (d.y.to_numpy() - 50) / 25
    X = {'const': np.ones(len(d)), 'x': d.x.to_numpy()}
    for k in range(1, degree+1):
        feature = u**k
        centered = feature - feature[d.x.to_numpy() == 1].mean()
        X[f'y{k}'] = centered
        X[f'x_y{k}'] = d.x.to_numpy() * centered
    fit = sm.OLS(d.z, pd.DataFrame(X)).fit(cov_type='HC3', use_t=False)
    row = {'method': f'interacted_polynomial_degree_{degree}',
           'estimate': float(fit.params['x']), 'se_HC3': float(fit.bse['x']),
           'ci95_lower': float(fit.conf_int().loc['x', 0]),
           'ci95_upper': float(fit.conf_int().loc['x', 1]),
           'p_two_sided': float(fit.pvalues['x']), 'R_squared': float(fit.rsquared)}
    fits.append(row)
    (out / f'regression_degree_{degree}.txt').write_text(fit.summary().as_text() + '\n')
pd.DataFrame(fits).to_csv(out / 'adjusted_estimates.csv', index=False)
print('\nBaseline-adjusted sensitivity estimates:\n', pd.DataFrame(fits).to_string(index=False))

# Baseline deciles describe overlap and possible effect heterogeneity.
d['baseline_decile'] = pd.qcut(d.y, 10, labels=False) + 1
deciles = d.groupby(['baseline_decile','x']).agg(n=('z','size'),
   y_mean=('y','mean'), z_mean=('z','mean'), z_sd=('z','std'))
deciles.to_csv(out / 'baseline_deciles.csv')
print('\nBaseline deciles:\n', deciles.to_string())
print('\nWithin-arm Pearson correlations of baseline and change:')
for arm in [0,1]:
    sub = d[d.x == arm]
    print(arm, stats.pearsonr(sub.y, sub.z))

results = {'unadjusted': unadjusted, 'adjusted_sensitivity': fits}
(out / 'estimates.json').write_text(json.dumps(results, indent=2) + '\n')
print('\nWrote audit, summaries, mean contrast, and all sensitivity model results.')
