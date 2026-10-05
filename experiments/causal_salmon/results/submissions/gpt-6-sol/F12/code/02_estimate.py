"""Estimate the average effect on Q recipients using only the supplied CSV.

Selection is independent of potential outcomes conditional on baseline y under
the mechanism in the supplied study description. The main estimator fits a
cubic regression spline for E[z(0)|y] among untreated units and averages
z - fitted counterfactual over treated units. Stratified nonparametric bootstrap
resamples units within observed treatment groups for its uncertainty interval.
"""
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
assert len(x) == 2000 and x.sum() == 600


def design(y, knots=(55, 60, 65, 70)):
    t = (y - 60) / 10
    cols = [np.ones_like(t), t, t*t, t*t*t]
    cols.extend(np.maximum(t - (k-60)/10, 0)**3 for k in knots)
    return np.column_stack(cols)


def estimate(y, z, x, knots):
    control, treated = x == 0, x == 1
    b = np.linalg.lstsq(design(y[control], knots), z[control], rcond=None)[0]
    untreated_prediction = design(y[treated], knots) @ b
    return float(np.mean(z[treated] - untreated_prediction)), float(np.mean(untreated_prediction))


def local_control_difference(bandwidth):
    estimates = []
    counts = []
    for yi, zi in zip(y[x==1], z[x==1]):
        nearby = (x==0) & (np.abs(y-yi) <= bandwidth)
        counts.append(int(nearby.sum()))
        estimates.append(zi-z[nearby].mean() if nearby.any() else np.nan)
    return {'estimate': float(np.nanmean(estimates)),
            'matched_treated': int(np.isfinite(estimates).sum()),
            'minimum_control_neighbors': min(counts),
            'median_control_neighbors': float(np.median(counts))}


rng = np.random.default_rng(20261004)
tidx, cidx = np.where(x==1)[0], np.where(x==0)[0]
main, counterfactual = estimate(y, z, x, (55,60,65,70))
bootstrap = []
for _ in range(2000):
    idx = np.concatenate([rng.choice(tidx, len(tidx), replace=True),
                          rng.choice(cidx, len(cidx), replace=True)])
    bootstrap.append(estimate(y[idx], z[idx], x[idx], (55,60,65,70))[0])

result = {
    'estimand': 'sample average treatment effect on the 600 recipients (ATT)',
    'main_method': 'control-only cubic regression spline, knots y=55,60,65,70',
    'main_att_points': main,
    'mean_observed_change_treated': float(z[x==1].mean()),
    'mean_predicted_untreated_change_for_treated': counterfactual,
    'bootstrap_resamples': len(bootstrap),
    'bootstrap_seed': 20261004,
    'bootstrap_percentile_95_interval': [float(v) for v in np.quantile(bootstrap, [.025,.975])],
    'bootstrap_standard_error': float(np.std(bootstrap, ddof=1)),
    'sensitivity': {
        'cubic_polynomial_control_regression_att': estimate(y,z,x,())[0],
        'spline_knots_60_70_att': estimate(y,z,x,(60,70))[0],
        'spline_knots_55_60_65_70_72_5_att': estimate(y,z,x,(55,60,65,70,72.5))[0],
        'local_controls_within_0_5_y': local_control_difference(.5),
        'local_controls_within_1_y': local_control_difference(1),
    }
}
# A separate linear fit, rather than the cubic polynomial design above.
bc = np.linalg.lstsq(np.column_stack((np.ones(len(cidx)), y[cidx])), z[cidx], rcond=None)[0]
result['sensitivity']['linear_control_regression_att'] = float(np.mean(z[tidx]-(bc[0]+bc[1]*y[tidx])))

dest = OUT / 'estimates.json'
dest.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
print(f'Wrote {dest.relative_to(ROOT)}')
