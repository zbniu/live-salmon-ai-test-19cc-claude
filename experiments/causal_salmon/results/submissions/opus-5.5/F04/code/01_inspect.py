import pandas as pd
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
print(df.shape); print(df.dtypes); print(df.head())
print(df.describe())
print(df.isna().sum())
print(df.x.value_counts())
print(df.groupby('x')[['y','z']].describe().T)
fu = df.y + df.z
print("follow-up range:", fu.min(), fu.max())
print("y==0/100:", (df.y<=0).sum(), (df.y>=100).sum(), "fu<=0/>=100:", (fu<=0).sum(), (fu>=100).sum())
print("unique y count", df.y.nunique(), "unique z", df.z.nunique())
