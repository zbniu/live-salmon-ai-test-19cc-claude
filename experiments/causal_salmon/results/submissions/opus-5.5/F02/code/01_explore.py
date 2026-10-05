import pandas as pd, numpy as np
d = pd.read_csv('/mnt/user-data/uploads/data.csv')
print(d.shape, d.isna().sum().to_dict())
print(d.describe().T)
print(d.groupby('x')[['y','z']].describe().T)
t = d[d.x==1]; c = d[d.x==0]
cut = t.y.min()
print("min y among treated (cutoff c):", cut)
print("max y among untreated:", c.y.max())
print("untreated with y>=c:", (c.y>=cut).sum(), " treated:", len(t))
print("units with y>=c:", (d.y>=cut).sum())
print("ties near cutoff (sorted y around c):")
print(d.sort_values('y').query('@cut-0.5<y<@cut+0.5'))
# treatment share by y bins
d['bin'] = pd.cut(d.y, np.arange(0,101,5))
print(d.groupby('bin', observed=True).agg(n=('x','size'), px=('x','mean'), mz=('z','mean'),
      mz_t=('z', lambda s: s[d.loc[s.index,'x']==1].mean()),
      mz_c=('z', lambda s: s[d.loc[s.index,'x']==0].mean())))
print("z range:", d.z.min(), d.z.max(), " follow-up range:", (d.y+d.z).min(), (d.y+d.z).max())
print("naive diff in means:", t.z.mean()-c.z.mean())
