"""Randomization-based estimation for the realized recipients; baseline sensitivity.

Let tau_T be the average individual effect in the randomly chosen treated set.
D - tau_T = mean_T(z(0)) - mean_C(z(0)). Under complete randomization,
Var(D-tau_T) = (1/n_T + 1/n_C)*S_0^2. Control sample variance unbiasedly
estimates the finite-population untreated potential-change variance S_0^2.
The interval below is a large-sample normal approximation, not an exact interval.
The conventional Welch comparison interval is also retained, separately labeled.
"""
import json
import pathlib
import numpy as np
import pandas as pd
from scipy import stats
from scipy.interpolate import BSpline

df = pd.read_csv('upload/data(6).csv')
assert len(df)==2000 and df.notna().all().all() and df.x.sum()==600
t = df[df.x==1]
c = df[df.x==0]
nt,nc = len(t),len(c)
d = t.z.mean()-c.z.mean()
se_satt = np.sqrt(c.z.var(ddof=1)*(1/nt+1/nc))
crit = stats.norm.ppf(.975)
v1,v0 = t.z.var(ddof=1)/nt,c.z.var(ddof=1)/nc
se_welch = np.sqrt(v1+v0)
welch_df = (v1+v0)**2/(v1*v1/(nt-1)+v0*v0/(nc-1))
welch_test = stats.ttest_ind(t.z,c.z,equal_var=False)
baseline_test = stats.ttest_ind(t.y,c.y,equal_var=False)

result = {
    'estimand':'mean[z_i(1)-z_i(0)] over the 600 actual recipients (sample ATT)',
    'n_total':len(df), 'n_treated':nt, 'n_control':nc,
    'mean_z_treated':t.z.mean(), 'mean_z_control':c.z.mean(),
    'primary_difference_points':d,
    'recipient_target_randomization_se':se_satt,
    'recipient_target_approx_95_interval':[d-crit*se_satt,d+crit*se_satt],
    'conventional_welch_se':se_welch, 'conventional_welch_df':welch_df,
    'conventional_welch_95_interval':[d-stats.t.ppf(.975,welch_df)*se_welch,d+stats.t.ppf(.975,welch_df)*se_welch],
    'conventional_welch_two_sided_p':welch_test.pvalue,
    'mean_baseline_treated':t.y.mean(), 'mean_baseline_control':c.y.mean(),
    'baseline_difference':t.y.mean()-c.y.mean(), 'baseline_welch_p':baseline_test.pvalue,
    'counterfactual_bounds_from_0_100_followup':[
        t.z.mean()-(100-t.y).mean(), t.z.mean()-(-t.y).mean()],
    'notes':[
        'Randomization interval is approximate repeated-assignment coverage for D minus the varying recipient-specific target.',
        'No individual counterfactual is observed; a positive average does not establish benefit for every recipient.',
        'Welch interval and p value are conventional group-comparison inference, distinct from the primary recipient-target interval.',
        'Baseline adjustment is secondary and model-assisted; its standard errors are not used for the primary result.'
    ]
}

# Predict untreated change at each recipient baseline using controls only.
# Treated observed mean minus predicted untreated mean targets the recipients.
q = (df.y.to_numpy()-60)/15
mask = df.x.to_numpy()==0
fits = []
predictions = pd.DataFrame({'y':df.y,'x':df.x,'z':df.z})
for degree in [1,2,3]:
    B = np.column_stack([q**i for i in range(degree+1)])
    coef = np.linalg.lstsq(B[mask],df.z.to_numpy()[mask],rcond=None)[0]
    pred = B@coef
    residual = df.z.to_numpy()[mask]-pred[mask]
    fits.append({'model':f'control_polynomial_degree_{degree}', 'adjusted_recipient_effect':float(t.z.mean()-pred[~mask].mean()),
                 'control_residual_sd':float(np.sqrt(residual@residual/(nc-B.shape[1]))),
                 'control_r_squared':float(1-(residual@residual)/np.sum((c.z-c.z.mean())**2))})
    predictions[f'untreated_prediction_degree_{degree}'] = pred
    if degree==1:
        result['control_linear_slope_z_per_baseline_point']=coef[1]/15
        result['secondary_linear_adjusted_recipient_effect']=fits[-1]['adjusted_recipient_effect']

knots = np.r_[np.repeat(q.min(),4),np.quantile(q,[.25,.5,.75]),np.repeat(q.max(),4)]
B = BSpline.design_matrix(q,knots,3).toarray()
coef = np.linalg.lstsq(B[mask],df.z.to_numpy()[mask],rcond=None)[0]
pred=B@coef
residual=df.z.to_numpy()[mask]-pred[mask]
fits.append({'model':'control_cubic_bspline_3_internal_knots','adjusted_recipient_effect':float(t.z.mean()-pred[~mask].mean()),
             'control_residual_sd':float(np.sqrt(residual@residual/(nc-B.shape[1]))),
             'control_r_squared':float(1-(residual@residual)/np.sum((c.z-c.z.mean())**2))})
predictions['untreated_prediction_spline']=pred
pd.DataFrame(fits).to_csv('submission/results/03_baseline_sensitivity.csv',index=False)
predictions.to_csv('submission/results/03_unit_predictions.csv',index=False)

# Descriptive subgroup comparisons: exploratory, not individually identified effects.
edges=np.linspace(45,75,7)
band=df.assign(baseline_band=pd.cut(df.y,edges,include_lowest=True)).groupby(['baseline_band','x'],observed=True).agg(
    n=('z','size'),baseline_mean=('y','mean'),change_mean=('z','mean'),change_sd=('z','std'))
band.to_csv('submission/results/03_baseline_subgroups.csv')

pathlib.Path('submission/results/03_primary_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
print(pd.DataFrame(fits).to_string(index=False))
print(band.to_string())
