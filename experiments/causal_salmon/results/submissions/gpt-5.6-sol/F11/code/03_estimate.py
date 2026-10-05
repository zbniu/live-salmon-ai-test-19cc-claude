"""ATT by untreated outcome standardization, with flexible sensitivity checks.

All 2000 rows are read. No external data. Main model: restricted cubic spline
with 6 knots (5 nonconstant degrees of freedom), fitted only to controls.
Counterfactual predictions are averaged over the 600 actual attendees.
Bootstrap independently resamples rows within attendance group and holds
the original knot locations fixed; this is approximate model-based inference,
not an exact reconstruction of the quota-based assignment randomization.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import norm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[1]
d=pd.read_csv(root/'inputs/data.csv')
t=d[d.x==1]; c=d[d.x==0]
yt=t.y.to_numpy(); yc=c.y.to_numpy(); zt=t.z.to_numpy(); zc=c.z.to_numpy()
nt,nc=len(t),len(c)
assert (nt,nc)==(600,1400) and d.notna().all().all()

def rcs(y,knots):
    u=(np.asarray(y)-60)/10; k=(np.asarray(knots)-60)/10
    pos=lambda a: np.maximum(a,0)**3
    out=[np.ones_like(u),u]
    for kj in k[:-2]:
        b=pos(u-kj)-pos(u-k[-2])*(k[-1]-kj)/(k[-1]-k[-2])+pos(u-k[-1])*(k[-2]-kj)/(k[-1]-k[-2])
        out.append(b/(k[-1]-k[0])**2)
    return np.column_stack(out)

rows=[]
def outcome_model(Bc,Bt,name):
    beta=np.linalg.lstsq(Bc,zc,rcond=None)[0]
    m0=Bt@beta
    att=zt.mean()-m0.mean()
    rows.append({'method':name,'att':float(att),'untreated_counterfactual_mean':float(m0.mean())})
    return att,beta,m0

for deg in [1,2,3]:
    Bc=np.column_stack([((yc-60)/10)**j for j in range(deg+1)])
    Bt=np.column_stack([((yt-60)/10)**j for j in range(deg+1)])
    outcome_model(Bc,Bt,f'Control polynomial degree {deg}, standardized to attendees')

fits={}
for K in [4,5,6,7,8,10]:
    knots=np.quantile(yc,np.linspace(.05,.95,K))
    Bc=rcs(yc,knots); Bt=rcs(yt,knots)
    att,beta,m0=outcome_model(Bc,Bt,f'Control restricted cubic spline, {K-1} nonconstant df')
    fits[K]=(knots,Bc,Bt,beta,m0,att)

knots,Bc,Bt,beta,m0,att=fits[6]
rng=np.random.default_rng(20261004)
R=2000; boot=np.empty(R)
for r in range(R):
    ci=rng.integers(0,nc,nc); ti=rng.integers(0,nt,nt)
    beta_b=np.linalg.lstsq(Bc[ci],zc[ci],rcond=None)[0]
    boot[r]=zt[ti].mean()-Bt[ti].mean(axis=0)@beta_b
np.savetxt(root/'results/bootstrap_att.csv',boot,delimiter=',',header='att',comments='')
se=boot.std(ddof=1); ci=np.quantile(boot,[.025,.975])

# Independent flexible checks. Local linear regression accommodates trends
# within neighborhoods; all controls enter with Gaussian kernel weights.
for h in [.75,1.5,3.0]:
    delta=yc[None,:]-yt[:,None]
    w=np.exp(-.5*(delta/h)**2)
    s0=w.sum(axis=1); s1=(w*delta).sum(axis=1); s2=(w*delta**2).sum(axis=1)
    q0=w@zc; q1=(w*delta)@zc
    pred=(s2*q0-s1*q1)/(s0*s2-s1*s1)
    rows.append({'method':f'Control local linear, Gaussian bandwidth {h} points','att':float(zt.mean()-pred.mean()),'untreated_counterfactual_mean':float(pred.mean())})

stratum_records=[]
for width in [1,2,4]:
    labels=np.floor((d.y.to_numpy()-45)/width).astype(int)
    total=0.; var=0.; used=0
    for s in np.unique(labels):
        a=d[(labels==s)&(d.x==1)]; b=d[(labels==s)&(d.x==0)]
        if not len(a): continue
        assert len(b)>1 and len(a)>1
        wt=len(a)/nt; diff=a.z.mean()-b.z.mean()
        total+=wt*diff; var+=wt**2*(a.z.var(ddof=1)/len(a)+b.z.var(ddof=1)/len(b)); used+=len(a)
        stratum_records.append({'width':width,'y_lower':45+s*width,'n_treated':len(a),'n_control':len(b),'y_difference':a.y.mean()-b.y.mean(),'gain_difference':diff,'treated_weight':wt})
    assert used==nt
    rows.append({'method':f'Starting-score strata of width {width} points','att':float(total),'untreated_counterfactual_mean':float(zt.mean()-total)})
    print(f'Strata width={width}: ATT={total:.9f}, approximate SE={np.sqrt(var):.9f}')
pd.DataFrame(stratum_records).to_csv(root/'results/stratum_details.csv',index=False)

distance,idx=cKDTree(yc[:,None]).query(yt[:,None],k=1)
rows.append({'method':'One nearest starting-score control per attendee, with replacement','att':float(np.mean(zt-zc[idx])),'untreated_counterfactual_mean':float(np.mean(zc[idx]))})
print('Nearest-control distance: median',np.median(distance),'maximum',max(distance))
pd.DataFrame({'y':yt,'observed_gain':zt,'estimated_untreated_gain':m0}).to_csv(root/'results/attendee_counterfactual_predictions.csv',index=False)
pd.DataFrame(rows).to_csv(root/'results/sensitivity_estimates.csv',index=False)

# Descriptive unadjusted comparison and baseline overlap statistics.
raw=zt.mean()-zc.mean(); rawse=np.sqrt(zt.var(ddof=1)/nt+zc.var(ddof=1)/nc)
summary={
    'n':len(d),'n_attended':nt,'n_did_not_attend':nc,
    'mean_gain_attended':float(zt.mean()),'mean_gain_did_not_attend':float(zc.mean()),
    'unadjusted_gain_difference':float(raw),'unadjusted_se':float(rawse),
    'main_method':'Control restricted cubic spline, 5 nonconstant df; ATT standardization',
    'spline_knots_starting_score':knots.tolist(),'att':float(att),
    'estimated_attendee_gain_without_tutoring':float(m0.mean()),
    'bootstrap_se':float(se),'bootstrap_percentile_95_ci':ci.tolist(),
    'bootstrap_replicates':R,'bootstrap_seed':20261004,
    'treated_outside_control_y_range':int(((yt<min(yc))|(yt>max(yc))).sum()),
    'controls_at_or_above_minimum_attendee_score':int((yc>=min(yt)).sum()),
    'nearest_control_max_distance':float(max(distance)),
    'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'inputs').iterdir()},
    'inference_note':'Within-group row bootstrap; fixed spline knots. Approximate inference assuming a smooth untreated outcome curve, not exact quota randomization inference.'
}
(root/'results/main_estimate.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print('MAIN RESULT\n'+json.dumps(summary,indent=2))
print('SENSITIVITY\n'+pd.DataFrame(rows).to_string(index=False))

grid=np.linspace(d.y.min(),d.y.max(),300)
fig,axs=plt.subplots(1,2,figsize=(11,4))
axs[0].scatter(yc,zc,s=5,alpha=.15,color='#3977a3',label='Nonattendees')
axs[0].scatter(yt,zt,s=5,alpha=.15,color='#d47a28',label='Attendees')
axs[0].plot(grid,rcs(grid,knots)@beta,color='#153e65',lw=2,label='Estimated gain without tutoring')
axs[0].set(xlabel='Starting score',ylabel='Score gain (points)'); axs[0].legend(fontsize=8)
axs[1].hist(boot,bins=35,color='#3977a3',alpha=.8)
axs[1].axvline(0,color='black',lw=1); axs[1].axvline(att,color='#d47a28',lw=2)
axs[1].set(xlabel='Estimated average effect on attendees (points)',ylabel='Bootstrap count')
fig.tight_layout();fig.savefig(root/'results/adjusted_analysis.png',dpi=180)
print('Outputs: main_estimate.json, sensitivity_estimates.csv, bootstrap_att.csv, stratum_details.csv, attendee_counterfactual_predictions.csv, adjusted_analysis.png')
