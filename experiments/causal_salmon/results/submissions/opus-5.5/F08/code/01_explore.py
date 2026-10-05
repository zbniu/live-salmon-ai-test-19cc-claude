import pandas as pd, numpy as np
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
print(d.shape, d.isna().sum().to_dict()); print(d.describe())
print(d.groupby('x')[['y','z']].describe().T)
t=d[d.x==1]; c=d[d.x==0]
cut=t.y.min(); print('min y treated',cut,'max y treated',t.y.max())
print('controls with y>=min treated y:',(c.y>=cut).sum())
d['bin']=pd.cut(d.y,np.arange(0,101,5))
print(d.groupby('bin',observed=True).agg(n=('x','size'),treated=('x','sum'),zmean=('z','mean')))
print('naive diff', t.z.mean()-c.z.mean())
