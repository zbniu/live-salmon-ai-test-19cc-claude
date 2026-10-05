"""Inspect all input rows without modifying the supplied data."""
import hashlib
import json
from pathlib import Path
import platform
import numpy as np
import pandas as pd
import scipy
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'submission' / 'results'
path = ROOT / 'upload' / 'data(20261004-180728).csv'
d = pd.read_csv(path)
assert list(d.columns) == ['x', 'y', 'z']
assert len(d) == 2000 and d.isna().sum().sum() == 0
assert set(d.x.unique()) == {0, 1} and d.x.sum() == 600
assert np.isfinite(d.to_numpy()).all()
assert d.y.between(0, 100).all()
print('Versions:', platform.python_version(), np.__version__, pd.__version__, scipy.__version__)
print('Shape:', d.shape, 'missing:', d.isna().sum().to_dict())
summary = d.groupby('x').agg(n=('x','size'), y_mean=('y','mean'), y_sd=('y','std'),
    y_min=('y','min'), y_max=('y','max'), z_mean=('z','mean'), z_sd=('z','std'),
    z_min=('z','min'), z_max=('z','max'))
print(summary.to_string())
print('Follow-up range:', (d.y+d.z).min(), (d.y+d.z).max())
print('Correlation by group:', d.groupby('x')[['y','z']].corr().to_string())
bins = pd.qcut(d.y, 10, duplicates='drop')
bs = d.assign(baseline_decile=bins).groupby(['baseline_decile','x'], observed=True).agg(
    n=('z','size'), y_mean=('y','mean'), z_mean=('z','mean'), z_sd=('z','std'))
print('Baseline deciles:\n', bs.to_string())
summary.to_csv(OUT / 'group_summary.csv')
bs.to_csv(OUT / 'baseline_decile_summary.csv')
checks = {'rows':len(d), 'columns':list(d.columns), 'missing':d.isna().sum().to_dict(),
    'treated_count':int(d.x.sum()), 'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'baseline_in_range':bool(d.y.between(0,100).all()),
    'followup_in_range':bool((d.y+d.z).between(0,100).all()),
    'versions': {'python':platform.python_version(),'numpy':np.__version__, 'pandas':pd.__version__, 'scipy':scipy.__version__}}
(OUT / 'data_checks.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
print('Outputs: group_summary.csv, baseline_decile_summary.csv, data_checks.json')
