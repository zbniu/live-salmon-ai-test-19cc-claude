import pandas as pd, numpy as np
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
print(df.shape); print(df.dtypes); print(df.head()); print(df.isna().sum())
print(df.describe())
print(df.groupby('x')[['y','z']].describe().T)
t=df[df.x==1]; c=df[df.x==0]
print("min y treated:", t.y.min(), " max y treated:", t.y.max())
print("controls with y >= min treated y:", (c.y>=t.y.min()).sum())
print("naive diff in mean z:", t.z.mean()-c.z.mean())
bins=np.quantile(df.y,np.linspace(0,1,21))
df['bin']=pd.cut(df.y,bins,include_lowest=True)
g=df.groupby('bin',observed=True)
out=pd.DataFrame({'n':g.size(),'n_treat':g.x.sum(),'p_treat':g.x.mean(),
  'z_treat':df[df.x==1].groupby('bin',observed=True).z.mean(),
  'z_ctrl':df[df.x==0].groupby('bin',observed=True).z.mean()})
print(out.to_string())
