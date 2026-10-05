"""Randomization-based uncertainty for the realized attendees' mean effect.

If ATT_T = mean_T[Z(1)-Z(0)], then D-ATT_T = mean_T Z(0)-mean_C Z(0).
Across complete random assignments, this error has mean zero and variance
S_0^2*(1/n_T + 1/n_C). The observed controls' sample variance estimates S_0^2.
The interval below is a large-sample randomization approximation.
Also perform a Monte Carlo randomization test of the sharp no-effect null.
"""
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from scipy import stats

root = Path(__file__).resolve().parents[1]
d = pd.read_csv(sys.argv[1])
z = d.z.to_numpy()
mask = d.x.to_numpy() == 1
nt, nc = int(mask.sum()), int((~mask).sum())
diff = float(z[mask].mean() - z[~mask].mean())
control_var = float(z[~mask].var(ddof=1))
se = float(np.sqrt(control_var * (1/nt + 1/nc)))
critical = float(stats.norm.ppf(.975))
seed, repetitions = 20261004, 99999
rng = np.random.default_rng(seed)
extreme = 0
total = z.sum()
draws = np.empty(repetitions)
for i in range(repetitions):
    selected_sum = z[rng.choice(len(z), size=nt, replace=False)].sum()
    value = selected_sum/nt - (total-selected_sum)/nc
    draws[i] = value
    extreme += abs(value) >= abs(diff)-1e-12
p = (extreme+1)/(repetitions+1)
result = {
    'estimand': 'Mean Z(1)-Z(0) for the 600 actual attendees',
    'estimator': 'Unadjusted attendee minus nonattendee mean observed gain',
    'effect': diff, 'control_sample_variance': control_var,
    'randomization_error_se': se,
    'approximate_randomization_ci95': [diff-critical*se, diff+critical*se],
    'interpretation': 'Approximate coverage over the random draw, targeting the attendees selected in each draw; not an exact interval and not an individual-effect interval.',
    'sharp_null_test': {
        'null': 'Z_i(1)=Z_i(0) for every student',
        'statistic': 'absolute difference in means',
        'seed': seed, 'repetitions': repetitions, 'extreme_draws': int(extreme),
        'p_two_sided_plus_one': p,
        'monte_carlo_se_approx': float(np.sqrt(p*(1-p)/(repetitions+1)))
    }
}
np.save(root/'results'/'04_randomization_draws.npy', draws)
(root/'results'/'04_att_inference.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
