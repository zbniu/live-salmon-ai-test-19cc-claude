import pandas as pd, numpy as np
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
c=d.loc[d.x==1,'y'].min(); print('cutoff (min treated y)',c)
print('controls with y>=c:',((d.x==0)&(d.y>=c)).sum(),' controls y<c:',((d.x==0)&(d.y<c)).sum(), 'treated y<c:',((d.x==1)&(d.y<c)).sum())
d['bin']=pd.cut(d.y,np.arange(45,76,2.5))
t=d.groupby(['bin','x']).z.agg(['count','mean']).unstack(); print(t)
print(d.groupby('bin').x.mean())
print(d.groupby('bin').z.mean())
