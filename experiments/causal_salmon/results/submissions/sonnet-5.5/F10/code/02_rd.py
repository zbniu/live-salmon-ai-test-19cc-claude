import pandas as pd, numpy as np, statsmodels.api as sm
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
c=d[d.x==1].y.min()
print("cutoff (lowest treated y) =",c, " max untreated below:",d[(d.x==0)&(d.y<c)].y.max())
d['t']=(d.y>=c).astype(int); d['r']=d.y-c
print("Untreated above cutoff:",((d.t==1)&(d.x==0)).sum(),"treated above:",((d.t==1)&(d.x==1)).sum())

def fuzzy(h,kernel='tri',order=1,df=d):
    s=df[abs(df.r)<=h].copy()
    w=(1-abs(s.r)/h) if kernel=='tri' else np.ones(len(s))
    R=np.column_stack([s.r**k for k in range(1,order+1)])
    Rt=R*s.t.values[:,None]
    X=np.column_stack([np.ones(len(s)),s.t,R,Rt])
    # first stage and reduced form
    fs=sm.WLS(s.x,X,weights=w).fit(cov_type='HC1')
    rf=sm.WLS(s.z,X,weights=w).fit(cov_type='HC1')
    # 2SLS manually: instrument t, endog x, controls
    Xc=np.column_stack([np.ones(len(s)),R,Rt])
    xhat=fs.fittedvalues
    Z2=np.column_stack([xhat,Xc])
    sec=sm.WLS(s.z,Z2,weights=w).fit()
    beta=sec.params[0]
    # proper SE via IV sandwich
    Xe=np.column_stack([s.x,Xc]); Zi=X
    Wm=np.diag(w) if False else None
    sw=np.sqrt(w.values if hasattr(w,'values') else w)
    Xe_w=Xe*sw[:,None]; Zi_w=Zi*sw[:,None]; zw=s.z.values*sw
    P=Zi_w@np.linalg.solve(Zi_w.T@Zi_w,Zi_w.T)
    b=np.linalg.solve(Xe_w.T@P@Xe_w,Xe_w.T@P@zw)
    u=zw-Xe_w@b
    A=np.linalg.inv(Xe_w.T@P@Xe_w)
    Xh=P@Xe_w
    V=A@(Xh.T@np.diag(u**2)@Xh)@A*len(s)/(len(s)-Xe.shape[1])
    se=np.sqrt(V[0,0])
    return dict(h=h,order=order,kernel=kernel,n=len(s),first_stage=fs.params[1],fs_se=fs.bse[1],
                reduced_form=rf.params[1],rf_se=rf.bse[1],tau=b[0],se=se,lo=b[0]-1.96*se,hi=b[0]+1.96*se)
rows=[]
for order in (1,2):
    for h in (3,4,5,6,8,10,12,15,18):
        for k in ('tri','unif'):
            rows.append(fuzzy(h,k,order))
res=pd.DataFrame(rows)
pd.set_option('display.width',200)
print(res.round(3).to_string())
res.to_csv('results/02_fuzzy_rd_grid.csv',index=False)
