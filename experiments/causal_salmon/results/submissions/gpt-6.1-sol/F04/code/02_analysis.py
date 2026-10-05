"""Randomized mean comparison and recipient-targeted baseline adjustments.

Primary: difference in observed means, with Welch/Neyman standard error.
Sensitivity: separate-arm polynomial regressions standardized to recipients'
baseline values. HC3 sandwich variance is conditional on the baseline design.
The question concerns average causal effect; individual effects are not observed.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'submission/results'
d = pd.read_csv(ROOT / 'upload/data(20261004-180720).csv')
x, y, z = (d[c].to_numpy() for c in ['x', 'y', 'z'])
treated = x == 1
n1, n0 = int(treated.sum()), int((~treated).sum())
z1, z0 = z[treated], z[~treated]
delta = z1.mean() - z0.mean()
v1, v0 = z1.var(ddof=1) / n1, z0.var(ddof=1) / n0
se = np.sqrt(v1 + v0)
df = (v1 + v0)**2 / (v1**2/(n1-1) + v0**2/(n0-1))
critical = stats.t.ppf(.975, df)
primary = {'method': 'Unadjusted randomized difference in means', 'estimate': float(delta),
    'se': float(se), 'ci_low': float(delta-critical*se), 'ci_high': float(delta+critical*se),
    'df': float(df), 't': float(delta/se), 'p_two_sided': float(2*stats.t.sf(abs(delta/se),df)),
    'p_one_sided_increase': float(stats.t.sf(delta/se,df)),
    'treated_mean_change': float(z1.mean()), 'control_mean_change': float(z0.mean()),
    'treated_n': n1, 'control_n': n0}
print('PRIMARY RANDOMIZED COMPARISON:\n' + json.dumps(primary, indent=2))

def fit_hc3(A, response):
    bread = np.linalg.inv(A.T @ A)
    beta = bread @ A.T @ response
    residual = response - A @ beta
    leverage = np.einsum('ij,jk,ik->i', A, bread, A)
    weighted = A * (residual/(1-leverage))[:, None]
    covariance = bread @ (weighted.T @ weighted) @ bread
    return beta, covariance, residual, leverage

# Scaling/centering uses only pretreatment baseline measurements.
w = (y-y[treated].mean())/15
models = []
prediction_table = d.copy()
for degree in [1, 2, 3]:
    basis = np.column_stack([w**k for k in range(degree+1)])
    A = np.column_stack([basis*(1-x[:,None]), basis*x[:,None]])
    beta, covariance, residual, leverage = fit_hc3(A, z)
    recipient_basis = basis[treated].mean(axis=0)
    L = np.concatenate([-recipient_basis, recipient_basis])
    effect = float(L @ beta)
    standard_error = float(np.sqrt(L @ covariance @ L))
    ci = effect + np.array([-1,1])*stats.norm.ppf(.975)*standard_error
    counterfactual = float(recipient_basis @ beta[:degree+1])
    record = {'method': f'Separate-arm degree-{degree} polynomial, recipient standardization',
        'degree': degree, 'estimate': effect, 'se': standard_error, 'ci_low': float(ci[0]),
        'ci_high': float(ci[1]), 'p_two_sided': float(2*stats.norm.sf(abs(effect/standard_error))),
        'recipient_predicted_mean_without_Q': counterfactual,
        'residual_sd_control': float(np.sqrt(np.sum(residual[~treated]**2)/(n0-degree-1))),
        'residual_sd_treated': float(np.sqrt(np.sum(residual[treated]**2)/(n1-degree-1))),
        'max_leverage': float(leverage.max()), 'coefficients': beta.tolist(),
        'hc3_covariance': covariance.tolist()}
    if degree == 1:
        # Interaction tests baseline slope difference, without assuming homogeneity.
        Lslope = np.array([0.,-1./15,0.,1./15])
        slope_difference = float(Lslope @ beta)
        slope_se = float(np.sqrt(Lslope @ covariance @ Lslope))
        record.update({'control_slope_per_baseline_point': float(beta[1]/15),
            'treated_slope_per_baseline_point': float(beta[3]/15),
            'slope_difference': slope_difference, 'slope_difference_se': slope_se,
            'slope_interaction_p_two_sided': float(2*stats.norm.sf(abs(slope_difference/slope_se)))})
    models.append(record)
    prediction_table[f'control_mean_model_degree_{degree}'] = basis @ beta[:degree+1]
    prediction_table[f'observed_arm_residual_degree_{degree}'] = residual
    print('\nBASELINE ADJUSTMENT:\n' + json.dumps({k:v for k,v in record.items() if k not in ['coefficients','hc3_covariance']},indent=2))
prediction_table.to_csv(OUT / 'regression_diagnostics.csv',index=False)

# Transparent coarser standardization: 6 equal-width baseline strata, all rows.
bins = np.linspace(45,75,7)
band = pd.cut(y,bins,include_lowest=True)
rows=[]
for b in band.categories:
    take = band == b
    a, c = z[take & treated], z[take & ~treated]
    assert len(a) and len(c)
    weight = len(a)/n1
    effect = a.mean()-c.mean()
    variance = a.var(ddof=1)/len(a)+c.var(ddof=1)/len(c)
    rows.append({'baseline_band':str(b),'n_treated':len(a),'n_control':len(c),
        'recipient_weight':weight,'treated_mean':a.mean(),'control_mean':c.mean(),
        'effect':effect,'within_band_variance':variance})
band_table = pd.DataFrame(rows)
band_table.to_csv(OUT/'baseline_strata.csv',index=False)
band_effect = float(sum(r['recipient_weight']*r['effect'] for r in rows))
band_se = float(np.sqrt(sum(r['recipient_weight']**2*r['within_band_variance'] for r in rows)))
stratified = {'method': 'Recipient-weighted six baseline bands, conditional-weight SE',
    'estimate':band_effect,'se':band_se,'ci_low':band_effect-1.95996398454*band_se,
    'ci_high':band_effect+1.95996398454*band_se,
    'note':'Approximate conditional-weight interval; coarsening can leave within-band baseline differences.'}
print('\nSTRATIFIED SENSITIVITY:\n'+json.dumps(stratified,indent=2))

baseline = {'treated_mean':float(y[treated].mean()),'control_mean':float(y[~treated].mean()),
    'mean_difference':float(y[treated].mean()-y[~treated].mean()),
    'standardized_difference':float((y[treated].mean()-y[~treated].mean())/np.sqrt((y[treated].var(ddof=1)+y[~treated].var(ddof=1))/2)),
    'treated_min':float(y[treated].min()),'treated_max':float(y[treated].max()),
    'control_min':float(y[~treated].min()),'control_max':float(y[~treated].max())}
results = {'primary':primary,'baseline':baseline,'baseline_adjusted_models':models,'stratified_sensitivity':stratified,
    'analysis_choices':{'primary':'Unadjusted randomized comparison; chosen before inferential fits.',
    'sensitivities':'Recipient-targeted polynomials degrees 1, 2, 3 and six five-point baseline strata. No significance-based model selection.',
    'uncertainty':'Primary Welch/Neyman approximation. Polynomial sensitivity HC3 normal intervals conditional on baseline design.',
    'estimand':'Average Q effect for recipients; exact individual and realized recipient counterfactuals are unobserved.'}}
(OUT/'analysis_results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
comparison = [{k:primary[k] for k in ['method','estimate','se','ci_low','ci_high']}]+[
    {k:r[k] for k in ['method','estimate','se','ci_low','ci_high']} for r in models+[stratified]]
pd.DataFrame(comparison).to_csv(OUT/'effect_estimates.csv',index=False)
print('\nCOMPARISON OF ESTIMATES:\n'+pd.DataFrame(comparison).to_string(index=False))
print('\nOutputs: analysis_results.json, effect_estimates.csv, baseline_strata.csv, regression_diagnostics.csv')
