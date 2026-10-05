import pandas as pd
p='upload/data(20261004-171728).csv'; d=pd.read_csv(p); t=d[d.x==1]; print('means',t.y.mean(),t.z.mean(),t.y.add(t.z).mean()); print('end min/max',t.y.add(t.z).min(),t.y.add(t.z).max()); print('raw contrast',t.z.mean()-d[d.x==0].z.mean()); print('quantiles end',t.y.add(t.z).quantile([0,.5,1]).to_dict())
