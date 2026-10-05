import pandas as pd, numpy as np
from scipy import stats
d = pd.read_csv('/mnt/user-data/uploads/data.csv')
print(d.shape); print(d.dtypes); print(d.isna().sum())
print(d.describe())
print(d.x.value_counts())
print(d.groupby('x')[['y','z']].agg(['mean','std','median','min','max']))
# balance check on baseline
a,b = d[d.x==1], d[d.x==0]
print('baseline y diff', a.y.mean()-b.y.mean(), stats.ttest_ind(a.y,b.y,equal_var=False))
print('KS y', stats.ks_2samp(a.y,b.y))
print('corr y,z', d[['y','z']].corr().iloc[0,1])
print('corr within arm', a[['y','z']].corr().iloc[0,1], b[['y','z']].corr().iloc[0,1])
print('skew z', stats.skew(a.z), stats.skew(b.z))
print('quantiles z by arm'); print(d.groupby('x').z.quantile([.01,.05,.25,.5,.75,.95,.99]).unstack())
print('quantiles y by arm'); print(d.groupby('x').y.quantile([0,.01,.25,.5,.75,.99,1]).unstack())
