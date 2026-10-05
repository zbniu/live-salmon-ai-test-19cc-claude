"""Estimate ATT with baseline-score standardization; no external data.

Primary: cubic B-spline regression of untreated gain on baseline score,
then average observed treated gain minus predicted untreated gain.
HC3 control-regression covariance plus variance of treated adjusted gains
provides a conventional approximate 95% confidence interval.
Sensitivity: polynomial outcome models, fine score stratification, and
nearest-control matching. These do not assume a constant treatment effect.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.interpolate import BSpline
from scipy.spatial import cKDTree
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'submission/results'
d = pd.read_csv(ROOT / 'upload/data(9).csv')
assert len(d) == 2000 and not d.isna().any().any()
t = d.x.to_numpy() == 1
y = d.y.to_numpy()
z = d.z.to_numpy()
nt, nc = int(t.sum()), int((~t).sum())

def fit_ols_hc3(B, response):
    beta = np.linalg.lstsq(B, response, rcond=None)[0]
    bread = np.linalg.inv(B.T @ B)
    resid = response - B @ beta
    leverage = np.einsum('ij,jk,ik->i', B, bread, B)
    meat = B.T @ (B * (resid/(1-leverage))[:, None]**2)
    cov = bread @ meat @ bread
    return beta, cov, resid

def standardized(B, name, control_mask=None):
    control_mask = ~t if control_mask is None else control_mask
    beta, cov, resid = fit_ols_hc3(B[control_mask], z[control_mask])
    adjusted = z[t] - B[t] @ beta
    v = B[t].mean(axis=0)
    est = float(adjusted.mean())
    se = float(np.sqrt(adjusted.var(ddof=1)/nt + v @ cov @ v))
    return {'method': name, 'att': est, 'se': se,
            'ci95_low': est-1.959963984540054*se,
            'ci95_high': est+1.959963984540054*se,
            'n_treated': nt, 'n_controls': int(control_mask.sum()),
            'mean_counterfactual_gain': float((B[t] @ beta).mean()),
            'control_residual_sd': float(np.sqrt(np.mean(resid**2))),
            'two_sided_normal_p': float(2*norm.sf(abs(est/se)))}, beta, cov

rows = []
raw = float(z[t].mean() - z[~t].mean())
raw_se = float(np.sqrt(z[t].var(ddof=1)/nt + z[~t].var(ddof=1)/nc))
rows.append({'method': 'Unadjusted difference (association)', 'att': raw,
             'se': raw_se, 'ci95_low': raw-1.959963984540054*raw_se,
             'ci95_high': raw+1.959963984540054*raw_se,
             'n_treated': nt, 'n_controls': nc})

# Bounds are fixed score-scale values; knots fixed before outcome modeling.
knots = np.r_[np.repeat(0.,4), [50.,55.,60.,65.,70.], np.repeat(100.,4)]
B = BSpline.design_matrix(y, knots, 3).toarray()
primary, beta, cov = standardized(B, 'Primary: untreated cubic B-spline, knots 50/55/60/65/70')
rows.append(primary)
np.savetxt(OUT / 'primary_spline_coefficients.csv', beta, delimiter=',', header='coefficient', comments='')
np.savetxt(OUT / 'primary_spline_hc3_covariance.csv', cov, delimiter=',')
pred = d.copy()
pred['predicted_untreated_gain'] = B @ beta
pred['observed_minus_predicted_untreated'] = z - B @ beta
pred.to_csv(OUT / 'student_predictions.csv', index=False)

for degree in (1, 2, 3, 4):
    P = np.vander((y-60)/15, N=degree+1, increasing=True)
    result, _, _ = standardized(P, f'Untreated polynomial degree {degree}, all controls')
    rows.append(result)
for degree in (1,2,3):
    P = np.vander((y-66)/10, N=degree+1, increasing=True)
    mask = (~t) & (y >= y[t].min())
    result, _, _ = standardized(P, f'Untreated polynomial degree {degree}, controls in attendee range', mask)
    rows.append(result)

# Fine strata: directly compare gains, averaging bin contrasts with attendee
# counts. No controls below the lowest treated score can influence the result.
stratum_tables = []
for width in (0.5, 1., 2., 2.5, 5.):
    labels = np.floor((y-y[t].min())/width).astype(int)
    pieces = []
    est = var = 0.
    for label in sorted(set(labels[t])):
        tm = t & (labels == label)
        cm = (~t) & (labels == label)
        n1, n0 = int(tm.sum()), int(cm.sum())
        assert n0 > 1 and n1 > 1, (width, label, n1, n0)
        delta = float(z[tm].mean()-z[cm].mean())
        w = n1/nt
        est += w*delta
        var += w*w*(z[tm].var(ddof=1)/n1 + z[cm].var(ddof=1)/n0)
        pieces.append({'width': width, 'lower': y[t].min()+label*width,
                       'upper': y[t].min()+(label+1)*width,
                       'n_treated': n1, 'n_controls': n0,
                       'treated_y_mean': y[tm].mean(), 'control_y_mean': y[cm].mean(),
                       'treated_z_mean': z[tm].mean(), 'control_z_mean': z[cm].mean(),
                       'gain_difference': delta, 'treated_weight': w})
    stratum_tables.extend(pieces)
    se = float(np.sqrt(var))
    rows.append({'method': f'Attendee-weighted strata, width {width:g}',
                 'att': est, 'se': se, 'ci95_low': est-1.959963984540054*se,
                 'ci95_high': est+1.959963984540054*se,
                 'n_treated': nt, 'n_controls': sum(p['n_controls'] for p in pieces)})
pd.DataFrame(stratum_tables).to_csv(OUT / 'stratification_details.csv', index=False)

# Matching with replacement is a check, without a naive matching CI.
tree = cKDTree(y[~t,None])
matching_rows = []
for k in (1,5,10,20):
    distance, indices = tree.query(y[t,None], k=k)
    if k == 1:
        indices, distance = indices[:,None], distance[:,None]
    matched_gain = z[~t][indices].mean(axis=1)
    est = float(np.mean(z[t]-matched_gain))
    matching_rows.append({'k': k, 'att': est,
                          'mean_absolute_baseline_distance': float(distance.mean()),
                          'max_baseline_distance': float(distance.max()),
                          'unique_matched_controls': int(np.unique(indices).size)})
pd.DataFrame(matching_rows).to_csv(OUT / 'matching_sensitivity.csv', index=False)

# Descriptive effect differences by baseline-score region, using the primary
# untreated prediction. This is not used to infer a constant class effect.
regions = []
for lo, hi in ((y[t].min(),60),(60,65),(65,70),(70,75)):
    mask = t & (y >= lo) & (y < hi)
    regions.append({'lower':lo, 'upper':hi, 'n_treated':int(mask.sum()),
                    'adjusted_gain_difference':float((z-B @ beta)[mask].mean())})
pd.DataFrame(regions).to_csv(OUT / 'baseline_region_effects.csv', index=False)

pd.DataFrame(rows).to_csv(OUT / 'effect_estimates.csv', index=False)
(OUT / 'primary_result.json').write_text(json.dumps(primary, indent=2)+'\n')
print('PRIMARY RESULT\n'+json.dumps(primary, indent=2))
print('\nADJUSTMENT SENSITIVITY\n'+pd.DataFrame(rows).to_string(index=False))
print('\nMATCHING SENSITIVITY (no matching confidence intervals)\n'+pd.DataFrame(matching_rows).to_string(index=False))
print('\nDESCRIPTIVE BASELINE REGION EFFECTS\n'+pd.DataFrame(regions).to_string(index=False))
