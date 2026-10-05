"""Complete-data descriptive analysis; no causal identification assumed."""
from pathlib import Path
import csv
import hashlib
import json
import platform
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
source = ROOT / 'inputs' / 'data.csv'
with source.open(encoding='utf-8', newline='') as f:
    reader = csv.DictReader(f)
    assert reader.fieldnames == ['x', 'y', 'z'], reader.fieldnames
    rows = list(reader)
d = np.array([[float(r[k]) for k in ['x', 'y', 'z']] for r in rows])
assert d.shape == (2000, 3), d.shape
assert np.isfinite(d).all()
x, y, z = d.T
assert set(x) == {0.0, 1.0}
assert int(x.sum()) == 600
assert ((y >= 0) & (y <= 100)).all()
end = y + z
summary = []
for group in [0, 1]:
    m = x == group
    r = {'x': group, 'n': int(m.sum())}
    for name, values in [('y', y), ('z', z), ('end_score', end)]:
        for statistic, fn in [('mean', np.mean), ('sd', lambda a: np.std(a, ddof=1)),
                              ('min', np.min), ('max', np.max)]:
            r[f'{name}_{statistic}'] = float(fn(values[m]))
    summary.append(r)
with (OUT / 'group_summary.csv').open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(summary[0])); w.writeheader(); w.writerows(summary)

# HC3 uncertainty describes regression association under a sampling model,
# not causal uncertainty or a randomized-design confidence interval.
regressions = []
u = (y - y.mean()) / y.std()
for degree in [0, 1, 2, 3]:
    A = np.column_stack([np.ones(len(x)), x] + [u**p for p in range(1, degree+1)])
    beta, _, rank, _ = np.linalg.lstsq(A, z, rcond=None)
    assert rank == A.shape[1]
    residual = z - A @ beta
    bread = np.linalg.inv(A.T @ A)
    leverage = np.sum((A @ bread) * A, axis=1)
    scaled = residual / (1 - leverage)
    covariance = bread @ (A.T @ ((scaled**2)[:, None] * A)) @ bread
    se = float(np.sqrt(covariance[1, 1]))
    regressions.append({'degree_y': degree, 'attendance_coefficient': float(beta[1]),
                        'HC3_se': se, 'normal_95_lower': float(beta[1] - 1.96*se),
                        'normal_95_upper': float(beta[1] + 1.96*se),
                        'r_squared': float(1 - np.sum(residual**2) / np.sum((z-z.mean())**2))})
with (OUT / 'associational_regressions.csv').open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(regressions[0])); w.writeheader(); w.writerows(regressions)

# Empirical score support and fixed 10-point score bins; every row is included.
bins = []
for low in range(0, 100, 10):
    m = (y >= low) & ((y <= 100) if low == 90 else (y < low + 10))
    r = {'y_lower': low, 'y_upper': low+10}
    for group in [0, 1]:
        mg = m & (x == group)
        r[f'n_x{group}'] = int(mg.sum())
        r[f'mean_z_x{group}'] = float(z[mg].mean()) if mg.any() else None
    bins.append(r)
with (OUT / 'score_bins.csv').open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(bins[0])); w.writeheader(); w.writerows(bins)

t = x == 1
c = ~t
lo = max(y[t].min(), y[c].min())
hi = min(y[t].max(), y[c].max())
bounded = bool(((end >= 0) & (end <= 100)).all())
results = {
    'input_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'python_version': platform.python_version(), 'numpy_version': np.__version__,
    'rows_used': len(rows), 'missing_values': 0,
    'group_summary': summary,
    'unadjusted_gain_difference_attendees_minus_nonattendees': float(z[t].mean()-z[c].mean()),
    'observed_end_scores_all_in_0_100': bounded,
    'empirical_y_range_overlap': [float(lo), float(hi)],
    'attendees_outside_nonattendee_y_range': int((t & ((y < y[c].min()) | (y > y[c].max()))).sum()),
    'minimum_attendee_y': float(y[t].min()),
    'nonattendees_below_minimum_attendee_y': int((c & (y < y[t].min())).sum()),
    'associational_regressions': regressions,
    'causal_ATT_point_identified': False,
    'scale_only_ATT_bounds_if_counterfactual_end_scores_in_0_100':
        [float(end[t].mean()-100), float(end[t].mean())],
    'counterfactual_examples': [
        {'label': 'zero effect', 'untreated_end_for_attendees': 'observed end score', 'ATT': 0.0},
        {'label': 'benefit', 'untreated_end_for_attendees': '0 for each attendee', 'ATT': float(end[t].mean())},
        {'label': 'harm', 'untreated_end_for_attendees': '100 for each attendee', 'ATT': float(end[t].mean()-100)}
    ]
}
(OUT / 'analysis.json').write_text(json.dumps(results, indent=2, allow_nan=False)+'\n', encoding='utf-8')
print(json.dumps(results, indent=2, allow_nan=False))
print('\nOutput files: group_summary.csv, associational_regressions.csv, score_bins.csv, analysis.json')
