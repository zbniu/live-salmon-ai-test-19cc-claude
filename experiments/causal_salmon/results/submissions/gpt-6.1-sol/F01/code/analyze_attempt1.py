"""Analyze the two supplied files only; descriptive models are not causal estimates."""
from pathlib import Path
import hashlib
import json
import platform
import sys
import numpy as np
import pandas as pd
import scipy
import statsmodels
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'submission' / 'results'
OUT.mkdir(parents=True, exist_ok=True)
DATA = ROOT / 'upload' / 'data(20261004-180654).csv'
STUDY = ROOT / 'upload' / 'STUDY_DESCRIPTION(20261004-180655).md'
df = pd.read_csv(DATA)
assert list(df.columns) == ['x', 'y', 'z']
assert len(df) == 2000 and not df.isna().any().any()
assert set(df.x.unique()) == {0, 1} and int(df.x.sum()) == 600
assert np.isfinite(df.to_numpy()).all()
assert df.y.between(0, 100).all()
df['end_score'] = df.y + df.z
assert df.end_score.between(0, 100).all()

summary = df.groupby('x').agg(
    n=('x', 'size'), y_mean=('y', 'mean'), y_sd=('y', 'std'),
    y_min=('y', 'min'), y_max=('y', 'max'),
    z_mean=('z', 'mean'), z_sd=('z', 'std'),
    z_min=('z', 'min'), z_max=('z', 'max'),
    end_mean=('end_score', 'mean'), end_min=('end_score', 'min'),
    end_max=('end_score', 'max'))
summary.to_csv(OUT / 'group_summary.csv')

# HC3 intervals describe fitted associations under the specified regressions.
# They cannot measure uncertainty about omitted-confounder bias.
yc = (df.y - df.y.mean()) / 10
designs = {
    'unadjusted': pd.DataFrame({'const': 1., 'x': df.x}),
    'linear_start_score': pd.DataFrame({'const': 1., 'x': df.x, 'y_centered_per_10': yc}),
    'cubic_start_score': pd.DataFrame({'const': 1., 'x': df.x,
        'y_centered_per_10': yc, 'y_squared': yc**2, 'y_cubed': yc**3})
}
model_rows = []
model_details = []
for name, design in designs.items():
    fit = sm.OLS(df.z, design).fit(cov_type='HC3')
    ci = fit.conf_int()
    for term in design.columns:
        model_rows.append({'model': name, 'term': term,
            'coefficient': float(fit.params[term]), 'hc3_se': float(fit.bse[term]),
            'ci95_lower': float(ci.loc[term, 0]), 'ci95_upper': float(ci.loc[term, 1]),
            'n': int(fit.nobs), 'r_squared': float(fit.rsquared)})
    model_details.append(name + '\n' + fit.summary().as_text())
pd.DataFrame(model_rows).to_csv(OUT / 'associational_models.csv', index=False)
(OUT / 'associational_models.txt').write_text('\n\n'.join(model_details), encoding='utf-8')

# Examine support using every row; no matching or causal overlap assumption.
df['start_score_bin'] = pd.cut(df.y, bins=np.arange(0, 101, 10), include_lowest=True)
bins = df.groupby(['start_score_bin', 'x'], observed=False).agg(
    n=('z', 'size'), mean_gain=('z', 'mean'), mean_start_score=('y', 'mean'))
bins.to_csv(OUT / 'start_score_bins.csv')
treated = df[df.x == 1]
control = df[df.x == 0]
cut = float(treated.y.min())
overlap = {
    'lowest_observed_attendee_start_score': cut,
    'nonattendees_below_lowest_attendee': int((control.y < cut).sum()),
    'nonattendees_at_or_above_lowest_attendee': int((control.y >= cut).sum()),
    'attendees_below_lowest_attendee': int((treated.y < cut).sum()),
    'unique_start_scores': int(df.y.nunique()),
    'duplicate_complete_rows': int(df[['x', 'y', 'z']].duplicated().sum())
}

# Logical support bounds for the finite-sample ATT, assuming all potential
# end scores are on the stated 0--100 scale. These are NOT a confidence interval.
# ATT = mean(observed treated end score - unobserved untreated end score).
end_mean = float(treated.end_score.mean())
bounds = {'att_lower': end_mean - 100, 'att_upper': end_mean,
          'assumption': 'Counterfactual end scores are in [0,100].',
          'interpretation': 'Logical outcome-support bounds, not causal point estimates or confidence intervals.'}
examples = []
for tau in [-5., 0., 5.]:
    cf = treated.end_score - tau
    examples.append({'hypothetical_att': tau,
        'counterfactual_treated_no_tutoring_end_min': float(cf.min()),
        'counterfactual_treated_no_tutoring_end_max': float(cf.max()),
        'all_counterfactual_scores_in_0_100': bool(cf.between(0, 100).all()),
        'description': 'Illustrative missing potential-outcome completion; not an estimate.'})
pd.DataFrame(examples).to_csv(OUT / 'counterfactual_examples.csv', index=False)

audit = {
    'rows': len(df), 'columns_in_input': ['x', 'y', 'z'],
    'missing_cells': int(df[['x', 'y', 'z']].isna().sum().sum()),
    'all_observed_start_and_end_scores_in_0_100': True,
    'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [DATA, STUDY]},
    'environment': {'python': sys.version, 'platform': platform.platform(),
        'numpy': np.__version__, 'pandas': pd.__version__,
        'scipy': scipy.__version__, 'statsmodels': statsmodels.__version__},
    'unadjusted_gain_difference': float(treated.z.mean() - control.z.mean()),
    'group_summary': summary.reset_index().to_dict(orient='records'),
    'support_diagnostics': overlap, 'logical_att_bounds': bounds,
    'illustrative_counterfactuals': examples,
    'conclusion': 'The supplied assignment mechanism and observed variables do not identify the ATT.'
}
(OUT / 'analysis_summary.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
print(json.dumps(audit, indent=2))
print('\nAssociational coefficients of x (not causal estimates):')
print(pd.DataFrame(model_rows).query("term == 'x'").to_string(index=False))
print('\nStart-score bins:')
print(bins.to_string())
