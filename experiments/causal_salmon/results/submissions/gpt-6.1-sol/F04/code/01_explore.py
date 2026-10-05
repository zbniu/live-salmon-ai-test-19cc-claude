from pathlib import Path
import hashlib, json, sys
import numpy as np
import pandas as pd
import scipy
import statsmodels

root = Path(__file__).resolve().parents[2]
data_path = root / 'upload/data(20261004-180720).csv'
desc_path = root / 'upload/STUDY_DESCRIPTION(20261004-180721).md'
d = pd.read_csv(data_path)
assert list(d.columns) == ['x', 'y', 'z']
assert len(d) == 2000 and not d.isna().any().any()
assert np.isfinite(d.to_numpy()).all()
assert set(d.x.unique()) == {0, 1} and d.x.sum() == 600
assert d.y.between(0, 100).all()
summary = d.groupby('x').agg(['count', 'mean', 'std', 'min', 'median', 'max'])
summary.to_csv(root / 'submission/results/group_summary.csv')
print(summary.to_string())
print('\nQuantiles by assignment:')
print(d.groupby('x')[['y', 'z']].quantile([0, .01, .05, .1, .25, .5, .75, .9, .95, .99, 1]).to_string())
print('\nCorrelations within arms:')
for x in [0, 1]:
    g = d[d.x == x]
    print(x, g[['y', 'z']].corr().to_string())
d['baseline_band'] = pd.cut(d.y, [0, 20, 40, 60, 80, 100], include_lowest=True)
bands = d.groupby(['baseline_band', 'x'], observed=False)[['y', 'z']].agg(['count', 'mean', 'std'])
bands.to_csv(root / 'submission/results/exploratory_bands.csv')
print('\nBaseline bands:\n', bands.to_string())
metadata = {'n': len(d), 'treated': int(d.x.sum()), 'missing': int(d.isna().sum().sum()),
    'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [data_path, desc_path]},
    'versions': {'python': sys.version, 'numpy': np.__version__, 'pandas': pd.__version__, 'scipy': scipy.__version__, 'statsmodels': statsmodels.__version__}}
(root / 'submission/results/input_validation.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
print('\nOutputs: group_summary.csv, exploratory_bands.csv, input_validation.json')
