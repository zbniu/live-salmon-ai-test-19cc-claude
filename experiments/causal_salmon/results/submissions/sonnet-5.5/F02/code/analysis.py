import pandas as pd, numpy as np, statsmodels.api as sm
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
c=d[d.x==1].y.min()
print("cutoff (min y among treated) =",c)
print("treated below c:",((d.x==1)&(d.y<c)).sum()," untreated above c:",((d.x==0)&(d.y>=c)).sum(), " n above:",(d.y>=c).sum()," n below:",(d.y<c).sum())
d['r']=d.y-c; d['above']=(d.r>=0).astype(int)
# P(treated | y) above c, binned
d['bin']=pd.cut(d.y,np.arange(45,76,2.5),right=False)
print(d.groupby('bin',observed=True).agg(n=('x','size'),px=('x','mean'),zmean=('z','mean')))
# density check around c
for h in [1,2,3,5]:
    print("density h=%g: left %d right %d"%(h,((d.r<0)&(d.r>=-h)).sum(),((d.r>=0)&(d.r<h)).sum()))
def ll(h,outcome,deg=1,tri=True):
    s=d[abs(d.r)<=h].copy()
    w=(1-abs(s.r)/h) if tri else np.ones(len(s))
    X=pd.DataFrame({'a':s.above,'r':s.r})
    if deg>=2: X['r2']=s.r**2
    X['ar']=s.above*s.r
    if deg>=2: X['ar2']=s.above*s.r**2
    X=sm.add_constant(X)
    m=sm.WLS(s[outcome],X,weights=w).fit(cov_type='HC1')
    return m.params['a'],m.bse['a'],len(s)
rows=[]
for deg in [1,2]:
  for h in [2,3,4,5,7,10]:
    z=ll(h,'z',deg); x=ll(h,'x',deg)
    late=z[0]/x[0]
    # delta method ignoring covariance (approx) + bootstrap below
    rows.append((deg,h,z[2],z[0],z[1],x[0],x[1],late))
res=pd.DataFrame(rows,columns=['deg','h','n','jump_z','se_z','jump_x','se_x','wald'])
print(res.round(3).to_string())
# 2SLS fuzzy RD with robust SE
def fuzzy(h,deg=1):
    s=d[abs(d.r)<=h].copy(); w=(1-abs(s.r)/h)
    s['ar']=s.above*s.r; s['r2']=s.r**2; s['ar2']=s.above*s.r**2
    ex=['r','ar']+(['r2','ar2'] if deg==2 else [])
    X1=sm.add_constant(s[['above']+ex]); first=sm.WLS(s.x,X1,weights=w).fit()
    s['xh']=first.fittedvalues
    X2=sm.add_constant(s[['xh']+ex]); sec=sm.WLS(s.z,X2,weights=w).fit()
    # correct residuals
    Xc=sm.add_constant(s[['x']+ex]); b=sec.params.values
    resid=s.z-Xc.values@b
    Z=X1.values; Xv=Xc.values; W=np.diag(w.values) if len(s)<3000 else None
    A=np.linalg.inv(Z.T@(w.values[:,None]*Xv))
    meat=Z.T@((w.values*resid.values)[:,None]**2*Z)
    V=A@meat@A.T
    return b[1],np.sqrt(V[1,1]),len(s)
print("\n2SLS fuzzy RD (triangular kernel):")
for deg in [1,2]:
    for h in [3,4,5,7,10]:
        b,se,n=fuzzy(h,deg); print(f"deg={deg} h={h} n={n} effect={b:.3f} se={se:.3f} CI=({b-1.96*se:.2f},{b+1.96*se:.2f})")
# bootstrap for headline
rng=np.random.default_rng(1)
b0=fuzzy(5,1)[0]; bs=[]
orig=d.copy()
for i in range(300):
    d=orig.sample(len(orig),replace=True,random_state=int(rng.integers(1e9))).reset_index(drop=True)
    try: bs.append(fuzzy(5,1)[0])
    except Exception: pass
d=orig
print("\nBootstrap h=5 deg=1: est %.3f, boot SE %.3f, 95%% pct CI (%.2f,%.2f)"%(b0,np.std(bs),*np.percentile(bs,[2.5,97.5])))
# naive comparisons
print("\nNaive diff in means:",d[d.x==1].z.mean()-d[d.x==0].z.mean())
s=d[d.y>=c]; print("Naive diff above cutoff only:",s[s.x==1].z.mean()-s[s.x==0].z.mean())
# placebo cutoffs on left of c (no treatment anywhere)
print("\nPlacebo jumps in z at cutoffs below c (untreated side only):")
L=d[d.r<0].copy()
for pc in [48,50,52]:
    s=L.copy(); s['rr']=s.y-pc; s['a']=(s.rr>=0).astype(int); s['ar']=s.a*s.rr
    s=s[abs(s.rr)<=3]; w=1-abs(s.rr)/3
    m=sm.WLS(s.z,sm.add_constant(s[['a','rr','ar']]),weights=w).fit(cov_type='HC1'); print(pc,round(m.params['a'],3),round(m.bse['a'],3))
