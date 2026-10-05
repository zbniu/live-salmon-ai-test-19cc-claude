import pandas as pd, numpy as np
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
print(df.shape); print(df.dtypes); print(df.isna().sum())
print(df.describe())
print(df.groupby('x')[['y','z']].describe().T)
t = df[df.x==1]; c = df[df.x==0]
cut = t.y.min()
print("min y among treated (c):", cut)
print("controls with y >= c:", (c.y>=cut).sum(), " treated:", len(t))
print("y ties at cutoff:", (df.y==cut).sum())
# binned
df['bin']=pd.cut(df.y, bins=np.arange(0,105,5))
print(df.groupby('bin',observed=True).agg(n=('x','size'),ptreat=('x','mean'),z=('z','mean')))
print(df.groupby(['bin','x'],observed=True).z.agg(['size','mean']).unstack())
