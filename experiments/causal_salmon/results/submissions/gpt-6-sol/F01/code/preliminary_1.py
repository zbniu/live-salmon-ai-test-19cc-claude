import pandas as pd, numpy as np
p='upload/data(20261004-171728).csv'; d=pd.read_csv(p)
print(d.shape,d.isna().sum().to_dict(),d.x.value_counts().to_dict())
print(d.groupby('x')[['y','z']].agg(['mean','std','min','max']))
c=d.loc[d.x==1,'y'].min(); print('cutoff',repr(c),'treated below',sum((d.x==1)&(d.y<c)),'n below',sum(d.y<c),'n above',sum(d.y>=c))
print('quantiles y',d.y.quantile([0,.1,.25,.5,.75,.9,1]).to_dict())
print('closest',d.iloc[np.argsort(abs(d.y-c))[:20]].sort_values('y').to_string(index=False))
