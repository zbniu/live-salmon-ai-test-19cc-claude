import pandas as pd, numpy as np, statsmodels.formula.api as smf
rng=np.random.default_rng(1)
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
c=d[d.x==1].y.min()
o=d[d.y>=c].copy()   # common-support region (all treated are here)
print('cutoff',c,'overlap n',len(o),o.x.value_counts().to_dict())

def att_ols(df,form):
    m=smf.ols(form,df).fit()
    ctl=df[df.x==0]; tr=df[df.x==1]
    m0=smf.ols(form.replace('+x','').replace('x+',''),ctl).fit() if False else None
    return m
# 1. naive
print('naive all', smf.ols('z~x',d).fit().params['x'])
# 2. linear/quad/cubic adjustment, full sample & overlap sample
for name,df in [('full',d),('overlap',o)]:
    for f in ['z~x+y','z~x+y+I(y**2)','z~x+y+I(y**2)+I(y**3)','z~x*y']:
        m=smf.ols(f,df).fit(cov_type='HC3')
        print(name,f,'coef x',round(m.params['x'],3),'se',round(m.bse['x'],3))
# 3. imputation ATT: fit control outcome model on controls in overlap, predict for treated
def imp_att(df,deg):
    ctl=df[df.x==0]; tr=df[df.x==1]
    X=lambda y: np.vander(y-60,deg+1)
    b=np.linalg.lstsq(X(ctl.y.values),ctl.z.values,rcond=None)[0]
    return (tr.z.values-X(tr.y.values)@b).mean()
def boot(fn,df,B=2000):
    r=[]
    for _ in range(B):
        s=df.sample(len(df),replace=True,random_state=int(rng.integers(1e9)))
        r.append(fn(s))
    return np.percentile(r,[2.5,97.5]),np.std(r)
for deg in [1,2,3]:
    for name,df in [('overlap',o),('full controls',d)]:
        est=imp_att(df,deg); ci,se=boot(lambda s:imp_att(s,deg),df,1000)
        print(f'imputation ATT deg{deg} {name}: {est:.3f} se {se:.3f} CI {ci.round(3)}')
# 4. nearest neighbour matching on y (ATT), with replacement
def nn(df,k=1):
    ctl=df[df.x==0].sort_values('y'); tr=df[df.x==1]
    cy=ctl.y.values; cz=ctl.z.values
    idx=np.searchsorted(cy,tr.y.values)
    out=[]
    for yv,i in zip(tr.y.values,idx):
        cand=np.arange(max(0,i-k-1),min(len(cy),i+k+1))
        j=cand[np.argsort(np.abs(cy[cand]-yv))[:k]]
        out.append(cz[j].mean())
    return (tr.z.values-np.array(out)).mean()
for k in [1,5]:
    est=nn(o,k); ci,se=boot(lambda s:nn(s,k),o,1000)
    print(f'NN matching k={k}: {est:.3f} se {se:.3f} CI {ci.round(3)}')
# 5. IPW (ATT) with logistic propensity on y in overlap region
import statsmodels.api as sm
def ipw(df):
    X=sm.add_constant(np.column_stack([df.y-60,(df.y-60)**2]))
    p=sm.Logit(df.x.values,X).fit(disp=0).predict(X)
    w=p/(1-p)
    tr=df.x==1
    return df.z[tr].mean()-np.average(df.z[~tr],weights=w[~tr])
est=ipw(o); ci,se=boot(ipw,o,500)
print(f'IPW ATT overlap: {est:.3f} se {se:.3f} CI {ci.round(3)}')
# 6. Heterogeneity: effect by y within overlap
m=smf.ols('z~x*I(y-65)',o).fit(cov_type='HC3'); print(m.summary().tables[1])
# 7. check control outcome curvature: spline-ish check with y bins in controls
print(smf.ols('z~y+I(y**2)',d[d.x==0]).fit().summary().tables[1])
