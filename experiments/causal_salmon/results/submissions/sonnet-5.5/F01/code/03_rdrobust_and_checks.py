import pandas as pd, numpy as np, statsmodels.formula.api as smf
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
c=d[d.x==1].y.min(); d['r']=d.y-c; d['above']=(d.r>=0).astype(int)
try:
    from rdrobust import rdrobust, rdbwselect
    for p in (1,2):
        r=rdrobust(d.z.values,d.y.values,c=c,fuzzy=d.x.values,p=p)
        print('\n=== rdrobust fuzzy, p=%d ==='%p); print(r)
    r=rdrobust(d.x.values,d.y.values,c=c,p=1); print('\n=== first stage (jump in P(x=1)) ==='); print(r)
    r=rdrobust(d.z.values,d.y.values,c=c,p=1); print('\n=== reduced form (jump in E[z]) ==='); print(r)
except Exception as e:
    print('rdrobust unavailable/error:',repr(e))
# global polynomial fuzzy-RD via manual 2SLS with different orders
import statsmodels.api as sm
def tsls(order,h=None):
    s=d if h is None else d[d.r.abs()<=h]
    f=lambda k:' + '.join([f'I(r**{j})' for j in range(1,k+1)]+[f'I(r**{j}*above)' for j in range(1,k+1)])
    X=pd.DataFrame({'const':1.0},index=s.index)
    for j in range(1,order+1): X[f'r{j}']=s.r**j; X[f'ra{j}']=s.r**j*s.above
    Z=X.copy(); Z['above']=s.above
    fs=sm.OLS(s.x,Z).fit(); xh=fs.fittedvalues
    X2=X.copy(); X2['x']=s.x; Xh=X.copy(); Xh['x']=xh
    b=np.linalg.solve(Xh.T@Xh,Xh.T@s.z); res=s.z-X2@b
    A=np.linalg.inv(Xh.T@Xh); M=Xh.values*res.values[:,None]; V=A@(M.T@M)@A
    return b[-1],np.sqrt(V[-1,-1])
print('\nGlobal polynomial fuzzy RD (all data):')
for k in (1,2,3,4):
    e,se=tsls(k); print(f' order {k}: effect={e:.3f} se={se:.3f}  95%CI=({e-1.96*se:.2f},{e+1.96*se:.2f})')
# untreated-only jump at cutoff (selection check): E[z|x=0] jump at c
print('\nJump at c in E[z|x=0] (applicants vs non-applicants selection check), local linear unif:')
for h in (5,8,10,15,20):
    s=d[(d.x==0)&(d.r.abs()<=h)]
    m=smf.ols('z~above+r+r:above',s).fit(cov_type='HC1'); print(f' h={h}: jump={m.params["above"]:.3f} se={m.bse["above"]:.3f}')
# gap among y>=c: treated vs untreated, local at c
print('\nTreated minus untreated gap among y>=c, by bandwidth above c (local linear in r):')
for h in (4,6,8,10,15,20):
    s=d[(d.r>=0)&(d.r<=h)]
    m=smf.ols('z~x+r',s).fit(cov_type='HC1'); m2=smf.ols('z~x*r',s).fit(cov_type='HC1')
    print(f' h={h}: gap={m.params["x"]:.3f} se={m.bse["x"]:.3f}  | with interaction, gap at r=0: {m2.params["x"]:.3f} se={m2.bse["x"]:.3f}')
# placebo cutoffs on the left (no treatment anywhere)
print('\nPlacebo jumps in E[z] at cutoffs left of c (untreated region only), local linear h=4:')
L=d[d.r<0]
for pc in (47,49,51,53):
    s=L[(L.y-pc).abs()<=4].copy(); s['a']=(s.y>=pc).astype(int); s['rr']=s.y-pc
    m=smf.ols('z~a+rr+rr:a',s).fit(cov_type='HC1'); print(f' cutoff {pc}: jump={m.params["a"]:.3f} se={m.bse["a"]:.3f}')
# density
print('\nCounts within 3 points of c: below',((d.r<0)&(d.r>=-3)).sum(),'above',((d.r>=0)&(d.r<3)).sum())
