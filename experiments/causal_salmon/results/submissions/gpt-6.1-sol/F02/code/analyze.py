"""Analyze only the two supplied attachments; no network or external data."""
from pathlib import Path
import sys, json, hashlib, shutil, platform
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'
OUT.mkdir(parents=True, exist_ok=True)
INPUT = ROOT / 'inputs'
INPUT.mkdir(exist_ok=True)
sources = {
    'data.csv': ROOT.parent / 'upload' / 'data(20261004-180704).csv',
    'STUDY_DESCRIPTION.md': ROOT.parent / 'upload' / 'STUDY_DESCRIPTION(20261004-180705).md',
}
manifest = {}
for name, source in sources.items():
    if source.exists():
        shutil.copyfile(source, INPUT / name)
    path = INPUT / name
    manifest[name] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                      'bytes': path.stat().st_size}
(OUT / 'input_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
df = pd.read_csv(INPUT / 'data.csv')
assert list(df.columns) == ['x', 'y', 'z']
assert len(df) == 2000 and not df.isna().any().any()
assert np.isfinite(df.to_numpy()).all()
assert set(df.x) == {0, 1} and int(df.x.sum()) == 600
assert df.y.between(0, 100).all()
df['followup'] = df.y + df.z
validation = {
    'rows': len(df), 'missing_values': int(df.isna().sum().sum()),
    'received_Q': int(df.x.sum()), 'did_not_receive_Q': int((df.x == 0).sum()),
    'baseline_min': float(df.y.min()), 'baseline_max': float(df.y.max()),
    'followup_min': float(df.followup.min()), 'followup_max': float(df.followup.max()),
    'followup_within_0_100': bool(df.followup.between(0,100).all()),
    'rows_excluded': 0, 'python': platform.python_version(),
    'numpy': np.__version__, 'pandas': pd.__version__,
}
(OUT / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n')
groups = df.groupby('x').agg(n=('z','size'), y_mean=('y','mean'),
    y_sd=('y','std'), y_min=('y','min'), y_max=('y','max'),
    z_mean=('z','mean'), z_sd=('z','std'), z_min=('z','min'), z_max=('z','max'),
    followup_mean=('followup','mean'))
groups.to_csv(OUT / 'group_summary.csv', float_format='%.12g')
df['baseline_bin'] = pd.cut(df.y, bins=np.arange(0,101,10), include_lowest=True)
bins = df.groupby(['baseline_bin','x'], observed=False).agg(
    n=('z','size'), y_mean=('y','mean'), z_mean=('z','mean'))
bins.to_csv(OUT / 'baseline_bins.csv', float_format='%.12g')
t = df[df.x == 1]
c = df[df.x == 0]
# Descriptive OLS only: observed change versus receipt and centered baseline.
# HC3 standard error describes fitted-model uncertainty, not confounding.
X = np.column_stack([np.ones(len(df)), df.x, df.y - df.y.mean()])
beta = np.linalg.lstsq(X, df.z, rcond=None)[0]
residual = df.z.to_numpy() - X @ beta
inv = np.linalg.inv(X.T @ X)
h = np.einsum('ij,jk,ik->i', X, inv, X)
v = inv @ (X.T @ (X * ((residual/(1-h))**2)[:,None])) @ inv
models = {'formula': 'z ~ 1 + x + (y - mean(y))',
    'n':len(df), 'intercept':float(beta[0]), 'x_coefficient':float(beta[1]),
    'y_coefficient':float(beta[2]), 'x_HC3_se':float(np.sqrt(v[1,1])),
    'interpretation':'Descriptive conditional association, not an identified causal effect.'}
(OUT / 'descriptive_ols.json').write_text(json.dumps(models, indent=2)+'\n')
overlap = {'treated_min_y':float(t.y.min()), 'treated_max_y':float(t.y.max()),
    'control_min_y':float(c.y.min()), 'control_max_y':float(c.y.max()),
    'control_count_below_treated_min_y':int((c.y<t.y.min()).sum()),
    'control_count_in_treated_y_range':int(c.y.between(t.y.min(),t.y.max()).sum())}
# For recipients, ATT = mean(F1 - F0). If F0 is on 0--100,
# its sharp bounds without additional restrictions are mean(F1)-100 and mean(F1).
# Counterfactual completions are hypothetical, not newly observed data.
f1 = t.followup.to_numpy()
witness = []
for label, f0 in [('no_effect',f1), ('maximum_increase',np.zeros(len(t))),
                  ('maximum_decrease',np.full(len(t),100.0))]:
    witness.append({'completion':label, 'mean_counterfactual_followup':float(f0.mean()),
        'mean_effect_for_recipients':float((f1-f0).mean()),
        'counterfactual_within_0_100':bool(((f0>=0)&(f0<=100)).all())})
pd.DataFrame(witness).to_csv(OUT/'hypothetical_counterfactual_completions.csv',index=False,
                           float_format='%.12g')
summary = {'raw_mean_change_difference':float(t.z.mean()-c.z.mean()),
    'raw_mean_baseline_difference':float(t.y.mean()-c.y.mean()),
    'treated_mean_followup':float(f1.mean()),
    'ATT_logical_lower_bound_0_100':float(f1.mean()-100),
    'ATT_logical_upper_bound_0_100':float(f1.mean()),
    'bounds_are_confidence_interval':False,
    'positive_causal_effect_identified':False, 'overlap':overlap,
    'baseline_adjusted_descriptive_x_coefficient':float(beta[1])}
(OUT/'analysis_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Analysis used every one of the 2000 supplied rows; no rows dropped.')
print(groups.to_string())
print(json.dumps(summary,indent=2))
print(json.dumps(models,indent=2))
print('Outputs: input_manifest.json, validation.json, group_summary.csv, baseline_bins.csv,')
print('descriptive_ols.json, hypothetical_counterfactual_completions.csv, analysis_summary.json.')
