"""Estimate average treatment effect for attendees using only attached inputs.

Primary estimator: control-only restricted cubic spline outcome regression,
standardized to the 600 observed attendees. Five score-quantile knots are
chosen from y only, not from outcomes. Stratified pairs bootstrap provides
approximate sampling uncertainty, not exact design/randomization inference.
Sensitivity analyses do not replace the designated primary estimator.
"""
from pathlib import Path
import hashlib, json, platform, shutil
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[2]
out=root/'submission/results'
inputs=root/'submission/inputs';inputs.mkdir(exist_ok=True)
for name in ['data(20261004-180818).csv','STUDY_DESCRIPTION(20261004-180818).md']:
 source=root/'upload'/name
 if source.exists(): shutil.copyfile(source,inputs/name)
df=pd.read_csv(inputs/'data(20261004-180818).csv')
assert df.shape==(2000,3) and list(df.columns)==['x','y','z']
assert not df.isna().any().any() and np.isfinite(df.to_numpy()).all()
assert set(df.x.unique())=={0,1} and int(df.x.sum())==600
y=df.y.to_numpy(); z=df.z.to_numpy(); t=df.x.to_numpy()==1
yc=y[~t];yt=y[t];zc=z[~t];zt=z[t]
u=(y-60)/10

def rcs_basis(u, knots):
    """Restricted cubic spline with intercept; linear in both tails."""
    cols=[np.ones_like(u),u]
    last, penultimate=knots[-1],knots[-2]
    for knot in knots[:-2]:
        h=(np.maximum(u-knot,0)**3
           -np.maximum(u-penultimate,0)**3*(last-knot)/(last-penultimate)
           +np.maximum(u-last,0)**3*(penultimate-knot)/(last-penultimate))
        cols.append(h/(last-knots[0])**2)
    return np.column_stack(cols)

def fit(B, values):
    return np.linalg.lstsq(B, values, rcond=None)[0]

def hc3(B,values,beta):
    bread=np.linalg.inv(B.T@B)
    leverage=np.sum((B@bread)*B,axis=1)
    residual=values-B@beta
    scaled=residual/(1-leverage)
    return bread@(B.T@(scaled[:,None]**2*B))@bread

knots=np.quantile(u,[.05,.275,.5,.725,.95])
B=rcs_basis(u,knots);Bc=B[~t];Bt=B[t]
beta=fit(Bc,zc)
counterfactual=Bt@beta
individual_contrasts=zt-counterfactual
att=float(np.mean(individual_contrasts))
cfmean=float(np.mean(counterfactual))

# 3,000 actual stratified pairs bootstrap draws, preserving 600/1,400 counts.
# Fixed score-based spline knots; each draw refits the control regression.
rng=np.random.default_rng(20261004)
bootstrap=[]
for b in range(3000):
    ci=rng.integers(0,len(zc),len(zc))
    ti=rng.integers(0,len(zt),len(zt))
    bb=fit(Bc[ci],zc[ci])
    bootstrap.append(np.mean(zt[ti]-Bt[ti]@bb))
bootstrap=np.asarray(bootstrap)
pd.DataFrame({'replicate':np.arange(1,3001),'ATT_points':bootstrap}).to_csv(out/'bootstrap_draws.csv',index=False)
lower,upper=np.quantile(bootstrap,[.025,.975])
se=float(np.std(bootstrap,ddof=1))

# Prespecified alternatives: functional form, score strata, and nearby controls.
sensitivity=[]
designs={'linear':np.column_stack([np.ones(len(y)),u]),
         'quadratic':np.column_stack([np.ones(len(y)),u,u**2]),
         'cubic_polynomial':np.column_stack([np.ones(len(y)),u,u**2,u**3])}
for k in [4,5,7]:
    quantiles=np.linspace(.05,.95,k)
    if k==5: quantiles=np.array([.05,.275,.5,.725,.95])
    designs[f'restricted_cubic_spline_{k}_knots']=rcs_basis(u,np.quantile(u,quantiles))
for name,design in designs.items():
    bc=design[~t];bt=design[t];bb=fit(bc,zc)
    est=float(np.mean(zt-bt@bb))
    sensitivity.append({'method':name,'att_points':est,'n_treated':len(zt),'parameters':design.shape[1]})

for width in [.5,1,2]:
    label=np.floor((y-yt.min())/width).astype(int)
    contrast=[];supported=0
    for b in np.unique(label[t]):
        tt=(label==b)&t;cc=(label==b)&~t
        if cc.sum():
            contrast.extend((z[tt]-np.mean(z[cc])).tolist());supported+=int(tt.sum())
    sensitivity.append({'method':f'score_strata_width_{width:g}',
       'att_points':float(np.mean(contrast)), 'n_treated':supported,'parameters':None})
