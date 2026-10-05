import pandas as pd, numpy as np
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
print(d.describe())
print("min y treated",d[d.x==1].y.min())
below=d[d.y<d[d.x==1].y.min()]
print("treated below cutoff:",(below.x==1).sum(), "n below",len(below))
c=d[d.x==1].y.min()
above=d[d.y>=c]
print("n above",len(above),"treated share above",above.x.mean())
d['bin']=pd.cut(d.y,np.arange(45,76,2.5),right=False)
print(d.groupby('bin',observed=True).agg(n=('x','size'),px=('x','mean'),zbar=('z','mean'),ybar=('y','mean')))
print("Naive diff",d[d.x==1].z.mean()-d[d.x==0].z.mean())
