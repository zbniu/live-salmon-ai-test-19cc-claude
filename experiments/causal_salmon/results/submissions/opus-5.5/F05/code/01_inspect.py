import pandas as pd, numpy as np
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
print(df.shape); print(df.dtypes); print(df.head())
print(df.isna().sum())
print(df.describe())
print(df.groupby("x").describe().T)
print("unique x:", sorted(df.x.unique()))
print("y min/max", df.y.min(), df.y.max(), "z min/max", df.z.min(), df.z.max())
fu = df.y + df.z
print("follow-up min/max", fu.min(), fu.max())
print("followup at 0:", (fu<=0).sum(), " at 100:", (fu>=100).sum())
print("y at 0:", (df.y<=0).sum(), " at 100:", (df.y>=100).sum())
print("n unique y,z:", df.y.nunique(), df.z.nunique())
