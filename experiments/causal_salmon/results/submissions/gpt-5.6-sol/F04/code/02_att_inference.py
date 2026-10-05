"""Uncertainty for the finite-study average effect among actual recipients.

Under complete random assignment, D - ATT_selected equals the treated-control
difference in untreated potential outcomes. Its randomization variance is
S0_squared * (1/n1 + 1/n0). The random control sample's observed variance
estimates S0_squared, without assuming constant effects. The interval uses
a large-sample normal approximation, not an exact finite-sample pivot.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats

root = Path(__file__).resolve().parents[1]
d = pd.read_csv(root.parent / 'upload' / 'data(5).csv')
assert len(d) == 2000 and d.isna().sum().sum() == 0
treated = d.loc[d.x == 1, 'z']
controls = d.loc[d.x == 0, 'z']
estimate = float(treated.mean() - controls.mean())
variance0 = float(controls.var(ddof=1))
variance = variance0 * (1/len(treated) + 1/len(controls))
se = np.sqrt(variance)
critical = stats.norm.ppf(.975)
result = {
 'target': 'average causal effect on change among the 600 actual recipients',
 'estimator': 'treated mean change minus control mean change',
 'estimate_points': estimate,
 'untreated_potential_outcome_variance_estimated_from_controls': variance0,
 'se_randomization_ATT': float(se),
 'ci95_lower': float(estimate-critical*se),
 'ci95_upper': float(estimate+critical*se),
 'interval_method': 'large-sample normal randomization interval for the selected-recipient average effect',
 'variance_identity': '(1/n_treated + 1/n_control) * S0_squared',
 'interpretation': 'Approximate repeated-randomization coverage of the effect for whichever units receive Q; not an exact counterfactual reconstruction.',
}
(root / 'results' / 'att_inference.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))

# Independent arithmetic check of the OLS/HC3 implementation used previously:
# in an intercept-and-treatment model, HC3 has this closed form.
X = np.column_stack([np.ones(len(d)), d.x.to_numpy()])
beta = np.linalg.lstsq(X, d.z.to_numpy(), rcond=None)[0]
inverse = np.linalg.inv(X.T @ X)
residual = d.z.to_numpy() - X @ beta
h = np.einsum('ij,jk,ik->i', X, inverse, X)
V = inverse @ (X.T @ (X * (residual/(1-h))[:,None]**2)) @ inverse
closed_form = treated.var(ddof=1)/(len(treated)-1) + controls.var(ddof=1)/(len(controls)-1)
assert np.isclose(beta[1], estimate, rtol=1e-12, atol=1e-12)
assert np.isclose(V[1,1], closed_form, rtol=1e-12, atol=1e-12)
check = {'mean_contrast_matches_OLS': True, 'HC3_matches_closed_form': True,
 'HC3_computed_variance': float(V[1,1]), 'HC3_closed_form_variance': float(closed_form)}
(root / 'results' / 'numerical_checks.json').write_text(json.dumps(check, indent=2) + '\n')
print('\nNumerical checks:', json.dumps(check, indent=2))
