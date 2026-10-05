import pandas as pd, numpy as np, statsmodels.api as sm
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
c=d[d.x==1].y.min()
d['t']=(d.y>=c).astype(int); d['r']=d.y-c

def fuzzy(h,kernel='tri',order=1,df=d):
    s=df[abs(df.r)<=h].copy()
    w=((1-abs(s.r)/h) if kernel=='tri' else pd.Series(1.0,index=s.index)).values
    R=np.column_stack([s.r.values**k for k in range(1,order+1)])
    Rt=R*s.t.values[:,None]
    Xc=np.column_stack([np.ones(len(s)),R,Rt])
    Zi=np.column_stack([np.ones(len(s)),s.t.values,R,Rt])   # instruments incl. exogenous
    Xe=np.column_stack([s.x.values,Xc])                       # regressors (x endogenous first)
    fs=sm.WLS(s.x.values,Zi,weights=w).fit(cov_type='HC1')
    rf=sm.WLS(s.z.values,Zi,weights=w).fit(cov_type='HC1')
    sw=np.sqrt(w); Xw=Xe*sw[:,None]; Zw=Zi*sw[:,None]; zw=s.z.values*sw
    P=Zw@np.linalg.solve(Zw.T@Zw,Zw.T)
    A=np.linalg.inv(Xw.T@P@Xw)
    b=A@(Xw.T@P@zw)
    u=zw-Xw@b; Xh=P@Xw
    V=A@(Xh.T*(u**2)@Xh)@A*len(s)/(len(s)-Xe.shape[1])
    se=np.sqrt(V[0,0])
    return dict(h=h,order=order,kernel=kernel,n=len(s),first_stage=fs.params[1],fs_se=fs.bse[1],
                reduced_form=rf.params[1],rf_se=rf.bse[1],tau=b[0],se=se,lo=b[0]-1.96*se,hi=b[0]+1.96*se)
rows=[fuzzy(h,k,o) for o in (1,2) for h in (3,4,5,6,8,10,12,15,18) for k in ('tri','unif')]
res=pd.DataFrame(rows)
pd.set_option('display.width',200)
print("cutoff",c)
print(res.round(3).to_string())
res.to_csv('results/02b_fuzzy_rd_grid.csv',index=False)