dist=np.abs(yt[:,None]-yc[None,:]);order=np.argsort(dist,axis=1)
for k in [1,5,10,20]:
    nn=order[:,:k]
    est=float(np.mean(zt-np.mean(zc[nn],axis=1)))
    sensitivity.append({'method':f'{k}_nearest_controls_with_replacement',
      'att_points':est,'n_treated':len(zt),'parameters':None})
pd.DataFrame(sensitivity).to_csv(out/'sensitivity_estimates.csv',index=False)

# Check smoothness via fixed-fold prediction among controls; no model selection.
foldrng=np.random.default_rng(426)
folds=np.empty(len(zc),int);folds[foldrng.permutation(len(zc))]=np.arange(len(zc))%10
cv=[]
for name,design in designs.items():
    bc=design[~t];pred=np.empty(len(zc))
    for f in range(10):
        train=folds!=f;test=~train
        pred[test]=bc[test]@fit(bc[train],zc[train])
    cv.append({'method':name,'control_CV_RMSE':float(np.sqrt(np.mean((zc-pred)**2)))})
pd.DataFrame(cv).to_csv(out/'control_model_cross_validation.csv',index=False)

# Robust outcome-model tests: nonlinear control terms and effect heterogeneity.
cov=hc3(Bc,zc,beta)
wald=float(beta[2:]@np.linalg.solve(cov[2:,2:],beta[2:]))
nonlinear_p=float(stats.chi2.sf(wald,len(beta)-2))
interaction_design=np.column_stack([B, t.astype(float),t*u])
ib=fit(interaction_design,z);icov=hc3(interaction_design,z,ib)
interaction_p=float(2*stats.norm.sf(abs(ib[-1]/np.sqrt(icov[-1,-1]))))

result={'estimand':'Average effect of attending on score gain among the 600 attendees (ATT)',
 'primary_method':'Control-only restricted cubic spline (5 knots), standardized to attendees',
 'att_points':att,'approximate_95_percent_bootstrap_CI':[float(lower),float(upper)],
 'bootstrap_standard_error':se,'bootstrap_replicates':3000,'bootstrap_seed':20261004,
 'mean_observed_attendee_gain':float(np.mean(zt)),
 'estimated_mean_attendee_gain_without_tutoring':cfmean,
 'mean_control_gain':float(np.mean(zc)),
 'unadjusted_difference_points':float(np.mean(zt)-np.mean(zc)),
 'mean_starting_score_difference':float(np.mean(yt)-np.mean(yc)),
 'spline_knots_original_score':(knots*10+60).tolist(),
 'control_nonlinearity_HC3_Wald_p':nonlinear_p,
 'treatment_linear_interaction_HC3_p':interaction_p,
 'control_model_rmse':float(np.sqrt(np.mean((zc-Bc@beta)**2))),
 'no_attendees_outside_observed_control_score_range':bool((yt.min()>=yc.min()) and (yt.max()<=yc.max())),
 'end_of_term_score_range':[float((y+z).min()),float((y+z).max())],
 'CI_limitation':'Approximate model/sampling interval; assignment probabilities and the capacity-constrained lottery are not reconstructed. Not an exact finite-population randomization interval.',
 'python':platform.python_version(), 'numpy':np.__version__, 'pandas':pd.__version__}
(out/'primary_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
pd.DataFrame({'source_row':np.flatnonzero(t)+1,'starting_score':yt,'observed_gain':zt,
  'estimated_gain_without_tutoring':counterfactual,'observed_minus_estimated_no_tutoring':individual_contrasts}).to_csv(out/'attendee_standardization.csv',index=False)
pd.DataFrame({'term':np.arange(len(beta)),'coefficient':beta}).to_csv(out/'primary_control_model_coefficients.csv',index=False)
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs.iterdir()}
(out/'input_sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(result,indent=2));print('\nSensitivity estimates:')
print(pd.DataFrame(sensitivity).to_string(index=False))
print('\nControl outcome regression cross-validation:')
print(pd.DataFrame(cv).to_string(index=False))

grid=np.linspace(y.min(),y.max(),250);gb=rcs_basis((grid-60)/10,knots)
tb=fit(Bt,zt)
fig,ax=plt.subplots(figsize=(8,5))
for flag,color,name in [(False,'#4063A3','Nonattendees'),(True,'#C35C2E','Attendees')]:
    ax.scatter(y[t==flag],z[t==flag],s=7,alpha=.15,color=color,label=name)
ax.plot(grid,gb@beta,color='#1F477F',lw=2,label='Fitted gain without tutoring')
high=grid>=yt.min()
ax.plot(grid[high],gb[high]@tb,color='#B4481F',lw=2,label='Fitted attendee gain')
ax.set(xlabel='Starting score y',ylabel='Score gain z (points)',
 title=f'Average effect for attendees: {att:.2f} points (approx. 95% CI {lower:.2f}–{upper:.2f})')
ax.legend(fontsize=8);fig.tight_layout();fig.savefig(out/'adjusted_outcome_curves.png',dpi=180)
