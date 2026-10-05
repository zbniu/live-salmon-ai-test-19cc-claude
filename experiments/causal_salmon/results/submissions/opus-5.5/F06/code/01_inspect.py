"""01_inspect.py - load data.csv, check structure, describe variables, check balance of y."""
import pandas as pd
import numpy as np
from scipy import stats

OUT = "/home/claude/submission/results/01_inspect.txt"
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
lines = []
p = lines.append
p(f"shape: {df.shape}")
p(f"columns: {list(df.columns)}")
p(f"dtypes:\n{df.dtypes}")
p(f"missing per column:\n{df.isna().sum()}")
p(f"head:\n{df.head(10)}")
p(f"describe:\n{df.describe().T}")
p(f"x value counts:\n{df['x'].value_counts().sort_index()}")
p(f"unique y values: {df['y'].nunique()}, unique z values: {df['z'].nunique()}")
p(f"y min/max: {df['y'].min()} / {df['y'].max()}")
end = df['y'] + df['z']
p(f"implied end-of-term score (y+z) min/max: {end.min()} / {end.max()}")
p(f"count y+z <0: {(end<0).sum()}, >100: {(end>100).sum()}, ==100: {(end==100).sum()}, ==0: {(end==0).sum()}")
p(f"count y==100: {(df['y']==100).sum()}, y==0: {(df['y']==0).sum()}")
p("")
p("By group:")
p(f"{df.groupby('x')[['y','z']].describe().T}")
g1, g0 = df[df.x == 1], df[df.x == 0]
t = stats.ttest_ind(g1.y, g0.y, equal_var=False)
p(f"Balance of y (pre-treatment): mean diff = {g1.y.mean()-g0.y.mean():.4f}, Welch t = {t.statistic:.3f}, p = {t.pvalue:.4f}")
ks = stats.ks_2samp(g1.y, g0.y)
p(f"KS test y by group: D = {ks.statistic:.4f}, p = {ks.pvalue:.4f}")
p(f"corr(y, z) overall = {df[['y','z']].corr().iloc[0,1]:.4f}")
p(f"corr(y, z) x=0 = {g0[['y','z']].corr().iloc[0,1]:.4f}; x=1 = {g1[['y','z']].corr().iloc[0,1]:.4f}")
p(f"duplicate rows: {df.duplicated().sum()}")
txt = "\n".join(str(l) for l in lines)
open(OUT, "w").write(txt)
print(txt)
