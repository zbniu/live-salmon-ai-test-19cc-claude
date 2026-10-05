import pandas as pd, numpy as np
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
print(df.shape); print(df.dtypes); print(df.head())
print(df.describe())
print("x counts:", df.x.value_counts().to_dict())
print("unique y:", df.y.nunique(), " y decimals sample:", df.y.head(10).tolist())
t = df[df.x==1]; c = df[df.x==0]
cut = t.y.min()
print("min y among treated (cutoff c):", cut, " max y treated:", t.y.max())
print("controls with y >= c:", (c.y>=cut).sum(), " controls with y < c:", (c.y<cut).sum())
print("treated with y < c:", (t.y<cut).sum())
print("ties at cutoff:", (df.y==cut).sum())
# treatment share by y bins
bins = np.arange(0,101,5)
df['bin']=pd.cut(df.y,bins,include_lowest=True)
print(df.groupby('bin',observed=True).agg(n=('x','size'),px=('x','mean'),mz=('z','mean')))
print("mean z by x:", df.groupby('x').z.mean().to_dict())
