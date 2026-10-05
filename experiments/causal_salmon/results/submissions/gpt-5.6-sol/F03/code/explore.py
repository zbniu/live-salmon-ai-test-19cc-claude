"""Full-data validation and initial design-based and outcome-model analyses."""
from pathlib import Path
import hashlib, json, platform
import numpy as np
import pandas as pd
import scipy
from scipy import stats
from scipy.interpolate import BSpline

def fit_hc3(z, b):
    beta=np.linalg.lstsq(b,z,rcond=None)[0]
    bread=np.linalg.pinv(b.T@b)
    residual=z-b@beta
    leverage=np.einsum('ij,jk,ik->i',b,bread,b)
    meat=b.T@((residual/(1-leverage))[:,None]**2*b)
    cov=bread@meat@bread
    rss=residual@residual
    return beta,cov,1-rss/np.sum((z-z.mean())**2),np.sqrt(rss/(len(z)-b.shape[1]))

root = Path(__file__).resolve().parents[1]
source = root.parents[0] / 'upload' / 'data(4).csv'
d = pd.read_csv(source)
assert list(d.columns) == ['x','y','z']
assert d.shape == (2000,3) and not d.isna().any().any()
assert np.isfinite(d.to_numpy()).all()
assert set(d.x) == {0,1} and d.x.sum() == 600
assert d.y.between(0,100).all()
groups = d.groupby('x').agg(['count','mean','std','min','max'])
groups.to_csv(root/'results'/'group_summaries.csv')
print(groups.to_string())
print('End score range:', (d.y+d.z).min(), (d.y+d.z).max())
g1=d[d.x==1]; g0=d[d.x==0]
diff = g1.z.mean()-g0.z.mean()
v1=g1.z.var()/len(g1); v0=g0.z.var()/len(g0)
se=np.sqrt(v1+v0)
df=(v1+v0)**2/(v1**2/(len(g1)-1)+v0**2/(len(g0)-1))
crit=stats.t.ppf(.975,df)
result={'n':len(d),'n_treated':len(g1),'n_control':len(g0),
 'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'unadjusted':{'estimate':diff,'se':se,'df':df,'ci95':[diff-crit*se,diff+crit*se],
 'p_two_sided':float(2*stats.t.sf(abs(diff/se),df))},
 'versions':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
 'scipy':scipy.__version__}}
print('Unadjusted:',json.dumps(result['unadjusted']))
rows=[]
for df_spline in [1,3,5,8]:
    if df_spline==1:
        B=np.c_[np.ones(len(d)),(d.y-d.y.mean())/d.y.std()]
    else:
        interior=np.quantile(d.y,np.linspace(0,1,df_spline-2)[1:-1])
        knots=np.r_[np.repeat(d.y.min(),4),interior,np.repeat(d.y.max(),4)]
        B=BSpline.design_matrix(d.y.to_numpy(),knots,3).toarray()
    # Separate treatment/control regressions; standardize both to treated baseline scores.
    b1=B[d.x==1]; b0=B[d.x==0]
    m1=fit_hc3(g1.z.to_numpy(),b1)
    m0=fit_hc3(g0.z.to_numpy(),b0)
    a=b1.mean(axis=0)
    effect=float(a@(m1[0]-m0[0]))
    model_se=float(np.sqrt(a@(m1[1]+m0[1])@a))
    rows.append({'basis_df':df_spline,'ATT_estimate':effect,'conditional_model_se':model_se,
      'treated_R2':m1[2],'control_R2':m0[2],
      'treated_residual_sd':m1[3],'control_residual_sd':m0[3]})
print(pd.DataFrame(rows).to_string(index=False))
pd.DataFrame(rows).to_csv(root/'results'/'exploratory_adjustments.csv',index=False)
d.assign(baseline_bin=pd.cut(d.y,bins=np.arange(0,101,10),include_lowest=True)).groupby(
 ['baseline_bin','x'],observed=True).agg(n=('z','size'),mean_gain=('z','mean'),
 sd_gain=('z','std'),mean_baseline=('y','mean')).to_csv(root/'results'/'baseline_bins.csv')
(root/'results'/'initial_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('Generated group_summaries.csv, exploratory_adjustments.csv, baseline_bins.csv, initial_results.json')
