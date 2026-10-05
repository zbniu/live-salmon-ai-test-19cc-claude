import pandas as pd, numpy as np
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
print(df.shape); print(df.dtypes); print(df.head())
print(df.describe())
print("missing:", df.isna().sum().to_dict())
print(df.groupby('x')[['y','z']].describe().T)
t=df[df.x==1]; c=df[df.x==0]
print("min y treated:", t.y.min(), " max y treated:", t.y.max())
print("max y control:", c.y.max())
cut=t.y.min()
print("controls with y >= min treated y:", (c.y>=cut).sum())
print("treated with y > max control y:", (t.y>c.y.max()).sum())
print("unique y values:", df.y.nunique(), " is integer:", (df.y==df.y.round()).all())
# treated share by y bins in the upper region
bins=np.quantile(df.y,[0,.2,.4,.5,.6,.7,.8,.9,.95,1])
df['bin']=pd.cut(df.y,bins,include_lowest=True)
print(df.groupby('bin',observed=True).agg(n=('x','size'),treated=('x','sum'),share=('x','mean'),zbar=('z','mean')))
