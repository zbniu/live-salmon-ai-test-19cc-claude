import pandas as pd, numpy as np, statsmodels.api as sm
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
c=d.loc[d.x==1,'y'].min()
d['u']=d.y-c; d['Z']=(d.u>=0).astype(int)
rng=np.random.default_rng(1)

def fuzzy(df,h,kernel='tri',deg=1):
    s=df[df.u.abs()<=h].copy()
    w=(1-s.u.abs()/h) if kernel=='tri' else np.ones(len(s))
    cols=lambda: [s['u']**k for k in range(1,deg+1)]+[s['Z']*s['u']**k for k in range(1,deg+1)]
    X=pd.concat([pd.Series(1.0,index=s.index,name='c')]+cols(),axis=1); X.columns=[str(i) for i in range(X.shape[1])]
    # 2SLS manually
    Zm=X.copy(); Zm['zz']=s['Z']; 
    Xd=X.copy(); Xd['x']=s['x']
    W=np.sqrt(w.values)[:,None]
    first=sm.WLS(s['x'],Zm,weights=w).fit()
    red=sm.WLS(s['z'],Zm,weights=w).fit()
    xhat=first.fittedvalues
    Xs=X.copy(); Xs['xhat']=xhat
    sec=sm.WLS(s['z'],Xs,weights=w).fit()
    beta=sec.params['xhat']
    # proper SE via residuals with actual x
    Xa=X.copy(); Xa['x']=s['x']
    res=s['z']-Xa.values@np.append(sec.params.values[:-1],beta)
    Zf=Zm.values; Xv=Xa.values
    A=Zf.T@(w.values[:,None]*Xv)
    Bm=(Zf*(w.values*res.values)[:,None]).T@(Zf*(w.values*res.values)[:,None])
    Ai=np.linalg.inv(A)
    V=Ai@Bm@Ai.T
    se=np.sqrt(V[-1,-1])
    return dict(h=h,deg=deg,n=len(s),first=first.params['zz'],itt=red.params['zz'],late=beta,se=se)

rows=[]
for h in [4,6,8,10,12,15,20,30]:
    rows.append(fuzzy(d,h,'tri',1))
for h in [10,15,20,30]:
    rows.append(fuzzy(d,h,'tri',2))
r=pd.DataFrame(rows); r['lo']=r.late-1.96*r.se; r['hi']=r.late+1.96*r.se
print(r.round(3).to_string())
r.to_csv('../results/fuzzy_rd.csv',index=False)

# Naive comparisons
print('\nNaive diff in means:',d[d.x==1].z.mean()-d[d.x==0].z.mean())
m=sm.OLS(d.z,sm.add_constant(d[['x','y']])).fit(cov_type='HC1');print('OLS z~x+y:',m.params['x'],m.bse['x'])
s=d[d.y>=c]; m=sm.OLS(s.z,sm.add_constant(s[['x','y']])).fit(cov_type='HC1');print('OLS above cutoff only z~x+y:',m.params['x'],m.bse['x'])

# Density check
below=((d.u<0)&(d.u>=-3)).sum(); above=((d.u>=0)&(d.u<3)).sum(); print('\ncount within 3 below/above cutoff:',below,above)
for h in [2,5,10]:
    print(h,((d.u<0)&(d.u>=-h)).sum(),((d.u>=0)&(d.u<h)).sum())
