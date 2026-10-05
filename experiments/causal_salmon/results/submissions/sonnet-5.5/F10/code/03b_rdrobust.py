import pandas as pd
from rdrobust import rdrobust
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
c=d[d.x==1].y.min()
r=rdrobust(d.z.values,d.y.values,c=c,fuzzy=d.x.values)
print(r)
