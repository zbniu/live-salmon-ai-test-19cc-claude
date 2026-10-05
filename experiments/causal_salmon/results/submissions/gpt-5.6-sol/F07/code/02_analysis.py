"""ATT estimation using all 2000 units; only the two supplied inputs are used.

Primary method: regress control z on cubic B-spline baseline terms, then
standardize predicted untreated changes to the 600 treated baselines.
Seven basis functions: degree 3, boundaries 45 and 75, knots 52.5,60,67.5.
This allows nonlinear untreated trends and does not assume constant effects.
Inference is approximate model/sampling inference, not randomization inference.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.interpolate import BSpline
from scipy.stats import norm

root = Path(__file__).resolve().parents[1]
d = pd.read_csv(root/'inputs/data.csv')
c = d[d.x==0].reset_index(drop=True)
t = d[d.x==1].reset_index(drop=True)
yc, yt = c.y.to_numpy(), t.y.to_numpy()
zc, zt = c.z.to_numpy(), t.z.to_numpy()
nc, nt = len(c), len(t)
assert len(d)==2000 and nc==1400 and nt==600
assert d.notna().all().all()

def basis(y, kind, complexity):
    if kind=='polynomial':
        v = (np.asarray(y)-60)/15
        return np.column_stack([v**k for k in range(complexity+1)])
    interior = np.linspace(45,75,complexity+2)[1:-1]
    knots = np.r_[np.repeat(45.,4),interior,np.repeat(75.,4)]
    return BSpline.design_matrix(y,knots,3,extrapolate=False).toarray()

def fit(B,z):
    beta = np.linalg.lstsq(B,z,rcond=None)[0]
    residual = z-B@beta
    bread = np.linalg.inv(B.T@B)
    leverage = np.sum((B@bread)*B,axis=1)
    adjusted = residual/(1-leverage)
    cov = bread @ (B.T@(adjusted[:,None]**2*B)) @ bread
    return beta,residual,cov

specs = [('linear','polynomial',1),('quadratic','polynomial',2),('cubic','polynomial',3),('spline_5_basis','spline',1),('spline_7_basis_primary','spline',3),('spline_9_basis','spline',5)]
rows=[]
rng = np.random.default_rng(20261004)
fold = np.empty(nc,dtype=int)
fold[rng.permutation(nc)] = np.arange(nc)%10
primary=None
for name,kind,complexity in specs:
    C,T = basis(yc,kind,complexity),basis(yt,kind,complexity)
    beta,resid,cov = fit(C,zc)
    m0 = T@beta
    contrast = zt-m0
    estimate = contrast.mean()
    average_basis = T.mean(axis=0)
    se = np.sqrt(contrast.var(ddof=1)/nt + average_basis@cov@average_basis)
    cv_prediction = np.empty(nc)
    for k in range(10):
        train = fold!=k; test = ~train
        b = np.linalg.lstsq(C[train],zc[train],rcond=None)[0]
        cv_prediction[test] = C[test]@b
    row = dict(method=name, estimate=float(estimate), approximate_se=float(se), ci95_low=float(estimate-1.96*se), ci95_high=float(estimate+1.96*se), control_cv_rmse=float(np.sqrt(np.mean((zc-cv_prediction)**2))), n_control=nc, n_treated=nt)
    rows.append(row)
    pd.DataFrame({'term':np.arange(len(beta)), 'coefficient':beta}).to_csv(root/f'results/{name}_coefficients.csv',index=False)
    if name=='spline_7_basis_primary':
        primary=(C,T,beta,m0,row)
        pd.DataFrame({'input_row_1_based':d.index[d.x==1].to_numpy()+1,'y':yt,'observed_z':zt,'estimated_z_without_Q':m0,'observed_minus_estimated_untreated':contrast}).to_csv(root/'results/treated_counterfactual_predictions.csv',index=False)

C,T,beta,m0,primary_row=primary

# Stratified nonparametric bootstrap: preserve group sizes; refit m0 each time.
# Resampling is an approximate independent-unit sampling device, not a replay
# of the undisclosed selection scores and candidate allocation.
B=2000
brng = np.random.default_rng(872091)
boot=np.empty(B)
for b in range(B):
    ic=brng.integers(nc,size=nc); it=brng.integers(nt,size=nt)
    coef=np.linalg.lstsq(C[ic],zc[ic],rcond=None)[0]
    boot[b]=np.mean(zt[it]-T[it]@coef)
pd.DataFrame({'replicate':np.arange(1,B+1),'att':boot}).to_csv(root/'results/bootstrap_estimates.csv',index=False)

# Smoothness sensitivity using local linear prediction from the k nearest
# controls at each recipient baseline. This preserves local baseline trends.
local_rows=[]
for k in [5,10,20,40]:
    pred=np.empty(nt); gap=np.empty(nt)
    for i,y in enumerate(yt):
        ix=np.argsort(np.abs(yc-y))[:k]
        X=np.column_stack([np.ones(k),yc[ix]-y])
        pred[i]=np.linalg.lstsq(X,zc[ix],rcond=None)[0][0]
        gap[i]=np.max(np.abs(yc[ix]-y))
    local_rows.append(dict(method=f'local_linear_{k}_nearest_controls',estimate=float(np.mean(zt-pred)), max_neighbor_distance=float(gap.max()), median_neighbor_distance=float(np.median(gap))))
pd.DataFrame(local_rows).to_csv(root/'results/local_matching_sensitivity.csv',index=False)

# Baseline-stratum contrasts, weighted by the number of treated in each stratum.
# Baseline adjustment is approximate because y remains continuous within bins.
strata_rows=[]
for width in [.5,1.,2.]:
    edges=np.arange(45,75+width/2,width)
    membership=np.digitize(d.y,edges)-1
    att=0.; var=0.; details=[]
    for i in np.unique(membership[d.x==1]):
        a=d[(membership==i)&(d.x==1)].z
        b=d[(membership==i)&(d.x==0)].z
        assert len(b)>1
        w=len(a)/nt
        att+=w*(a.mean()-b.mean())
        if len(a)>1:
            var+=w*w*(a.var(ddof=1)/len(a)+b.var(ddof=1)/len(b))
        details.append(dict(lower=float(edges[i]),upper=float(edges[i+1]),n_treated=len(a),n_control=len(b),treated_mean=float(a.mean()),control_mean=float(b.mean()),weight=w))
    pd.DataFrame(details).to_csv(root/f'results/stratum_details_width_{width:g}.csv',index=False)
    strata_rows.append(dict(method=f'baseline_strata_width_{width:g}',estimate=float(att), approximate_se=float(np.sqrt(var)), caveat='Continuous-baseline imbalance remains within strata; variance omits singleton-treated stratum contribution if any.'))
pd.DataFrame(strata_rows).to_csv(root/'results/stratification_sensitivity.csv',index=False)

pd.DataFrame(rows).to_csv(root/'results/outcome_model_sensitivity.csv',index=False)
result={
    'estimand':'Average treatment effect on the treated: mean(z(1)-z(0) | x=1)',
    'primary_method':'Control-outcome cubic B-spline standardization; 7 basis functions; boundaries 45,75; interior knots 52.5,60,67.5; all 2000 rows used.',
    'primary_att':primary_row['estimate'],
    'observed_mean_z_treated':float(zt.mean()),
    'estimated_mean_z_without_Q_for_treated':float(m0.mean()),
    'bootstrap_replicates':B,
    'bootstrap_seed':872091,
    'bootstrap_se':float(boot.std(ddof=1)),
    'bootstrap_percentile_ci95':np.quantile(boot,[.025,.975]).tolist(),
    'approximate_hc3_ci95':[primary_row['ci95_low'],primary_row['ci95_high']],
    'approximate_hc3_se':primary_row['approximate_se'],
    'raw_difference':float(zt.mean()-zc.mean()),
    'model_sensitivity_estimate_range':[min(r['estimate'] for r in rows),max(r['estimate'] for r in rows)],
    'local_matching_estimate_range':[min(r['estimate'] for r in local_rows),max(r['estimate'] for r in local_rows)],
    'stratification_estimate_range':[min(r['estimate'] for r in strata_rows),max(r['estimate'] for r in strata_rows)],
    'inference_limit':'Intervals assume usual independent-unit sampling and smooth control outcome regression; they are not exact intervals under the fixed-slot assignment mechanism.',
}
(root/'results/estimates.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
print('\nOutcome models\n'+pd.DataFrame(rows).to_string(index=False))
print('\nLocal matching\n'+pd.DataFrame(local_rows).to_string(index=False))
print('\nStratification\n'+pd.DataFrame(strata_rows).to_string(index=False))
