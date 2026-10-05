import pandas as pd
df=pd.read_csv("/mnt/user-data/uploads/data.csv"); print(df.groupby("x").z.agg(["mean","count"]))
