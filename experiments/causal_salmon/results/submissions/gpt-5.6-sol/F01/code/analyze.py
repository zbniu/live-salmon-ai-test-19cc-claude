"""Analyze the complete supplied data. No internet or external data are used.

Descriptive associations are not interpreted as causal effects. Counterfactual
examples are hypothetical identification demonstrations, not generated records.
"""
from pathlib import Path
import csv
import hashlib
import json
import platform
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
source = ROOT / 'inputs' / 'data.csv'
with source.open(encoding='utf-8', newline='') as handle:
    reader = csv.DictReader(handle)
    assert reader.fieldnames == ['x', 'y', 'z']
    rows = list(reader)
data = np.array([[float(r[k]) for k in ['x', 'y', 'z']] for r in rows])
assert data.shape == (2000, 3)
assert np.isfinite(data).all()
x, y, z = data.T
assert set(x) == {0.0, 1.0}
assert ((y >= 0) & (y <= 100)).all()
end_score = y + z
treated = x == 1
assert treated.sum() == 600

summary = []
for value in [0, 1]:
    mask = x == value
    record = {'x': value, 'n': int(mask.sum())}
    for name, column in [('y', y), ('z', z), ('end_score', end_score)]:
        vals = column[mask]
        record.update({name + '_mean': float(vals.mean()),
                       name + '_sd': float(vals.std(ddof=1)),
                       name + '_min': float(vals.min()),
                       name + '_max': float(vals.max())})
    summary.append(record)
with (OUT / 'group_summary.csv').open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(summary[0]))
    writer.writeheader()
    writer.writerows(summary)

# Descriptive ordinary least squares with heteroskedasticity-robust HC3 SEs.
# These SEs quantify model-based association uncertainty, not causal uncertainty.
centered_y = (y - y.mean()) / 10
models = []
for degree in [1, 3]:
    design = np.column_stack([np.ones(len(x)), x] +
                             [centered_y ** j for j in range(1, degree + 1)])
    beta, _, rank, _ = np.linalg.lstsq(design, z, rcond=None)
    assert rank == design.shape[1]
    inv = np.linalg.inv(design.T @ design)
    residuals = z - design @ beta
    leverage = np.einsum('ij,jk,ik->i', design, inv, design)
    scores = design * (residuals / (1 - leverage))[:, None]
    covariance = inv @ (scores.T @ scores) @ inv
    se = np.sqrt(covariance[1, 1])
    models.append({'model': 'z ~ x + polynomial(y), degree ' + str(degree),
                   'n': len(x), 'x_coefficient': float(beta[1]),
                   'x_HC3_standard_error': float(se),
                   'x_normal_95_CI_low': float(beta[1] - 1.96 * se),
                   'x_normal_95_CI_high': float(beta[1] + 1.96 * se),
                   'interpretation': 'association only; not identified causal effect'})
with (OUT / 'descriptive_regressions.csv').open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(models[0]))
    writer.writeheader()
    writer.writerows(models)

# All rows contribute to the band summary. Zero-cell means remain blank.
bands = []
for low in range(0, 100, 10):
    mask = (y >= low) & ((y < low + 10) if low < 90 else (y <= 100))
    rec = {'y_lower': low, 'y_upper': low + 10}
    for value in [0, 1]:
        selected = mask & (x == value)
        rec['n_x' + str(value)] = int(selected.sum())
        rec['mean_z_x' + str(value)] = float(z[selected].mean()) if selected.any() else ''
    bands.append(rec)
assert sum(b['n_x0'] + b['n_x1'] for b in bands) == 2000
with (OUT / 'score_bands.csv').open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(bands[0]))
    writer.writeheader()
    writer.writerows(bands)

mean_treated_end = float(end_score[treated].mean())
results = {
    'validation': {'rows': len(rows), 'columns': ['x', 'y', 'z'],
                   'missing_or_nonfinite_values': 0,
                   'attendees': int(treated.sum()), 'nonattendees': int((~treated).sum()),
                   'all_observed_end_scores_in_0_100': bool(((end_score >= 0) & (end_score <= 100)).all()),
                   'global_end_score_min': float(end_score.min()),
                   'global_end_score_max': float(end_score.max()),
                   'distinct_y': int(len(np.unique(y)))},
    'group_summary': summary,
    'crude_gain_difference_points': float(z[treated].mean() - z[~treated].mean()),
    'crude_baseline_difference_points': float(y[treated].mean() - y[~treated].mean()),
    'descriptive_regressions': models,
    'score_support': {'min_treated_y': float(y[treated].min()),
                      'max_treated_y': float(y[treated].max()),
                      'min_control_y': float(y[~treated].min()),
                      'max_control_y': float(y[~treated].max()),
                      'controls_below_min_treated_y': int(((~treated) & (y < y[treated].min())).sum()),
                      'controls_at_or_above_min_treated_y': int(((~treated) & (y >= y[treated].min())).sum())},
    'causal_ATT_point_identified': False,
    'range_bounds_if_both_potential_end_scores_are_in_0_100': {
        'lower_points': mean_treated_end - 100, 'upper_points': mean_treated_end,
        'note': 'Identification bounds, not a confidence interval or point estimate.'},
    'hypothetical_counterfactual_examples': {
        'note': 'Unobserved end scores for attendees only. Factual data and selection are unchanged.',
        'zero_effect': {'end0': 'observed end1', 'ATT_points': 0},
        'positive_effect': {'end0': '0.99 * observed end1', 'ATT_points': 0.01 * mean_treated_end},
        'negative_effect': {'end0': '0.99 * observed end1 + 1', 'ATT_points': 0.01 * mean_treated_end - 1}},
    'provenance': {'data_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                   'study_description_sha256': hashlib.sha256((ROOT / 'inputs' / 'STUDY_DESCRIPTION.md').read_bytes()).hexdigest(),
                   'python': sys.version, 'numpy': np.__version__, 'platform': platform.platform()}
}
(OUT / 'analysis.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
print(json.dumps(results, indent=2))
print('SUCCESS: all 2000 rows used; no records dropped or values imputed.')
