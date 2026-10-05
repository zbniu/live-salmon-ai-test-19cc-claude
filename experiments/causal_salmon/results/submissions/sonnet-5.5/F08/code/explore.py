import pandas as pd, numpy as np
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
c=d[d.x==1].y.min(); print('cutoff',c)
d['bin']=pd.cut(d.y,np.arange(45,76,2.5))
print(d.groupby('bin',observed=True).agg(n=('x','size'),ptreat=('x','mean'),z0=('z',lambda s:np.nan),).drop(columns='z0'))
print(d[d.x==0].groupby('bin',observed=True).z.agg(['size','mean','std']))
print(d[d.x==1].groupby('bin',observed=True).z.agg(['size','mean','std']))
print('naive',d[d.x==1].z.mean()-d[d.x==0].z.mean())
