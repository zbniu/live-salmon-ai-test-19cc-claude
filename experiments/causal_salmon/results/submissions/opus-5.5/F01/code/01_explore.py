import pandas as pd, numpy as np
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
print(df.shape); print(df.dtypes); print(df.head())
print(df.isna().sum())
print(df.describe())
print("x counts:", df.x.value_counts().to_dict())
t = df[df.x==1]; c = df[df.x==0]
print("treated y range:", t.y.min(), t.y.max(), " control y range:", c.y.min(), c.y.max())
cut = t.y.min()
print("cutoff c = min y among treated:", cut)
print("n untreated with y >= c:", (c.y>=cut).sum(), " n untreated with y < c:", (c.y<cut).sum())
print("n with y == c:", (df.y==cut).sum(), "ties in y overall:", df.y.duplicated().sum())
print("unique y values:", df.y.nunique())
print("mean z treated/untreated:", t.z.mean(), c.z.mean(), "naive diff:", t.z.mean()-c.z.mean())
# P(x=1|y) by bins
df['bin'] = pd.cut(df.y, bins=np.arange(0,101,5))
print(df.groupby('bin', observed=True).agg(n=('x','size'), px=('x','mean'), z=('z','mean'),
      z_t=('z', lambda s: s[df.loc[s.index,'x']==1].mean()),
      z_c=('z', lambda s: s[df.loc[s.index,'x']==0].mean())))
