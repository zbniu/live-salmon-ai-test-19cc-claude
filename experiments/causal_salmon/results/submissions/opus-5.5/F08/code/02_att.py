import pandas as pd, numpy as np
import statsmodels.formula.api as smf
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import SplineTransformer
rng=np.random.default_rng(20261004)
D=pd.read_csv('/mnt/user-data/uploads/data.csv')
cut=D.loc[D.x==1,'y'].min()
R=D[D.y>=cut].reset_index(drop=True)   # common-support region
print('cut',cut,'n region',len(R),'treated',R.x.sum(),'controls',(R.x==0).sum())

def ra(d,deg):  # regression adjustment: fit control outcome model in y (polynomial), impute for treated
    c=d[d.x==0]; t=d[d.x==1]
    f='z ~ '+' + '.join([f'I(y**{k})' for k in range(1,deg+1)])
    m=smf.ols(f,c).fit()
    return (t.z-m.predict(t)).mean()
def ra_spline(d):
    c=d[d.x==0]; t=d[d.x==1]
    st=SplineTransformer(n_knots=5,degree=3).fit(d[['y']])
    from sklearn.linear_model import LinearRegression
    m=LinearRegression().fit(st.transform(c[['y']]),c.z)
    return (t.z-m.predict(st.transform(t[['y']]))).mean()
def nn(d,k=5):
    c=d[d.x==0].sort_values('y'); t=d[d.x==1]
    cy=c.y.values; cz=c.z.values; out=[]
    for yi,zi in zip(t.y,t.z):
        idx=np.argsort(np.abs(cy-yi))[:k]; out.append(zi-cz[idx].mean())
    return np.mean(out)
def ipw(d):
    X=np.column_stack([d.y,d.y**2]); X=(X-X.mean(0))/X.std(0)
    p=LogisticRegression(C=1e6,max_iter=5000).fit(X,d.x).predict_proba(X)[:,1]
    w=p/(1-p); c=d.x==0
    return d.z[d.x==1].mean()-np.sum(w[c]*d.z[c])/np.sum(w[c])
def dr(d):
    c=d[d.x==0]; m=smf.ols('z~y+I(y**2)',c).fit(); mu=m.predict(d)
    X=np.column_stack([d.y,d.y**2]); X=(X-X.mean(0))/X.std(0)
    p=LogisticRegression(C=1e6,max_iter=5000).fit(X,d.x).predict_proba(X)[:,1]
    w=p/(1-p); r=d.z-mu; cc=d.x==0
    return r[d.x==1].mean()-np.sum(w[cc]*r[cc])/np.sum(w[cc])
def ols_linear(d):
    return smf.ols('z~x+y',d).fit().params['x']

est={'RA linear (main)':lambda d:ra(d,1),'RA quadratic':lambda d:ra(d,2),'RA cubic':lambda d:ra(d,3),
     'RA cubic spline':ra_spline,'NN match k=5':nn,'IPW (ATT odds)':ipw,'Doubly robust':dr,'OLS z~x+y':ols_linear}
rows=[]
for name,f in est.items():
    pt=f(R); bs=[]
    for b in range(500):
        s=pd.concat([g.sample(len(g),replace=True,random_state=int(rng.integers(1e9))) for _,g in R.groupby('x')]).reset_index(drop=True)
        bs.append(f(s))
    bs=np.array(bs); rows.append([name,pt,bs.std(),np.percentile(bs,2.5),np.percentile(bs,97.5)])
    print(rows[-1],flush=True)
out=pd.DataFrame(rows,columns=['estimator','ATT','boot_se','ci_lo','ci_hi'])
out.to_csv('results/02_att_estimates.csv',index=False); print(out.to_string())
# diagnostics
c=R[R.x==0]
for deg in (1,2,3):
    m=smf.ols('z ~ '+' + '.join([f'I(y**{k})' for k in range(1,deg+1)]),c).fit(); print('control fit deg',deg,'AIC',round(m.aic,1),'params',m.params.round(4).to_dict())
mi=smf.ols('z~x*y',R).fit(); print(mi.summary().tables[1])
R['bin']=pd.qcut(R.y,5)
g=R.groupby(['bin','x'],observed=True).agg(n=('z','size'),ym=('y','mean'),zm=('z','mean')).unstack(); print(g)
# full-sample control fit as robustness (uses controls below cut too)
Dc=D[D.x==0]; m=smf.ols('z~y+I(y**2)',Dc).fit(); t=D[D.x==1]; print('RA quad using all controls',(t.z-m.predict(t)).mean())
