import pandas as pd, numpy as np, statsmodels.formula.api as smf, statsmodels.api as sm
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
c = df[df.x==1].y.min()
print("treated y cutoff (min y among treated):", c)
print("controls below cutoff:", (df[df.x==0].y<c).sum(), " controls at/above:", (df[df.x==0].y>=c).sum())
sub = df[df.y>=c].copy()
print("common-support sample:", len(sub), sub.x.value_counts().to_dict())
print("\nNaive full-sample diff:", df[df.x==1].z.mean()-df[df.x==0].z.mean())
print("Naive support-restricted diff:", sub[sub.x==1].z.mean()-sub[sub.x==0].z.mean())

# Full sample adjustment (extrapolates below cutoff for controls, but ATT only needs E[z0|y] at y>=c)
m_lin = smf.ols("z ~ x + y", df).fit(cov_type="HC3"); print("\nFull, linear y:", m_lin.params['x'], m_lin.bse['x'])
m_q = smf.ols("z ~ x + y + I(y**2)", df).fit(cov_type="HC3"); print("Full, quad y:", m_q.params['x'], m_q.bse['x'])

# Restricted-support models
for name,f in [("lin","z ~ x + y"),("quad","z ~ x + y + I(y**2)"),("cubic","z ~ x + y + I(y**2)+I(y**3)"),
               ("lin x interaction","z ~ x*y")]:
    m = smf.ols(f, sub).fit(cov_type="HC3")
    print(f"Restricted {name}: x coef {m.params['x']:.3f} se {m.bse['x']:.3f}")
# Check linearity in control group (restricted)
mc = smf.ols("z ~ y + I(y**2)", sub[sub.x==0]).fit(); print("control quad term p:", mc.pvalues['I(y ** 2)'], " slope-linear:", smf.ols("z~y",sub[sub.x==0]).fit().params['y'])
mt = smf.ols("z ~ y + I(y**2)", sub[sub.x==1]).fit(); print("treated quad term p:", mt.pvalues['I(y ** 2)'])
mi = smf.ols("z ~ x*y", sub).fit(cov_type="HC3"); print("interaction x:y p:", mi.pvalues['x:y'], mi.params['x:y'])

# ATT via control regression imputation (linear & quad) on controls in support
def att_imp(d, deg):
    ctl = d[d.x==0]; tr = d[d.x==1]
    X = lambda v: np.column_stack([v**k for k in range(deg+1)])
    b = np.linalg.lstsq(X(ctl.y.values), ctl.z.values, rcond=None)[0]
    return (tr.z.values - X(tr.y.values)@b).mean()
# Stratification on y (exact ATT weights): bins by treated-y quantiles
def att_strat(d, k=10):
    tr = d[d.x==1]; edges = np.quantile(tr.y, np.linspace(0,1,k+1)); edges[0]-=1e-9; edges[-1]+=1e-9
    d = d.assign(b=pd.cut(d.y, edges, labels=False, include_lowest=True)).dropna(subset=['b'])
    out=0; n=0
    for b,g in d.groupby('b'):
        if (g.x==1).sum()>0 and (g.x==0).sum()>0:
            out += (g.x==1).sum()*(g[g.x==1].z.mean()-g[g.x==0].z.mean()); n+=(g.x==1).sum()
    return out/n
# Nearest-neighbour matching (k=5) on y, with replacement
def att_match(d,k=5):
    tr=d[d.x==1]; ctl=d[d.x==0]; cy=ctl.y.values; cz=ctl.z.values; res=[]
    for y,z in zip(tr.y.values,tr.z.values):
        idx=np.argsort(np.abs(cy-y))[:k]; res.append(z-cz[idx].mean())
    return np.mean(res)
rng=np.random.default_rng(20240)
est = {"imputation_linear":lambda d:att_imp(d,1),"imputation_quad":lambda d:att_imp(d,2),
       "imputation_cubic":lambda d:att_imp(d,3),"stratification_10":att_strat,"match_k5":att_match}
print()
res={}
for n,f in est.items():
    pt=f(sub)
    bs=[]
    for _ in range(1000):
        s=sub.sample(len(sub),replace=True,random_state=int(rng.integers(1e9)))
        bs.append(f(s))
    lo,hi=np.percentile(bs,[2.5,97.5]); res[n]=(pt,np.std(bs),lo,hi)
    print(f"{n}: ATT={pt:.3f} se={np.std(bs):.3f} 95%CI=({lo:.3f},{hi:.3f})")
# Logit-based IPW check on support
ps = smf.logit("x ~ y", sub).fit(disp=0)
p = ps.predict(sub); w = np.where(sub.x==1,1,p/(1-p))
att_ipw = sub[sub.x==1].z.mean() - np.average(sub[sub.x==0].z, weights=w[sub.x==0])
print("\nIPW (logit on y, support sample) ATT:", att_ipw)
print("propensity logit y coef:", ps.params.to_dict())
# residual diagnostic: covariate balance after stratification & residual vs y
mm = smf.ols("z ~ x + y", sub).fit(); print("\nRestricted lin resid corr w/ y:", np.corrcoef(mm.resid, sub.y)[0,1])
# pooling linear: bin-wise differences
sub["bin"]=pd.qcut(sub.y,6)
print(sub.groupby(["bin","x"],observed=True).z.agg(["size","mean"]).unstack().to_string())
pd.DataFrame(res,index=["ATT","se","lo","hi"]).T.to_csv("results/02_att_estimates.csv")
