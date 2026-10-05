import pandas as pd, numpy as np, statsmodels.formula.api as smf
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
out=[]
def P(*a):
    s=' '.join(str(x) for x in a); print(s); out.append(s)
P('n',len(d)); P(d.groupby('x')[['y','z']].agg(['mean','std','min','max']).to_string())
P('min y treated',d[d.x==1].y.min())
# overlap: untreated with y>=min treated y
c=d[d.x==1].y.min()
P('untreated with y>=cutoff:',((d.x==0)&(d.y>=c)).sum(),' untreated below:',((d.x==0)&(d.y<c)).sum())
P('treated share among y>=c:',d[d.y>=c].x.mean())
P('naive diff',d[d.x==1].z.mean()-d[d.x==0].z.mean())
# z vs y shape
P(smf.ols('z~y',d).fit().summary().tables[1])
# bins of y
d['bin']=pd.cut(d.y,np.arange(45,80,5))
P(d.groupby(['bin','x'],observed=True).z.agg(['count','mean']).to_string())
# restrict to overlap region y>=c
o=d[d.y>=c].copy()
for f in ['z~x+y','z~x+y+I(y**2)','z~x*I(y-67)','z~x+y+I(y**2)+I(y**3)']:
    m=smf.ols(f,o).fit(cov_type='HC3'); P(f,'| coef x',m.params['x'],'se',m.bse['x'],'CI',m.conf_int().loc['x'].tolist())
# ATT via interaction: effect at treated y distribution
m=smf.ols('z~x*(y+I(y**2))',o).fit(cov_type='HC3')
t=o[o.x==1]; t1=t.copy();t1['x']=1;t0=t.copy();t0['x']=0
att=(m.predict(t1)-m.predict(t0)).mean(); P('ATT interaction quad',att)
# bootstrap
rng=np.random.default_rng(1);bs=[]
for _ in range(1000):
    b=o.sample(len(o),replace=True,random_state=int(rng.integers(1e9)))
    mm=smf.ols('z~x*(y+I(y**2))',b).fit();tt=b[b.x==1]
    a=tt.copy();a['x']=1;c0=tt.copy();c0['x']=0
    bs.append((mm.predict(a)-mm.predict(c0)).mean())
P('boot SE',np.std(bs),'CI',np.percentile(bs,[2.5,97.5]))
# whole sample with flexible control
m=smf.ols('z~x+y+I(y**2)+I(y**3)',d).fit(cov_type='HC3'); P('full sample cubic',m.params['x'],m.bse['x'])
# nearest-neighbor matching on y (untreated within overlap)
u=o[o.x==0]; 
from scipy.spatial import cKDTree
tr=cKDTree(u[['y']].values); dist,idx=tr.query(t[['y']].values,k=5)
mz=u.z.values[idx].mean(1); diff=t.z.values-mz; P('NN5 matching ATT',diff.mean(),'se approx',diff.std()/np.sqrt(len(diff)),'max dist',dist.max())
# local window
for w in [3,5]:
    q=d[(d.y>=c)&(d.y<c+w)]; mm=smf.ols('z~x+y',q).fit(cov_type='HC3'); P('window',w,len(q),q.x.sum(),mm.params['x'],mm.bse['x'])
# check z-y relationship below cutoff & continuity
mm=smf.ols('z~y',d[d.x==0]).fit(); P('untreated all slope',mm.params.to_dict())
open('results/output.txt','w').write('\n'.join(out))
