import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'upload' / 'data(20261004-071423).csv'
OUT = ROOT / 'submission' / 'results'
OUT.mkdir(parents=True, exist_ok=True)

with DATA.open(newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
x = np.array([int(r['x']) for r in rows])
y = np.array([float(r['y']) for r in rows])
z = np.array([float(r['z']) for r in rows])
assert len(rows) == 2000 and set(x) == {0, 1}

summary = {
    'n': len(x), 'treated': int(sum(x)), 'untreated': int(sum(1-x)),
    'treated_y_range': [float(y[x==1].min()), float(y[x==1].max())],
    'control_y_range': [float(y[x==0].min()), float(y[x==0].max())],
    'treated_y_mean': float(y[x==1].mean()),
    'control_y_mean': float(y[x==0].mean()),
    'treated_z_mean': float(z[x==1].mean()),
    'control_z_mean': float(z[x==0].mean()),
    'raw_z_difference': float(z[x==1].mean()-z[x==0].mean()),
    'bins': []
}
for lo in np.arange(0, 100, 5):
    mask = (y >= lo) & (y < lo+5)
    t, c = mask & (x==1), mask & (x==0)
    if mask.sum():
        summary['bins'].append({
            'y_interval': [int(lo), int(lo+5)], 'treated': int(t.sum()),
            'controls': int(c.sum()),
            'treated_z_mean': float(z[t].mean()) if t.any() else None,
            'control_z_mean': float(z[c].mean()) if c.any() else None,
        })

dest = OUT / 'exploration.json'
dest.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print(json.dumps(summary, indent=2))
print(f'Wrote {dest.relative_to(ROOT)}')
