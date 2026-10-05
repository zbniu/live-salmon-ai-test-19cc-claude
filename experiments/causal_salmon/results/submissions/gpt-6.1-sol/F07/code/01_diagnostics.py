from pathlib import Path
import json, hashlib, sys
import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[2]
p = root / 'upload/data(20261004-180745).csv'
d = pd.read_csv(p)
assert list(d.columns) == ['x', 'y', 'z']
assert len(d) == 2000 and not d.isna().any().any()
assert set(d.x.unique()) == {0, 1}
out = {'rows': len(d), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
       'python': sys.version, 'duplicate_rows': int(d.duplicated().sum()),
       'groups': {}, 'followup_range': [float((d.y+d.z).min()), float((d.y+d.z).max())]}
for x, g in d.groupby('x'):
    out['groups'][str(x)] = {'n': len(g), 'y_mean': float(g.y.mean()),
       'y_min': float(g.y.min()), 'y_max': float(g.y.max()),
       'z_mean': float(g.z.mean()), 'z_sd': float(g.z.std()),
       'z_min': float(g.z.min()), 'z_max': float(g.z.max())}
t, c = d[d.x == 1], d[d.x == 0]
out['raw_difference'] = float(t.z.mean() - c.z.mean())
out['treated_outside_control_range'] = int(((t.y < c.y.min()) | (t.y > c.y.max())).sum())
out['controls_at_or_above_min_treated'] = int((c.y >= t.y.min()).sum())
cy = np.sort(c.y.to_numpy())
nearest = np.min(np.abs(t.y.to_numpy()[:, None] - cy[None, :]), axis=1)
out['treated_nearest_control_baseline_distance_quantiles'] = dict(zip(['0','0.5','0.9','0.95','1'], map(float,np.quantile(nearest,[0,.5,.9,.95,1]))))
d['baseline_bin'] = pd.cut(d.y, np.arange(0, 105, 5), right=False)
bins = d.groupby(['baseline_bin', 'x'], observed=False).agg(n=('z','size'), mean_y=('y','mean'), mean_z=('z','mean')).reset_index()
bins.to_csv(root/'submission/results/01_baseline_bins.csv', index=False)
(root/'submission/results/01_diagnostics.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps(out, indent=2))
print(bins.to_string(index=False))
