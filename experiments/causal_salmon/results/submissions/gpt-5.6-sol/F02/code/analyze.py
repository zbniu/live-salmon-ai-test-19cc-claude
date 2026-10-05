"""Analyze all supplied rows. No external data or internet access.

Run from the workspace root with the primary runtime Python interpreter.
Input paths may alternatively be passed as the first two command-line arguments.
"""
import csv
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'
OUT.mkdir(parents=True, exist_ok=True)
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / 'upload/data(3).csv'
STUDY = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT.parent / 'upload/STUDY_DESCRIPTION(3).md'
with DATA.open(encoding='utf-8', newline='') as f:
    reader = csv.DictReader(f)
    assert reader.fieldnames == ['x', 'y', 'z'], reader.fieldnames
    rows = list(reader)
assert len(rows) == 2000, len(rows)
values = np.array([[float(row[k]) for k in ['x', 'y', 'z']] for row in rows])
assert np.isfinite(values).all(), 'Nonfinite or missing values'
x, y, z = values.T
assert set(x) == {0.0, 1.0}
assert int(x.sum()) == 600
assert ((y >= 0) & (y <= 100)).all()
followup = y + z
assert ((followup >= 0) & (followup <= 100)).all()
t = x == 1
c = ~t

summary = []
for label, mask in [('Q', t), ('No Q', c)]:
    item = {'group': label, 'n': int(mask.sum())}
    for name, arr in [('baseline_y', y), ('change_z', z), ('followup', followup)]:
        item.update({f'{name}_mean': float(arr[mask].mean()),
                     f'{name}_sd': float(arr[mask].std(ddof=1)),
                     f'{name}_min': float(arr[mask].min()),
                     f'{name}_max': float(arr[mask].max())})
    summary.append(item)
with (OUT / 'group_summary.csv').open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(summary[0]))
    w.writeheader()
    w.writerows(summary)

# Descriptive regression sensitivity: x coefficient with common baseline slopes.
# Center/scale baseline for stable polynomial calculations. Neither coefficient
# has a causal interpretation justified by the supplied assignment mechanism.
a = (y - 50) / 10
models = []
for degree in [1, 3]:
    design = np.column_stack([np.ones(len(x)), x] + [a**j for j in range(1, degree+1)])
    beta, _, rank, _ = np.linalg.lstsq(design, z, rcond=None)
    resid = z - design @ beta
    r2 = 1 - float(resid @ resid) / float(((z-z.mean())**2).sum())
    models.append({'baseline_polynomial_degree': degree,
                   'n': len(x), 'rank': int(rank),
                   'x_coefficient_association_only': float(beta[1]),
                   'coefficients': beta.tolist(), 'r_squared': r2})

# Baseline bins describe observed overlap, without trimming any records.
bin_rows = []
for low in range(0, 100, 10):
    b = (y >= low) & ((y < low+10) if low < 90 else (y <= 100))
    bt, bc = b & t, b & c
    bin_rows.append({'baseline_bin': f'{low}-{low+10}', 'n_Q': int(bt.sum()),
                     'n_no_Q': int(bc.sum()),
                     'mean_z_Q': float(z[bt].mean()) if bt.any() else None,
                     'mean_z_no_Q': float(z[bc].mean()) if bc.any() else None})
with (OUT / 'baseline_bins.csv').open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(bin_rows[0]))
    w.writeheader()
    w.writerows(bin_rows)

# Finite-study average effect among the 600 treated:
# mean(z1-z0). If each potential follow-up is on the same [0,100] scale,
# z0 is between -y and 100-y. These are logical bounds, not confidence limits.
bounds = [float(followup[t].mean()-100), float(followup[t].mean())]

# Concrete alternative missing counterfactuals for treated units. All scenarios
# leave every observed row and the described assignment process unchanged.
scenarios = []
for label, z0 in [('zero_effect', z[t].copy()),
                  ('positive_effect_1_point', z[t]-1),
                  ('negative_effect_1_point', z[t]+1)]:
    f0 = y[t] + z0
    scenarios.append({'scenario': label, 'mean_effect': float((z[t]-z0).mean()),
                      'counterfactual_followup_min': float(f0.min()),
                      'counterfactual_followup_max': float(f0.max()),
                      'within_0_100': bool(((f0 >= 0) & (f0 <= 100)).all())})

results = {
    'inputs': {str(p): {'bytes': p.stat().st_size,
                        'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
               for p in [DATA, STUDY]},
    'software': {'python': platform.python_version(), 'numpy': np.__version__},
    'validation': {'rows': len(rows), 'columns': ['x', 'y', 'z'],
                   'missing_or_nonfinite': 0, 'treated': int(t.sum()),
                   'untreated': int(c.sum()), 'rows_excluded': 0},
    'group_summary': summary,
    'raw_change_difference_association_only': float(z[t].mean()-z[c].mean()),
    'baseline_mean_difference': float(y[t].mean()-y[c].mean()),
    'baseline_overlap': {
        'treated_min': float(y[t].min()), 'treated_max': float(y[t].max()),
        'untreated_min': float(y[c].min()), 'untreated_max': float(y[c].max()),
        'untreated_at_or_above_treated_min': int((c & (y >= y[t].min())).sum()),
        'treated_outside_untreated_observed_range': int((t & ((y < y[c].min()) | (y > y[c].max()))).sum())},
    'descriptive_regressions': models,
    'finite_study_ATT_logical_bounds_assuming_0_100_potential_followup': bounds,
    'alternative_counterfactual_scenarios': scenarios,
    'causal_effect_point_identified': False}
(OUT / 'analysis.json').write_text(json.dumps(results, indent=2, allow_nan=False)+'\n', encoding='utf-8')
print(json.dumps(results, indent=2, allow_nan=False))
