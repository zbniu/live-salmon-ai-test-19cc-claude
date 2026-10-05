import pandas as pd, numpy as np
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
c=d[d.x==1].y.min()
# density check: counts in windows either side of cutoff
for h in (2,3,5):
    print("window",h,"below",((d.y<c)&(d.y>=c-h)).sum(),"above",((d.y>=c)&(d.y<c+h)).sum())
try:
    from rdrobust import rdrobust, rddensity
    r=rdrobust(d.z.values,d.y.values,c=c,fuzzy=d.x.values)
    print(r)
    try:
        print(rddensity(d.y.values,c=c))
    except Exception as e: print("rddensity error:",repr(e))
except Exception as e:
    print("rdrobust error:",repr(e))
