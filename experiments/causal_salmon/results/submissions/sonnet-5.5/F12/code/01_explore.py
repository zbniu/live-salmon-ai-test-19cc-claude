import pandas as pd, numpy as np
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
print(df.shape); print(df.dtypes); print(df.isna().sum())
print(df.describe())
print(df.groupby("x")[["y","z"]].describe().T)
print("naive diff in z (x=1 minus x=0):", df[df.x==1].z.mean()-df[df.x==0].z.mean())
t=df[df.x==1].y; c=df[df.x==0].y
print("treated y min/max", t.min(), t.max(), "n", len(t))
print("control y min/max", c.min(), c.max(), "n", len(c))
print("control with y>=min treated y:", (c>=t.min()).sum())
print("control y quantiles", c.quantile([.1,.25,.5,.75,.9,.95,.99]).values)
print("treated y quantiles", t.quantile([.0,.1,.25,.5,.75,.9,1]).values)
# bins of y
df["ybin"]=pd.cut(df.y,bins=np.arange(0,101,5))
print(df.groupby("ybin",observed=True).agg(n=("x","size"),ntr=("x","sum"),zmean=("z","mean")).to_string())
