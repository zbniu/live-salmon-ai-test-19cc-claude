from pathlib import Path
import pandas as pd
import numpy as np
import json, hashlib, sys

root = Path(__file__).resolve().parents[2]
path = root / 'upload' / 'data(20261004-013818).csv'
d = pd.read_csv(path)
assert list(d.columns) == ['x','y','z']
assert len(d) == 2000 and not d.isna().any().any()
assert set(d.x) == {0,1} and d.x.sum() == 600
summary = d.groupby('x').agg(n=('z','size'), y_mean=('y','mean'), y_min=('y','min'), y_max=('y','max'), z_mean=('z','mean'), z_sd=('z','std'), z_min=('z','min'), z_max=('z','max'))
bins = d.assign(baseline_bin=pd.cut(d.y, np.arange(0,101,5), right=False)).groupby(['baseline_bin','x'], observed=False).agg(n=('z','size'), z_mean=('z','mean'), z_sd=('z','std')).reset_index()
out = root / 'submission' / 'results'
summary.to_csv(out/'01_group_summary.csv')
bins.to_csv(out/'01_baseline_bins.csv', index=False)
c = d[d.x == 0]; t = d[d.x == 1]
nearest = np.min(np.abs(t.y.to_numpy()[:,None] - c.y.to_numpy()[None,:]),axis=1)
facts = dict(rows=len(d), columns=list(d.columns), missing=int(d.isna().sum().sum()), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), python=sys.version, pandas=pd.__version__, numpy=np.__version__, duplicates=int(d.duplicated().sum()), baseline_min=float(d.y.min()), baseline_max=float(d.y.max()), followup_min=float((d.y+d.z).min()), followup_max=float((d.y+d.z).max()), treated_above_control_max=int((t.y>c.y.max()).sum()), treated_below_control_min=int((t.y<c.y.min()).sum()), nearest_control_baseline_distance_quantiles=np.quantile(nearest,[0,.5,.9,.95,1]).tolist())
(out/'01_data_checks.json').write_text(json.dumps(facts,indent=2),encoding='utf-8')
print(json.dumps(facts,indent=2))
print(summary.to_string())
print(bins.to_string(index=False))
