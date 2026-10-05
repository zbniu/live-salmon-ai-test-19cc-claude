import pandas as pd, numpy as np
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
print(d.shape, d.isna().sum().to_dict())
c=d[d.x==1].y.min(); print('cutoff (min treated y) =',c)
print('treated with y<c:',((d.x==1)&(d.y<c)).sum())
print('untreated with y>=c:',((d.x==0)&(d.y>=c)).sum(),' treated:',((d.x==1)).sum())
print('naive diff in means z:',d[d.x==1].z.mean()-d[d.x==0].z.mean())
print('P(x=1|y>=c)=',d[d.y>=c].x.mean())
d['bin']=pd.cut(d.y,np.arange(45,76,2.5))
t=d.groupby('bin',observed=True).agg(n=('x','size'),p_treat=('x','mean'),mean_z=('z','mean'),mean_z_x1=('z',lambda s: s[d.loc[s.index,'x']==1].mean()),mean_z_x0=('z',lambda s: s[d.loc[s.index,'x']==0].mean()))
print(t.round(3).to_string())
t.to_csv('../results/binned_summary.csv')
# above cutoff: treated vs untreated, adjusted for y
a=d[d.y>=c]
import statsmodels.formula.api as smf
print(smf.ols('z~x+y',a).fit(cov_type='HC1').summary().tables[1])
print(a.groupby('x').y.describe())
