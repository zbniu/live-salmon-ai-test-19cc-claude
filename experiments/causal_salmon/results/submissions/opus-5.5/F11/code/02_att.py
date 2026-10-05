"""ATT of tutoring on score gain z.
Identification: per STUDY_DESCRIPTION s.3, treatment depends only on y and on a study-generated
random number unrelated to student characteristics -> z(0) independent of x given y.
Treated all have y >= c (c = min treated y); for y >= c, x = 1 iff applicant, and
non-applicants exist at every y, so controls with y >= c provide overlap for the ATT."""
import pandas as pd, numpy as np, statsmodels.api as sm
from patsy import dmatrix
rng = np.random.default_rng(20261004)
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
c = df.loc[df.x==1,'y'].min()
R = df[df.y>=c].reset_index(drop=True)
print(f"cutoff c={c:.4f}; region n={len(R)}, treated={R.x.sum()}, controls={(R.x==0).sum()}")

def basis(y, kind, ref):
    if kind=='lin':  return np.column_stack([np.ones_like(y), y])
    if kind=='quad': return np.column_stack([np.ones_like(y), y, y**2])
    if kind=='cub':  return np.column_stack([np.ones_like(y), y, y**2, y**3])
    if kind=='spline':
        return np.asarray(dmatrix("bs(y, df=5, degree=3, lower_bound=lb, upper_bound=ub)",
                {"y":y,"lb":ref.min()-1e-6,"ub":ref.max()+1e-6}))
def reg_att(d, kind):
    t=d[d.x==1]; k=d[d.x==0]
    Xc=basis(k.y.values,kind,d.y.values); b=np.linalg.lstsq(Xc,k.z.values,rcond=None)[0]
    return (t.z.values - basis(t.y.values,kind,d.y.values)@b).mean()
def ps(d, kind='quad'):
    yy=(d.y.values-d.y.mean())/d.y.std()
    X=np.column_stack([np.ones_like(yy),yy,yy**2]) if kind=='quad' else np.column_stack([np.ones_like(yy),yy])
    m=sm.Logit(d.x.values,X).fit(disp=0); return m.predict(X)
def ipw_att(d):
    e=ps(d); w=e/(1-e); t=d.x.values==1
    return d.z.values[t].mean() - np.sum(w[~t]*d.z.values[~t])/np.sum(w[~t])
def aipw_att(d, kind='quad'):
    e=ps(d); t=d.x.values==1; k=d[~t]
    b=np.linalg.lstsq(basis(k.y.values,kind,d.y.values),k.z.values,rcond=None)[0]
    m0=basis(d.y.values,kind,d.y.values)@b; r=d.z.values-m0; w=e/(1-e)
    return r[t].mean() - np.sum(w[~t]*r[~t])/t.sum()
def nn_att(d, M=5):
    t=d[d.x==1]; k=d[d.x==0].sort_values('y'); ky=k.y.values; kz=k.z.values
    eff=[]
    for yv,zv in zip(t.y.values,t.z.values):
        idx=np.argsort(np.abs(ky-yv))[:M]; eff.append(zv-kz[idx].mean())
    return np.mean(eff)
def ols_region(d):
    X=sm.add_constant(np.column_stack([d.x.values,d.y.values])); return sm.OLS(d.z.values,X).fit(cov_type='HC1')

ests = {
 'REG_linear':lambda d:reg_att(d,'lin'),
 'REG_quadratic':lambda d:reg_att(d,'quad'),
 'REG_cubic':lambda d:reg_att(d,'cub'),
 'REG_cubic_spline_df5':lambda d:reg_att(d,'spline'),
 'IPW_ATT_logit_quad':ipw_att,
 'AIPW_ATT_quad':aipw_att,
 'NN_match_5':nn_att,
}
point={k:f(R) for k,f in ests.items()}
B=2000; boot={k:[] for k in ests}
for b in range(B):
    # stratified resample of treated and controls within region (cutoff treated as fixed)
    i=np.concatenate([rng.choice(np.where(R.x==1)[0],R.x.sum()), rng.choice(np.where(R.x==0)[0],(R.x==0).sum())])
    d=R.iloc[i].reset_index(drop=True)
    for k,f in ests.items(): boot[k].append(f(d))
rows=[]
for k in ests:
    s=np.array(boot[k]); rows.append([k,point[k],s.std(ddof=1),np.percentile(s,2.5),np.percentile(s,97.5)])
res=pd.DataFrame(rows,columns=['estimator','ATT','boot_SE','CI95_lo','CI95_hi'])
print(res.to_string(index=False, float_format=lambda v:f"{v:.3f}"))
res.to_csv("results/02_att_estimates.csv",index=False)
o=ols_region(R); print("\nOLS z ~ x + y in region (HC1):", o.params.round(3), o.bse.round(3))
# full-sample regressions for comparison (extrapolative for controls below c)
for kind in ['lin','quad','cub']:
    print(f"full-sample REG_{kind} (uses all 1400 controls):", round(reg_att(df,kind),3))
print("naive difference in means (full sample):", round(df[df.x==1].z.mean()-df[df.x==0].z.mean(),3))
# balance / overlap diagnostics
e=ps(R); w=e/(1-e)
print("\nps range treated:",e[R.x==1].min().round(3),e[R.x==1].max().round(3)," controls:",e[R.x==0].min().round(3),e[R.x==0].max().round(3))
yc=R.y[R.x==0].values; wc=w[R.x==0]
print("mean y treated:",R.y[R.x==1].mean().round(3)," controls unweighted:",yc.mean().round(3)," controls ATT-weighted:",(np.sum(wc*yc)/wc.sum()).round(3))
# effect by y tercile among treated (descriptive heterogeneity, spline model)
k=R[R.x==0]; Xb=basis(k.y.values,'spline',R.y.values); b=np.linalg.lstsq(Xb,k.z.values,rcond=None)[0]
t=R[R.x==1].copy(); t['eff']=t.z.values-basis(t.y.values,'spline',R.y.values)@b
t['tercile']=pd.qcut(t.y,3)
print("\nindividual-level (y-adjusted) effect by y tercile among treated:\n", t.groupby('tercile',observed=True).eff.agg(['size','mean','sem']).round(3))
