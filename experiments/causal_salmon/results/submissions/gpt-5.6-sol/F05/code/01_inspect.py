"""Complete-data integrity checks and exploratory summaries; no rows excluded."""
import hashlib
import json
import pathlib
import sys
import numpy as np
import pandas as pd
import scipy
import statsmodels

root = pathlib.Path.cwd()
path = root / 'upload/data(6).csv'
df = pd.read_csv(path)
assert list(df.columns) == ['x', 'y', 'z']
assert len(df) == 2000 and not df.isna().any().any()
assert set(df.x.unique()) == {0, 1} and int(df.x.sum()) == 600
assert np.isfinite(df.to_numpy()).all()
summary = df.groupby('x').agg(['count', 'mean', 'std', 'min', 'median', 'max'])
summary.to_csv('submission/results/01_group_summary.csv')
df.assign(baseline_band=pd.cut(df.y, [0,20,40,60,80,100], include_lowest=True)).groupby(
    ['baseline_band','x'], observed=True
).agg(n=('z','size'), y_mean=('y','mean'), z_mean=('z','mean'), z_sd=('z','std')).to_csv(
    'submission/results/01_baseline_bands.csv')
metadata = {'n':len(df), 'missing':df.isna().sum().to_dict(), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'python':sys.version, 'numpy':np.__version__, 'pandas':pd.__version__, 'scipy':scipy.__version__,
    'statsmodels':statsmodels.__version__, 'followup_range':[(df.y+df.z).min(), (df.y+df.z).max()],
    'within_group_y_z_correlations':{str(x):g.y.corr(g.z) for x,g in df.groupby('x')}}
pathlib.Path('submission/results/01_integrity.json').write_text(json.dumps(metadata, indent=2)+'\n')
print(json.dumps(metadata, indent=2))
print(summary.to_string())
print(pathlib.Path('submission/results/01_baseline_bands.csv').read_text())
