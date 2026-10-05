from pathlib import Path
import hashlib, json, sys, platform
import numpy as np
import pandas as pd
import scipy

root = Path(__file__).resolve().parents[1]
d = pd.read_csv(root / 'inputs/data.csv')
assert list(d.columns) == ['x', 'y', 'z']
assert d.shape == (2000, 3)
assert d.notna().all().all()
assert set(d.x.unique()) == {0, 1}
assert d.x.sum() == 600
assert np.isfinite(d.to_numpy()).all()
assert d.y.between(0, 100).all()
summary = d.groupby('x').agg(n=('z','size'), y_min=('y','min'), y_max=('y','max'), y_mean=('y','mean'), z_mean=('z','mean'), z_sd=('z','std'))
summary.to_csv(root / 'results/group_summary.csv')
edges = np.arange(0, 101, 5)
d['baseline_bin'] = pd.cut(d.y, edges, right=False, include_lowest=True)
bins = d.groupby(['baseline_bin','x'], observed=False).agg(n=('z','size'), y_mean=('y','mean'), z_mean=('z','mean'), z_sd=('z','std'))
bins.to_csv(root / 'results/baseline_bins.csv')
t = d[d.x == 1]; c = d[d.x == 0]
distance = np.abs(t.y.to_numpy()[:,None] - c.y.to_numpy()[None,:]).min(axis=1)
audit = {
    'n_rows':len(d), 'n_missing':int(d[['x','y','z']].isna().sum().sum()),
    'duplicate_rows':int(d[['x','y','z']].duplicated().sum()),
    'raw_mean_difference':float(t.z.mean()-c.z.mean()),
    'treated_outside_control_range':int(((t.y<c.y.min())|(t.y>c.y.max())).sum()),
    'nearest_control_baseline_distance_quantiles':dict(zip(['min','median','p90','p95','max'],np.quantile(distance,[0,.5,.9,.95,1]).tolist())),
    'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'inputs').iterdir()},
    'versions':{'python':platform.python_version(), 'numpy':np.__version__, 'pandas':pd.__version__, 'scipy':scipy.__version__},
}
(root/'results/data_audit.json').write_text(json.dumps(audit, indent=2)+'\n')
print(summary.to_string())
print(bins[bins.n>0].to_string())
print(json.dumps(audit, indent=2))
