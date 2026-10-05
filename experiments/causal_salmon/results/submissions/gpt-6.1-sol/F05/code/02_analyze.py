"""Finite-population randomization inference for the average effect on recipients.

The primary estimator is the unadjusted difference in means. Its error relative
to the *realized treated-group* mean effect is exactly the difference between
treated and control means of the untreated potential change, z(0). Under complete
randomization, Var(error) = (1/n1 + 1/n0) S_0^2. The control sample variance
estimates S_0^2. Normal intervals are approximate, not exact randomization bounds.

Baseline adjustment is a sensitivity analysis, not a search over primary tests.
Control-only polynomial regressions predict the recipients' mean untreated
change. Residual-based randomization SEs are first-order approximations; they
ignore higher-order uncertainty from fitting the adjustment in this same draw.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'submission' / 'results'
d = pd.read_csv(ROOT / 'upload' / 'data(20261004-180728).csv')
assert len(d) == 2000 and int(d.x.sum()) == 600 and not d.isna().any().any()
c, t = d[d.x==0], d[d.x==1]
n0, n1 = len(c), len(t)
crit = stats.norm.ppf(.975)
mean_diff = float(t.z.mean()-c.z.mean())
se = float(np.sqrt(c.z.var(ddof=1)*(1/n1+1/n0)))
primary = {'estimator':'unadjusted randomized difference in means',
    'estimand':'mean z(1)-z(0) among the 600 actual recipients (SATT)',
    'effect_points':mean_diff, 'se_points':se,
    'approx_95ci_low':mean_diff-crit*se, 'approx_95ci_high':mean_diff+crit*se,
    'treated_mean_change':float(t.z.mean()), 'control_mean_change':float(c.z.mean()),
    'treated_mean_baseline':float(t.y.mean()), 'control_mean_baseline':float(c.y.mean()),
    'variance_formula':'control sample variance of z * (1/600 + 1/1400)',
    'interval_method':'normal approximation under complete randomization; finite treated-group target'}
rows = [{'method':'Unadjusted (primary)', 'effect':mean_diff,'se':se,
    'ci_low':primary['approx_95ci_low'],'ci_high':primary['approx_95ci_high']}]
fits = {}
# Center/scale baseline for stable polynomial fitting. This uses baseline only.
yc = (c.y.to_numpy()-60)/10
yt = (t.y.to_numpy()-60)/10
for degree in [1,2,3]:
    Xc = np.vander(yc, degree+1, increasing=True)
    Xt = np.vander(yt, degree+1, increasing=True)
    beta = np.linalg.lstsq(Xc,c.z.to_numpy(),rcond=None)[0]
    residual = c.z.to_numpy()-Xc@beta
    untreated = float((Xt@beta).mean())
    estimate = float(t.z.mean()-untreated)
    rvar = float(residual@residual/(n0-Xc.shape[1]))
    adj_se = float(np.sqrt(rvar*(1/n1+1/n0)))
    rows.append({'method':f'Control-only polynomial degree {degree} (sensitivity)',
        'effect':estimate,'se':adj_se,'ci_low':estimate-crit*adj_se,'ci_high':estimate+crit*adj_se})
    fits[str(degree)] = {'basis':'powers of (y-60)/10, including intercept',
        'coefficients':beta.tolist(),'predicted_untreated_mean_for_recipients':untreated,
        'control_residual_sd':float(np.sqrt(rvar)),
        'control_r_squared':float(1-residual@residual/np.sum((c.z-c.z.mean())**2))}

# Flexible baseline-only sensitivity: ten strata chosen by pooled baseline
# deciles, averaging stratum contrasts with the actual recipients' proportions.
d['stratum'] = pd.qcut(d.y,10,labels=False)
stratum_rows = []
for k,g in d.groupby('stratum'):
    g0,g1 = g[g.x==0],g[g.x==1]
    assert len(g0)>1 and len(g1)>1
    stratum_rows.append({'stratum':int(k)+1,'n_control':len(g0),'n_treated':len(g1),
        'treated_weight':len(g1)/n1,'mean_control':float(g0.z.mean()),
        'mean_treated':float(g1.z.mean()),'contrast':float(g1.z.mean()-g0.z.mean()),
        'control_variance':float(g0.z.var(ddof=1))})
strata = pd.DataFrame(stratum_rows)
stratum_est = float(np.sum(strata.treated_weight*strata.contrast))
stratum_se = float(np.sqrt(np.sum(strata.treated_weight**2*strata.control_variance*
    (1/strata.n_treated+1/strata.n_control))))
rows.append({'method':'Recipient-weighted baseline deciles (sensitivity)',
    'effect':stratum_est,'se':stratum_se,'ci_low':stratum_est-crit*stratum_se,
    'ci_high':stratum_est+crit*stratum_se})
result = pd.DataFrame(rows)
print('PRIMARY: randomized mean comparison targeting actual recipients\n'+json.dumps(primary,indent=2))
print('\nAnalysis comparison (all 2,000 rows used):\n'+result.to_string(index=False))
print('\nAdjustment fits:\n'+json.dumps(fits,indent=2))
result.to_csv(OUT/'effect_estimates.csv',index=False)
strata.to_csv(OUT/'stratum_effects.csv',index=False)
(OUT/'analysis.json').write_text(json.dumps({'primary':primary,'baseline_adjustment_fits':fits,
    'sensitivity_estimates':rows[1:]},indent=2),encoding='utf-8')
print('Outputs: effect_estimates.csv, stratum_effects.csv, analysis.json')
