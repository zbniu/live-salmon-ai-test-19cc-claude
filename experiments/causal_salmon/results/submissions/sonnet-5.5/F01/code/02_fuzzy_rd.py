import pandas as pd, numpy as np, statsmodels.api as sm
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
c=d[d.x==1].y.min()
d['r']=d.y-c; d['above']=(d.r>=0).astype(int)
def fit(h,order=1,kernel='tri'):
    s=d[d.r.abs()<=h].copy()
    w=(1-s.r.abs()/h) if kernel=='tri' else pd.Series(1.0,index=s.index)
    cols=[]
    X=pd.DataFrame({'const':1.0,'above':s.above},index=s.index)
    for k in range(1,order+1):
        X[f'r{k}']=s.r**k; X[f'ra{k}']=s.r**k*s.above
    # reduced form, first stage
    rf=sm.WLS(s.z,X,weights=w).fit(cov_type='HC1')
    fs=sm.WLS(s.x,X,weights=w).fit(cov_type='HC1')
    # fuzzy: 2SLS with above as instrument for x (manual), controls same poly
    Z=X.copy(); 
    xhat=fs.fittedvalues
    X2=X.drop(columns='above').copy(); X2['x']=s.x
    Xh=X2.copy(); Xh['x']=xhat
    b=np.linalg.solve((Xh.T*w.values)@Xh.values,(Xh.T*w.values)@s.z.values)
    beta=pd.Series(b,index=Xh.columns)
    # robust 2SLS variance
    res=s.z.values-X2.values@beta.values
    A=np.linalg.inv((Xh.T*w.values)@Xh.values)
    M=(Xh.values*(w.values*res)[:,None]); meat=M.T@M
    V=A@meat@A
    se=np.sqrt(V[list(Xh.columns).index('x'),list(Xh.columns).index('x')])
    return dict(h=h,order=order,kernel=kernel,n=len(s),n_treated=int(s.x.sum()),jump_z=rf.params['above'],se_jump_z=rf.bse['above'],jump_x=fs.params['above'],se_jump_x=fs.bse['above'],effect=beta['x'],se=se)
rows=[]
for order in (1,2):
    for kernel in ('tri','unif'):
        for h in (3,4,5,6,8,10,12,15,20):
            rows.append(fit(h,order,kernel))
R=pd.DataFrame(rows); R['lo']=R.effect-1.96*R.se; R['hi']=R.effect+1.96*R.se
pd.set_option('display.width',250)
print('cutoff',c)
print(R.round(3).to_string()); R.to_csv('../results/fuzzy_rd_estimates.csv',index=False)
