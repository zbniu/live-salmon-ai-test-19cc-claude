"""Inspect the complete supplied dataset and empirical comparison support."""
import hashlib
import json
import pathlib
import sys
import numpy as np
import pandas as pd
import scipy
import statsmodels
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = pathlib.Path.cwd()
out = root / 'submission/results'
data_path = root / 'upload/data(20261004-180826).csv'
study_path = root / 'upload/STUDY_DESCRIPTION(20261004-180826).md'
df = pd.read_csv(data_path)
assert list(df.columns) == ['x', 'y', 'z']
assert len(df) == 2000 and df.notna().all().all()
assert set(df.x) == {0, 1} and int(df.x.sum()) == 600
assert df.y.between(0, 100).all()
summary = df.groupby('x').agg(n=('z','size'), y_mean=('y','mean'), y_sd=('y','std'), y_min=('y','min'), y_max=('y','max'), z_mean=('z','mean'), z_sd=('z','std'), z_min=('z','min'), z_max=('z','max'))
summary.to_csv(out / 'group_summary.csv')
df['baseline_bin'] = pd.cut(df.y, np.arange(0, 105, 5), right=False)
bins = df.groupby(['baseline_bin', 'x'], observed=False).agg(n=('z','size'), y_mean=('y','mean'), z_mean=('z','mean'), z_sd=('z','std')).reset_index()
bins.to_csv(out / 'baseline_bins.csv', index=False)
t = df[df.x == 1]
c = df[df.x == 0]
nearest = np.min(np.abs(t.y.to_numpy()[:,None] - c.y.to_numpy()[None,:]), axis=1)
support = {
    'n': len(df), 'columns': ['x','y','z'], 'missing_values': int(df[['x','y','z']].isna().sum().sum()),
    'unique_baselines': int(df.y.nunique()),
    'crude_z_difference': float(t.z.mean()-c.z.mean()),
    'treated_below_control_range': int((t.y < c.y.min()).sum()),
    'treated_above_control_range': int((t.y > c.y.max()).sum()),
    'nearest_control_baseline_distance_quantiles': dict(zip(['min','median','90%','95%','99%','max'], map(float, np.quantile(nearest,[0,.5,.9,.95,.99,1])))),
    'followup_min': float((df.y+df.z).min()), 'followup_max': float((df.y+df.z).max()),
    'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [data_path,study_path]},
    'versions': {'python': sys.version, 'numpy': np.__version__, 'pandas':pd.__version__, 'scipy':scipy.__version__, 'statsmodels':statsmodels.__version__, 'matplotlib':matplotlib.__version__}
}
(out / 'data_checks.json').write_text(json.dumps(support,indent=2),encoding='utf-8')
fig, axes = plt.subplots(2,1,figsize=(9,9))
for x, label, color in [(0,'No Q','#2374AB'),(1,'Q','#D45D00')]:
    a=df[df.x==x]
    axes[0].scatter(a.y,a.z,s=9,alpha=.45,label=label,color=color)
    axes[1].hist(a.y,bins=np.arange(0,102,2),alpha=.55,label=label,color=color)
axes[0].set(xlabel='Baseline y (points)',ylabel='Observed change z (points)')
axes[1].set(xlabel='Baseline y (points)',ylabel='Number of units')
for ax in axes: ax.legend(); ax.grid(alpha=.15)
fig.tight_layout(); fig.savefig(out/'baseline_outcome_support.png',dpi=160); plt.close(fig)
print('All 2000 rows validated; no rows excluded. Outputs: group_summary.csv, baseline_bins.csv, data_checks.json, baseline_outcome_support.png')
print(summary.to_string())
print(bins.to_string(index=False))
print(json.dumps(support,indent=2))
