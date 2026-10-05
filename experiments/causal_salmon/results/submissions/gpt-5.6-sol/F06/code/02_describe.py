"""Read every record and produce validation and descriptive trial results."""
import hashlib
import json
import platform
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import scipy
from scipy import stats

root = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1]).resolve()
out = root / 'results'
out.mkdir(parents=True, exist_ok=True)
d = pd.read_csv(source)
assert list(d.columns) == ['x', 'y', 'z']
assert len(d) == 2000 and not d.isna().any().any()
assert d['x'].isin([0, 1]).all() and int(d['x'].sum()) == 600
assert np.isfinite(d.to_numpy()).all()
summary = d.groupby('x')[['y', 'z']].agg(['count', 'mean', 'std', 'min', 'max'])
summary.to_csv(out / '02_group_summary.csv')
t = d.loc[d.x == 1, 'z'].to_numpy()
c = d.loc[d.x == 0, 'z'].to_numpy()
diff = float(t.mean() - c.mean())
a, b = t.var(ddof=1)/len(t), c.var(ddof=1)/len(c)
se = float(np.sqrt(a+b))
df = float((a+b)**2/(a*a/(len(t)-1)+b*b/(len(c)-1)))
crit = stats.t.ppf(.975, df)
bins = pd.cut(d.y, bins=np.linspace(0, 100, 11), include_lowest=True)
bin_summary = d.groupby([bins, 'x'], observed=True).agg(n=('z', 'size'), mean_y=('y', 'mean'), mean_z=('z', 'mean'), sd_z=('z', 'std'))
bin_summary.to_csv(out / '02_baseline_bins.csv')
result = {
    'input': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'shape': list(d.shape), 'missing': d.isna().sum().to_dict(),
    'counts': {str(k): int(v) for k,v in d.x.value_counts().sort_index().items()},
    'baseline_difference': float(d.loc[d.x==1,'y'].mean()-d.loc[d.x==0,'y'].mean()),
    'range_y': [float(d.y.min()), float(d.y.max())],
    'range_z': [float(d.z.min()), float(d.z.max())],
    'range_end_score': [float((d.y+d.z).min()), float((d.y+d.z).max())],
    'unadjusted': {'treated_mean': float(t.mean()), 'control_mean': float(c.mean()),
        'difference': diff, 'se': se, 'welch_df': df,
        'ci95': [float(diff-crit*se), float(diff+crit*se)],
        'p_two_sided': float(2*stats.t.sf(abs(diff/se), df))},
    'correlations_by_arm': {str(x): float(g.y.corr(g.z)) for x,g in d.groupby('x')},
    'versions': {'python': platform.python_version(), 'numpy': np.__version__,
        'pandas': pd.__version__, 'scipy': scipy.__version__}
}
(out / '02_descriptive.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
print(summary.to_string())
print(bin_summary.to_string())
