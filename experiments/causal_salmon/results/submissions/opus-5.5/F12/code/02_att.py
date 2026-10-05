"""ATT of arrangement Q on change z.
Design: x=1 iff (candidate) AND (y >= c), c = min y among treated.
Candidate status depends on y and on study-generated noise unrelated to unit
characteristics -> given y, x is independent of potential outcomes.
For y < c nobody is treated; for y >= c treated and untreated coexist.
All treated have y >= c, so ATT is identified by comparing with controls at the same y."""
import pandas as pd, numpy as np
import statsmodels.formula.api as smf
from sklearn.linear_model import LogisticRegression
rng=np.random.default_rng(20261004)
df=pd.read_csv("/mnt/user-data/uploads/data.csv")
c=df.loc[df.x==1,'y'].min()
S=df[df.y>=c].copy()
print(f"cutoff c={c:.4f}; region y>=c: n={len(S)}, treated={S.x.sum()}, controls={(S.x==0).sum()}")

def est_reg(d, deg):
    """outcome-regression imputation: fit z~poly(y) on controls in region, impute for treated"""
    cc=d[d.x==0]; tt=d[d.x==1]
    X=lambda v: np.vander(v-65,deg+1)
    b=np.linalg.lstsq(X(cc.y.values),cc.z.values,rcond=None)[0]
    return (tt.z.values - X(tt.y.values)@b).mean()

def est_ipw(d, deg=2):
    """ATT odds weighting with logit propensity in poly(y)"""
    Z=np.vander(d.y.values-65,deg+1)[:,:-1]
    p=LogisticRegression(C=1e6,max_iter=5000).fit(Z,d.x).predict_proba(Z)[:,1]
    t=d.x.values==1; w=p/(1-p)
    return d.z.values[t].mean()-np.sum(w[~t]*d.z.values[~t])/np.sum(w[~t])

def est_match(d,k=5):
    cc=d[d.x==0].sort_values('y'); tt=d[d.x==1]
    cy=cc.y.values; cz=cc.z.values; out=[]
    for yv,zv in zip(tt.y.values,tt.z.values):
        idx=np.argsort(np.abs(cy-yv))[:k]; out.append(zv-cz[idx].mean())
    return np.mean(out)

def est_strata(d,nb=10):
    q=pd.qcut(d.y,nb,labels=False); d=d.assign(b=q)
    g=d.groupby(['b','x']).z.mean().unstack(); nt=d[d.x==1].groupby('b').size()
    return np.sum((g[1]-g[0])*nt)/nt.sum()

ests={'reg_linear':lambda d:est_reg(d,1),'reg_quadratic':lambda d:est_reg(d,2),
      'reg_cubic':lambda d:est_reg(d,3),'ipw_quadratic':est_ipw,
      'nn_match_k5':est_match,'strata_10':est_strata}
# Naive difference for reference
print(f"naive diff in means (all units): {df[df.x==1].z.mean()-df[df.x==0].z.mean():.3f}")
print(f"naive diff in means (y>=c):      {S[S.x==1].z.mean()-S[S.x==0].z.mean():.3f}")
# OLS with interaction, robust SE
m=smf.ols("z ~ x*I(y-c)",data=S.assign(c=c)).fit(cov_type='HC2')
print(m.summary().tables[1])
B=1000; rows=[]
for name,f in ests.items():
    pt=f(S)
    bs=[]
    for _ in range(B):
        bd=S.iloc[rng.integers(0,len(S),len(S))]
        bs.append(f(bd))
    bs=np.array(bs)
    rows.append(dict(method=name,ATT=pt,boot_se=bs.std(ddof=1),ci_lo=np.percentile(bs,2.5),ci_hi=np.percentile(bs,97.5)))
res=pd.DataFrame(rows); print(res.round(3).to_string(index=False))
res.to_csv("results/02_att_estimates.csv",index=False)
