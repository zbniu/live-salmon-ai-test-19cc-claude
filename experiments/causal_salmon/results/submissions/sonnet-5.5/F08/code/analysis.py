import pandas as pd, numpy as np, statsmodels.formula.api as smf
from sklearn.linear_model import LogisticRegression
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
c=d[d.x==1].y.min()
s=d[d.y>=c].copy()   # region with overlap: everyone below c has x=0 by design
print('n region',len(s), s.x.value_counts().to_dict())
ym=s[s.x==1].y.mean(); s['yc']=s.y-ym
rng=np.random.default_rng(1)

def ests(s):
    out={}
    m=smf.ols('z~x+yc',s).fit(); out['ols_lin']=m.params['x']
    m=smf.ols('z~x+yc+I(yc**2)',s).fit(); out['ols_quad']=m.params['x']
    m=smf.ols('z~x*yc',s).fit(); out['ols_interact_ATT']=m.params['x']   # yc centred at treated mean
    m=smf.ols('z~x*(yc+I(yc**2))',s).fit()
    t=s[s.x==1]; t0=t.copy(); t0['x']=0
    out['ols_quad_interact_ATT']=(t.z-m.predict(t0)).mean()
    # IPW ATT with logistic ps in y (quadratic)
    X=np.c_[s.yc,s.yc**2]; ps=LogisticRegression(C=1e6,max_iter=1000).fit(X,s.x).predict_proba(X)[:,1]
    w=ps/(1-ps); a=s.x==1
    out['ipw_att']=s.z[a].mean()-np.average(s.z[~a],weights=w[~a])
    # 1-NN matching on y (with replacement) for treated
    yt=s.y[a].values; zt=s.z[a].values; yc_=s.y[~a].values; zc=s.z[~a].values
    idx=np.abs(yt[:,None]-yc_[None,:]).argmin(1)
    out['nn_match_att']=(zt-zc[idx]).mean()
    return out
pt=ests(s); print(pd.Series(pt).round(3))
B=[]
for b in range(1000):
    B.append(ests(s.sample(len(s),replace=True,random_state=int(rng.integers(1e9)))))
B=pd.DataFrame(B)
res=pd.DataFrame({'est':pd.Series(pt),'se':B.std(),'lo':B.quantile(.025),'hi':B.quantile(.975)}).round(3)
print(res)
res.to_csv('../results/estimates.csv')
m=smf.ols('z~x+yc',s).fit(cov_type='HC3'); print(m.summary().tables[1])
# linearity / specification checks
m2=smf.ols('z~x*yc',s).fit(cov_type='HC3'); print('interaction x:yc',m2.params['x:yc'],m2.pvalues['x:yc'])
# controls-only curvature over full range
c0=d[d.x==0]; print(smf.ols('z~y+I(y**2)',c0).fit().summary().tables[1])
# narrower windows
for hi in [70,65,62.5]:
    w=s[s.y<=hi]; mm=smf.ols('z~x+yc',w).fit(cov_type='HC3'); print('window y<=',hi,len(w),mm.params['x'].round(3),mm.bse['x'].round(3))
# balance on y in matched sense
print(s.groupby('x').y.describe())
