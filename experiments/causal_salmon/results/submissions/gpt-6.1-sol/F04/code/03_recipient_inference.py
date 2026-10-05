"""Inference for the realized recipients, rather than all-unit ATE.

For a complete random draw of n1 recipients, with fixed potential changes z(0),
tau_T = mean_T[z(1)-z(0)]. The error of the difference-in-means estimator is
mean_T[z(0)] - mean_C[z(0)], whose randomization variance is
(1/n1+1/n0)*S_0^2. Control sample variance is unbiased for S_0^2.
No assumption of constant unit-level effects is needed for this error identity.
The normal interval is approximate, not exact finite-sample inference.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'submission/results'
d=pd.read_csv(ROOT/'upload/data(20261004-180720).csv')
t=d.x.eq(1)
n1,n0=int(t.sum()),int((~t).sum())
estimate=float(d.loc[t,'z'].mean()-d.loc[~t,'z'].mean())
control_variance=float(d.loc[~t,'z'].var(ddof=1))
se=float(np.sqrt((1/n1+1/n0)*control_variance))
critical=float(stats.norm.ppf(.975))
result={'estimand':'Realized-recipient average causal effect: mean_T[z(1)-z(0)]',
    'adopted_estimate':estimate,'randomization_error_se':se,
    'approximate_95_ci_low':estimate-critical*se,'approximate_95_ci_high':estimate+critical*se,
    'control_sample_variance':control_variance,
    'variance_formula':'(1/n_treated + 1/n_control) * sample_variance(z_control)',
    'error_identity':'estimated_effect - recipient_effect = mean_T[z(0)] - mean_C[z(0)]',
    'interpretation':'Design-unbiased estimation error over complete random assignments. Confidence coverage is approximate over assignments, not exact conditional on the observed selected set.',
    'qualification':'Actual recipient counterfactuals and individual causal effects are unobserved; randomization supports statistical inference rather than an exact known effect.'}
(OUT/'recipient_inference.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
print('\nThe earlier Welch interval in analysis_results.json is retained as the conventional all-unit ATE comparison; this recipient-specific interval is adopted for the stated question.')
print('Output: recipient_inference.json')
