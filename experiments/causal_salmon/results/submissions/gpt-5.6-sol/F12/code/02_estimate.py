"""ATT by control-outcome standardization, with baseline-model sensitivity.

All 2,000 supplied rows are used. No data generation mechanism for z is
assumed known. Intervals use HC3 regression covariance and a conditional,
independent-outcome working model; they are not exact randomization intervals.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import scipy
import statsmodels.api as sm
import patsy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import norm

root = Path(__file__).resolve().parents[2]
out = root/'submission'/'results'
d = pd.read_csv(root/'upload'/'data(20261004-013818).csv')
is_t = d.x.to_numpy() == 1
t, c = d[is_t], d[~is_t]
yt, yc = t.y.to_numpy(), c.y.to_numpy()
zt, zc = t.z.to_numpy(), c.z.to_numpy()
models = [('Linear', '1 + y'), ('Quadratic', '1 + y + I(y ** 2)'),
          ('Natural spline df=3', '1 + cr(y, df=3, constraints="center")'),
          ('Natural spline df=5 (primary)', '1 + cr(y, df=5, constraints="center")'),
          ('Natural spline df=7', '1 + cr(y, df=7, constraints="center")')]
rows = []
fits = {}
for label, formula in models:
    # Basis locations use baselines from the entire data, never outcomes.
    B = patsy.dmatrix(formula, d, return_type='dataframe')
    bt, bc = np.asarray(B)[is_t], np.asarray(B)[~is_t]
    fc = sm.OLS(zc, bc).fit(cov_type='HC3')
    ft = sm.OLS(zt, bt).fit(cov_type='HC3')
    L = bt.mean(axis=0)
    counterfactual = float(L @ fc.params)
    att = float(zt.mean()-counterfactual)
    se = float(np.sqrt(L @ (fc.cov_params()+ft.cov_params()) @ L))
    rows.append(dict(method=label, estimated_control_change_for_treated=counterfactual,
                     att=att, se_HC3=se, ci95_low=att-norm.ppf(.975)*se,
                     ci95_high=att+norm.ppf(.975)*se,
                     p_two_sided=float(2*norm.sf(abs(att/se))),
                     control_residual_sd=float(np.sqrt(fc.scale)),
                     design_columns=B.shape[1], design_rank=int(np.linalg.matrix_rank(bc))))
    fits[label] = (B, fc, ft)
    with (out/f'02_model_{len(rows)}.txt').open('w',encoding='utf-8') as f:
        f.write(f'{label}\nCONTROL OUTCOME MODEL\n{fc.summary()}\nTREATED OUTCOME MODEL\n{ft.summary()}\n')
res = pd.DataFrame(rows)
res.to_csv(out/'02_att_models.csv',index=False)

# Matching serves as a separate local comparison, with reuse of controls.
# No naive paired-test CI is computed: reuse makes such a CI inappropriate.
dist = np.abs(yt[:,None]-yc[None,:])
order = np.argsort(dist, axis=1)
matching = []
for k in [1,5,10,20]:
    idx = order[:,:k]
    m0 = zc[idx].mean(axis=1)
    matching.append(dict(k=k, att=float((zt-m0).mean()),
                         mean_absolute_baseline_distance=float(np.take_along_axis(dist,idx,axis=1).mean()),
                         maximum_absolute_baseline_distance=float(np.take_along_axis(dist,idx,axis=1).max()),
                         distinct_controls=int(np.unique(idx).size)))
pd.DataFrame(matching).to_csv(out/'02_matching_sensitivity.csv',index=False)

# Support counts in 1-point baseline bands, retaining the entire data.
support = d.assign(baseline_bin=np.floor(d.y).astype(int)).groupby(['baseline_bin','x']).agg(n=('z','size'),y_mean=('y','mean'),z_mean=('z','mean')).unstack('x')
support.to_csv(out/'02_one_point_support.csv')

# Save individual predictions for auditing the primary standardization.
B, fc, ft = fits['Natural spline df=5 (primary)']
audit = d.copy()
audit.insert(0,'input_row',np.arange(1,len(d)+1))
audit['predicted_change_without_Q'] = np.asarray(B) @ fc.params
audit['observed_minus_predicted_without_Q'] = d.z-audit.predicted_change_without_Q
audit.to_csv(out/'02_primary_predictions.csv',index=False)

# Check whether the linear control regression misses detectable curvature.
# HC3 Wald test jointly tests nonlinear columns in a nested cubic model.
scaled = (d.y.to_numpy()-60)/15
C = np.column_stack([np.ones(len(d)),scaled,scaled**2,scaled**3])
cubic = sm.OLS(zc,C[~is_t]).fit(cov_type='HC3')
R = np.array([[0,0,1,0],[0,0,0,1]])
w = cubic.wald_test(R, scalar=True)
checks = dict(scipy=scipy.__version__,statsmodels=sm.__version__,patsy=patsy.__version__,
              raw_difference=float(zt.mean()-zc.mean()),
              treated_mean_change=float(zt.mean()), untreated_mean_change=float(zc.mean()),
              cubic_control_nonlinearity_wald_stat=float(w.statistic),
              cubic_control_nonlinearity_p=float(w.pvalue),
              primary_prediction_average=float(audit.loc[is_t,'predicted_change_without_Q'].mean()),
              primary_standardization_check=float(audit.loc[is_t,'observed_minus_predicted_without_Q'].mean()),
              primary_model='Natural spline df=5 (primary)',
              inference_note='Approximate HC3 normal intervals under independent conditional outcome errors; not exact selection-design inference.')
(out/'02_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')

# Diagnostic figure: baseline overlap and separately fitted change curves.
grid = pd.DataFrame({'y':np.linspace(d.y.min(),d.y.max(),300)})
bg = np.asarray(patsy.build_design_matrices([B.design_info],grid)[0])
fig, ax = plt.subplots(2,1,figsize=(8,8),sharex=True,gridspec_kw={'height_ratios':[1,2]})
ax[0].hist([c.y,t.y],bins=np.arange(45,76,1),label=['Untreated','Q'],color=['#6b7280','#2563eb'])
ax[0].set_ylabel('Units');ax[0].legend()
ax[1].scatter(c.y,c.z,s=5,alpha=.18,color='#6b7280')
ax[1].scatter(t.y,t.z,s=5,alpha=.18,color='#2563eb')
ax[1].plot(grid.y,bg @ fc.params,color='#374151',lw=2,label='Untreated spline')
mask=grid.y>=t.y.min()
ax[1].plot(grid.y[mask],(bg @ ft.params)[mask],color='#2563eb',lw=2,label='Q spline')
ax[1].set_xlabel('Baseline y (points)');ax[1].set_ylabel('Change z (points)');ax[1].legend()
fig.tight_layout();fig.savefig(out/'02_baseline_and_change.png',dpi=160);plt.close(fig)
print(res.to_string(index=False))
print('\nMATCHING SENSITIVITY\n'+pd.DataFrame(matching).to_string(index=False))
print('\nCHECKS\n'+json.dumps(checks,indent=2))
