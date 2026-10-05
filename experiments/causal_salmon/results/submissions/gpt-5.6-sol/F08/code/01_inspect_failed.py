from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd
import scipy
import statsmodels

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'submission/results'
OUT.mkdir(parents=True, exist_ok=True)
source = ROOT / 'upload/data(9).csv'
d = pd.read_csv(source)
assert list(d.columns) == ['x', 'y', 'z']
assert len(d) == 2000 and not d.isna().any().any()
assert set(d.x.unique()) == {0, 1}
assert d.x.sum() == 600
assert np.isfinite(d.to_numpy()).all()
assert d.y.between(0, 100).all()
summary = d.groupby('x').agg(n=('z','size'), y_mean=('y','mean'),
    y_sd=('y','std'), y_min=('y','min'), y_max=('y','max'),
    z_mean=('z','mean'), z_sd=('z','std'), z_min=('z','min'), z_max=('z','max'))
summary.to_csv(OUT / 'group_summary.csv')
print('GROUP SUMMARY\n', summary.to_string())
bins = pd.cut(d.y, np.arange(0, 105, 5), right=False)
tab = d.groupby([bins, 'x'], observed=True).agg(n=('z','size'),
    y_mean=('y','mean'), z_mean=('z','mean'), z_sd=('z','std'))
tab.to_csv(OUT / 'five_point_bins.csv')
print('\nFIVE POINT BINS\n', tab.to_string())
control_max = d.loc[d.x.eq(0), 'y'].max()
treated_min = d.loc[d.x.eq(1), 'y'].min()
meta = {
    'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (source, ROOT / 'upload/STUDY_DESCRIPTION(9).md')},
    'rows': len(d), 'missing_values': int(d.isna().sum().sum()),
    'duplicate_rows': int(d.duplicated().sum()),
    'python': sys.version, 'numpy': np.__version__, 'pandas': pd.__version__,
    'scipy': scipy.__version__, 'statsmodels': statsmodels.__version__,
    'control_max_y': float(control_max), 'treated_min_y': float(treated_min),
    'treated_above_control_max': int((d.x.eq(1) & d.y.gt(control_max)).sum()),
    'controls_above_treated_min': int((d.x.eq(0) & d.y.ge(treated_min)).sum()),
    'raw_gain_difference': float(d.loc[d.x.eq(1), 'z'].mean() - d.loc[d.x.eq(0), 'z'].mean()),
    'end_score_min': float((d.y+d.z).min()),
    'end_score_max': float((d.y+d.z).max())
}
(OUT / 'inspection.json').write_text(json.dumps(meta, indent=2)+'\n')
print('\nVALIDATION AND METADATA\n', json.dumps(meta, indent=2))
