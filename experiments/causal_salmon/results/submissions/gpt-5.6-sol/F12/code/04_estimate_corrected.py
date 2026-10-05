"""ATT estimation using NumPy/SciPy; no external data or downloads.

Natural cubic splines use 4/6/8 knots at full-sample baseline quantiles.
The primary model uses 6 knots (6 parameters, including the constant).
Control-outcome standardization targets the observed 600 treated baselines.
HC3 intervals use an independent conditional-error working model, not an
exact randomization distribution for the undisclosed selection mechanism.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import scipy
from scipy.interpolate import CubicSpline
from scipy.stats import norm, chi2

root = Path(__file__).resolve().parents[2]
out = root/'submission'/'results'
d = pd.read_csv(root/'upload'/'data(20261004-013818).csv')
assert len(d)==2000 and d.x.sum()==600 and not d.isna().any().any()
is_t = d.x.to_numpy()==1
y = d.y.to_numpy(); z = d.z.to_numpy()
yt,yc,zt,zc=y[is_t],y[~is_t],z[is_t],z[~is_t]

def ols_hc3(a, response):
    # SVD inverse handles redundant spline columns in the treated-only range.
    pinv=np.linalg.pinv(a)
    beta=pinv @ response
    residual=response-a @ beta
    leverage=np.sum(a*pinv.T,axis=1)
    weighted=pinv*(residual/(1-leverage))[None,:]
    cov=weighted @ weighted.T
    return dict(beta=beta,cov=cov,residual=residual,leverage=leverage,
                rank=int(np.linalg.matrix_rank(a)),
                residual_sd=float(np.sqrt(residual @ residual/(len(response)-np.linalg.matrix_rank(a)))))

scaled=(y-60)/15
designs={'Linear':np.column_stack([np.ones(len(y)),scaled]),
         'Quadratic':np.column_stack([np.ones(len(y)),scaled,scaled**2])}
knots_log={}
splines={}
for k in [4,6,8]:
    knots=np.quantile(y,np.linspace(0,1,k))
    basis=CubicSpline(knots,np.eye(k),axis=0,bc_type='natural')
    name=f'Natural cubic spline {k} knots'+(' (primary)' if k==6 else '')
    designs[name]=basis(y)
    knots_log[name]=knots.tolist();splines[name]=basis

rows=[];fits={}
for name,B in designs.items():
    bt,bc=B[is_t],B[~is_t]
    fc,ft=ols_hc3(bc,zc),ols_hc3(bt,zt)
    L=bt.mean(axis=0)
    mu0=float(L @ fc['beta'])
    att=float(zt.mean()-mu0)
    se=float(np.sqrt(L @ (fc['cov']+ft['cov']) @ L))
    rows.append(dict(method=name,estimated_control_change_for_treated=mu0,att=att,se_HC3=se,
                     ci95_low=att-norm.ppf(.975)*se,ci95_high=att+norm.ppf(.975)*se,
                     p_two_sided=float(2*norm.sf(abs(att/se))),
                     control_residual_sd=fc['residual_sd'],design_columns=B.shape[1],
                     design_rank=int(np.linalg.matrix_rank(bc))))
    fits[name]=(fc,ft)
    record={group:{key:value.tolist() if isinstance(value,np.ndarray) else value for key,value in fit.items()}
            for group,fit in [('control',fc),('treated',ft)]}
    (out/f'04_model_{len(rows)}.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
res=pd.DataFrame(rows)
res.to_csv(out/'04_att_models.csv',index=False)

# Matching with replacement. No invalid paired-test interval is reported.
dist=np.abs(yt[:,None]-yc[None,:]);order=np.argsort(dist,axis=1)
matching=[]
for k in [1,5,10,20]:
    idx=order[:,:k];m0=zc[idx].mean(axis=1)
    matching.append(dict(k=k,att=float((zt-m0).mean()),
                         mean_absolute_baseline_distance=float(np.take_along_axis(dist,idx,axis=1).mean()),
                         maximum_absolute_baseline_distance=float(np.take_along_axis(dist,idx,axis=1).max()),
                         distinct_controls=int(np.unique(idx).size)))
pd.DataFrame(matching).to_csv(out/'04_matching_sensitivity.csv',index=False)
d.assign(baseline_bin=np.floor(d.y).astype(int)).groupby(['baseline_bin','x']).agg(
    n=('z','size'),y_mean=('y','mean'),z_mean=('z','mean')).unstack('x').to_csv(out/'04_one_point_support.csv')

name='Natural cubic spline 6 knots (primary)'
fc,ft=fits[name];B=designs[name]
audit=d.copy();audit.insert(0,'input_row',np.arange(1,len(d)+1))
audit['predicted_change_without_Q']=B @ fc['beta']
audit['observed_minus_predicted_without_Q']=d.z-audit.predicted_change_without_Q
audit.to_csv(out/'04_primary_predictions.csv',index=False)

# Nested cubic baseline model: robust joint test of curvature in controls.
C=np.column_stack([np.ones(len(y)),scaled,scaled**2,scaled**3])
cubic=ols_hc3(C[~is_t],zc)
b=cubic['beta'][2:];V=cubic['cov'][2:,2:]
w=float(b @ np.linalg.inv(V) @ b)
checks=dict(scipy=scipy.__version__,raw_difference=float(zt.mean()-zc.mean()),
            treated_mean_change=float(zt.mean()),untreated_mean_change=float(zc.mean()),
            control_curvature_wald_stat=w,control_curvature_p=float(chi2.sf(w,2)),
            primary_prediction_average=float(audit.loc[is_t,'predicted_change_without_Q'].mean()),
            primary_standardization_check=float(audit.loc[is_t,'observed_minus_predicted_without_Q'].mean()),
            primary_treated_fitted_mean_check=float((B[is_t] @ ft['beta']).mean()-zt.mean()),
            primary_model=name,knots=knots_log,
            inference_note='Approximate HC3 normal intervals assuming independent conditional outcome errors; not exact selection-design inference.')
assert abs(checks['primary_treated_fitted_mean_check']) < 1e-10
assert abs(checks['primary_standardization_check']-res.loc[res.method==name,'att'].iloc[0]) < 1e-10
(out/'04_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')

# Export plotting data without depending on optional plotting packages.
grid=np.linspace(y.min(),y.max(),301);bg=splines[name](grid)
pd.DataFrame(dict(y=grid,predicted_untreated=bg @ fc['beta'],predicted_Q=bg @ ft['beta'],
                  Q_within_observed_range=grid>=yt.min())).to_csv(out/'04_fitted_curves.csv',index=False)
print(res.to_string(index=False))
print('\nMATCHING SENSITIVITY\n'+pd.DataFrame(matching).to_string(index=False))
print('\nCHECKS\n'+json.dumps(checks,indent=2))
