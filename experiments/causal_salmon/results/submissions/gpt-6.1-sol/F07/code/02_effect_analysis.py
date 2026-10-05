"""Estimate ATT by untreated-outcome regression standardized to all recipients.
Primary model is specified here before looking at adjusted effect estimates:
cubic B-spline, five equally spaced interior baseline knots, all 1400 controls.
Sensitivity fits vary smoothness; matching uses every treated unit, with reuse.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.interpolate import BSpline
from scipy.spatial.distance import cdist
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[2]
out = root/'submission/results'
d = pd.read_csv(root/'upload/data(20261004-180745).csv')
t, c = d[d.x==1].copy(), d[d.x==0].copy()
yc, yt, zc, zt = c.y.to_numpy(), t.y.to_numpy(), c.z.to_numpy(), t.z.to_numpy()
lo, hi = float(d.y.min()), float(d.y.max())

def basis(y, interior):
    knots = np.r_[np.repeat(lo,4), interior, np.repeat(hi,4)]
    return BSpline.design_matrix(y, knots, 3).toarray()

def standardized(Bc, Bt):
    beta = np.linalg.lstsq(Bc, zc, rcond=None)[0]
    pred = Bt@beta
    adjusted = zt-pred
    att = float(adjusted.mean())
    # Sandwich SE for the empirical-treated-distribution ATT functional:
    # treated adjusted-outcome variability plus HC3 control regression variance.
    inv = np.linalg.pinv(Bc.T@Bc)
    h = np.einsum('ij,jk,ik->i', Bc, inv, Bc)
    resid = zc-Bc@beta
    omega = (resid/(1-h))**2
    cov = inv@(Bc.T@(omega[:,None]*Bc))@inv
    v = Bt.mean(axis=0)
    se = float(np.sqrt(adjusted.var(ddof=1)/len(t)+v@cov@v))
    return att, se, beta, pred, resid

interior = np.linspace(lo,hi,7)[1:-1]
Bc, Bt = basis(yc,interior), basis(yt,interior)
att, se, beta, pred, resid = standardized(Bc,Bt)
summary = {
    'estimand': 'average effect on the treated (ATT), in change-score points',
    'primary_model': 'untreated-outcome cubic B-spline with five equally spaced interior knots; standardized to all 600 recipients',
    'interior_knots': interior.tolist(), 'n_treated':len(t), 'n_controls':len(c),
    'observed_treated_mean':float(zt.mean()), 'estimated_untreated_mean_for_treated':float(pred.mean()),
    'att':att, 'sandwich_se':se, 'approximate_normal_95_ci':[att-1.96*se,att+1.96*se],
    'raw_difference':float(zt.mean()-zc.mean()),
    'control_residual_sd':float(np.sqrt(np.sum(resid**2)/(len(c)-Bc.shape[1]))),
}
records=[]
for model in ['linear','quadratic','cubic','spline_3_knots','spline_5_knots','spline_7_knots','spline_9_knots']:
    if model in ['linear','quadratic','cubic']:
        degree = {'linear':1,'quadratic':2,'cubic':3}[model]
        C = np.column_stack([((yc-60)/15)**i for i in range(degree+1)])
        T = np.column_stack([((yt-60)/15)**i for i in range(degree+1)])
    else:
        k = int(model.split('_')[1])
        interior_k = np.linspace(lo,hi,k+2)[1:-1]
        C, T = basis(yc,interior_k), basis(yt,interior_k)
    a, s, *_ = standardized(C,T)
    records.append({'method':model,'att':a,'sandwich_se':s,'ci_lower':a-1.96*s,'ci_upper':a+1.96*s})
pd.DataFrame(records).to_csv(out/'02_model_sensitivity.csv',index=False)

# Bootstrap recipients and nonrecipients separately, preserving group sizes.
# This is an approximate resampling analysis, not the unknown assignment design.
rng = np.random.default_rng(20261004)
boot = np.empty(2000)
for b in range(len(boot)):
    ic = rng.integers(0,len(c),len(c)); it = rng.integers(0,len(t),len(t))
    bb = np.linalg.lstsq(Bc[ic],zc[ic],rcond=None)[0]
    boot[b] = (zt[it]-Bt[it]@bb).mean()
summary['bootstrap'] = {'replicates':len(boot),'seed':20261004,
                        'standard_error':float(boot.std(ddof=1)),
                        'percentile_95_ci':np.quantile(boot,[.025,.975]).tolist()}
pd.DataFrame({'replicate':np.arange(1,len(boot)+1),'att':boot}).to_csv(out/'02_bootstrap_draws.csv',index=False)

dist = np.abs(yt[:,None]-yc[None,:])
order = np.argsort(dist,axis=1)
match_records=[]
for k in [1,5,10,20]:
    ids=order[:,:k]
    match_records.append({'controls_per_recipient':k,
         'att':float((zt-zc[ids].mean(axis=1)).mean()),
         'mean_baseline_difference':float((yt-yc[ids].mean(axis=1)).mean()),
         'max_matched_baseline_distance':float(np.take_along_axis(dist,ids,axis=1).max())})
pd.DataFrame(match_records).to_csv(out/'02_matching_sensitivity.csv',index=False)

pd.DataFrame({'input_row_1_based':t.index+1,'y':yt,'observed_z':zt,
 'estimated_z_without_Q':pred,'observed_minus_estimated_without_Q':zt-pred}).to_csv(out/'02_recipient_predictions.csv',index=False)
summary['baseline_overlap']={'treated_min':float(yt.min()),'treated_max':float(yt.max()),
 'control_min':float(yc.min()),'control_max':float(yc.max()),
 'recipients_outside_control_range':int(((yt<yc.min())|(yt>yc.max())).sum())}
(out/'02_effect_summary.json').write_text(json.dumps(summary,indent=2)+'\n')

grid=np.linspace(lo,hi,300)
fig, axes=plt.subplots(1,2,figsize=(11,4.4))
axes[0].scatter(yc,zc,s=7,alpha=.22,label='No Q')
axes[0].scatter(yt,zt,s=7,alpha=.3,label='Q')
axes[0].plot(grid,basis(grid,interior)@beta,color='black',lw=2,label='Estimated mean without Q')
axes[0].set(xlabel='Baseline y (points)',ylabel='Change z (points)')
axes[0].legend(fontsize=8)
axes[1].hist(yc,bins=np.arange(45,77,2),alpha=.6,label='No Q')
axes[1].hist(yt,bins=np.arange(45,77,2),alpha=.6,label='Q')
axes[1].set(xlabel='Baseline y (points)',ylabel='Number of units')
axes[1].legend()
fig.tight_layout(); fig.savefig(out/'02_diagnostics.png',dpi=170); plt.close(fig)
print(json.dumps(summary,indent=2))
print('\nMODEL SENSITIVITY\n'+pd.DataFrame(records).to_string(index=False))
print('\nMATCHING SENSITIVITY\n'+pd.DataFrame(match_records).to_string(index=False))
