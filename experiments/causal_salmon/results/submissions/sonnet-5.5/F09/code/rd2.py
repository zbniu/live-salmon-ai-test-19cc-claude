import pandas as pd, numpy as np
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
c=d.loc[d.x==1,'y'].min()
d['u']=d.y-c; d['Z']=(d.u>=0).astype(int)

def wls(X,y,w):
    XtW=X.T*w; return np.linalg.solve(XtW@X,XtW@y)

def fuzzy(h,deg=1,tri=True):
    s=d[d.u.abs()<=h]
    w=(1-s.u.abs()/h).values if tri else np.ones(len(s))
    u=s.u.values; Z=s.Z.values
    X=np.column_stack([np.ones(len(s))]+[u**k for k in range(1,deg+1)]+[Z*u**k for k in range(1,deg+1)])
    Zi=np.column_stack([X,Z])           # instruments
    Xe=np.column_stack([X,s.x.values])  # regressors
    y=s.z.values
    # 2SLS
    P=Zi@np.linalg.solve((Zi.T*w)@Zi,(Zi.T*w)@Xe)
    beta=np.linalg.solve((P.T*w)@Xe,(P.T*w)@y)
    e=y-Xe@beta
    A=np.linalg.inv((P.T*w)@Xe)
    M=(P*(w*e)[:,None]).T@(P*(w*e)[:,None])
    V=A@M@A.T
    first=wls(Zi,s.x.values,w)[-1]; itt=wls(Zi,y,w)[-1]
    return dict(h=h,deg=deg,n=len(s),first_stage=first,ITT_jump=itt,LATE=beta[-1],se=np.sqrt(V[-1,-1]))

rows=[fuzzy(h,1) for h in [4,6,8,10,12,15,20,30]]+[fuzzy(h,2) for h in [10,15,20,30]]+[fuzzy(h,3) for h in [20,30]]
r=pd.DataFrame(rows); r['lo']=r.LATE-1.96*r.se; r['hi']=r.LATE+1.96*r.se
print('cutoff',c); print(r.round(3).to_string()); r.to_csv('../results/fuzzy_rd.csv',index=False)

print('\nNaive diff in means:',d[d.x==1].z.mean()-d[d.x==0].z.mean())
def ols_x(s):
    X=np.column_stack([np.ones(len(s)),s.x,s.y]); b=np.linalg.solve(X.T@X,X.T@s.z); e=s.z-X@b
    Xi=np.linalg.inv(X.T@X); V=Xi@((X*e.values[:,None]**1).T@(X*e.values[:,None]))@Xi
    return b[1],np.sqrt(V[1,1])
print('OLS z~x+y, all:',ols_x(d)); print('OLS z~x+y, y>=cutoff:',ols_x(d[d.y>=c]))
print('\nDensity counts below/above cutoff within h:')
for h in [1,2,3,5,10]: print(h,((d.u<0)&(d.u>=-h)).sum(),((d.u>=0)&(d.u<h)).sum())
print('\nTreated share above cutoff, by u-bin:'); 
a=d[d.u>=0]; print(a.groupby(pd.cut(a.u,[0,2,5,10,20]),observed=True).x.mean())
