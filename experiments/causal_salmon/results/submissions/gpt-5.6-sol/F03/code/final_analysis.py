"""Attendee-targeted randomization uncertainty and covariate sensitivity checks.

No imports of earlier analysis scripts: earlier executed outputs are read as
records, rather than recomputing those analyses.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats

root=Path(__file__).resolve().parents[1]
d=pd.read_csv(root.parent/'upload'/'data(4).csv')
initial=json.loads((root/'results'/'initial_results.json').read_text())
g0=d[d.x==0]; g1=d[d.x==1]
estimate=initial['unadjusted']['estimate']
# If SATT is the average effect for the realized treated set, then
# D-SATT = mean(Y0_treated)-mean(Y0_control).
# Under complete randomization its variance is S0^2*(1/n1+1/n0).
# Control sample variance is unbiased for finite-population S0^2.
att_se=float(np.sqrt(g0.z.var(ddof=1)*(1/len(g1)+1/len(g0))))
critical=float(stats.norm.ppf(.975))
att={'estimate':estimate,'estimated_randomization_se':att_se,
     'normal_approx_ci95':[estimate-critical*att_se,estimate+critical*att_se],
     'variance_formula':'s_control(z)^2 * (1/n_treated + 1/n_control)',
     'target':'average causal effect for the 600 realized attendees (SATT)',
     'coverage':'large-sample randomization coverage over the original random draw; not exact'}

# Separate linear regressions, expressed as fully interacted pooled regression.
c=(d.y.to_numpy()-g1.y.mean())/10
x=d.x.to_numpy()
b=np.c_[np.ones(len(d)),x,c,x*c]
beta=np.linalg.lstsq(b,d.z.to_numpy(),rcond=None)[0]
residual=d.z.to_numpy()-b@beta
bread=np.linalg.inv(b.T@b)
h=np.einsum('ij,jk,ik->i',b,bread,b)
cov=bread@(b.T@((residual/(1-h))[:,None]**2*b))@bread
se=np.sqrt(np.diag(cov))
adjusted={'ATT_estimate':float(beta[1]),'HC3_se':float(se[1]),
          'conditional_mean_ci95':[float(beta[1]-critical*se[1]),float(beta[1]+critical*se[1])],
          'interaction_per_10_baseline_points':float(beta[3]),
          'interaction_HC3_se':float(se[3]),
          'interaction_p_two_sided':float(2*stats.norm.sf(abs(beta[3]/se[3]))),
          'max_leverage':float(h.max()),
          'interpretation':'secondary linear conditional-mean model standardized to attendees baseline scores'}

# Baseline-only diagnostics are descriptive; assignment mechanism is supplied.
baseline={'treated_minus_control_mean':float(g1.y.mean()-g0.y.mean()),
          'standardized_mean_difference':float((g1.y.mean()-g0.y.mean())/
          np.sqrt((g1.y.var()+g0.y.var())/2)),
          'treated_range':[float(g1.y.min()),float(g1.y.max())],
          'control_range':[float(g0.y.min()),float(g0.y.max())]}
result={'primary_attendee_effect':att,'secondary_baseline_adjustment':adjusted,
        'baseline_diagnostics':baseline}
(root/'results'/'final_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
print('Generated final_results.json. Earlier results retained without rerunning earlier analyses.')
