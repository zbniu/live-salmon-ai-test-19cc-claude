import csv, json
import numpy as np
import pandas as pd
from scipy import stats

p='upload/data(20261004-071351).csv'
df=pd.read_csv(p)
assert list(df.columns)==['x','y','z']
assert len(df)==2000 and df.notna().all().all()
assert set(df.x.unique())=={0,1}
assert (df.y.between(0,100)).all()
assert ((df.y+df.z).between(0,100)).all()
T=df[df.x==1]; C=df[df.x==0]
t=T.y.min()
print('DATA:',df.shape,'treated:',len(T),'control:',len(C),'unique y:',df.y.nunique())
print('SUMMARY BY X')
print(df.groupby('x')[['y','z']].agg(['mean','std','min','max']).to_string())
print('Minimum treated y:',t,'rank among all baseline y:',(df.y<t).sum()+1)
print('Control count above minimum treated y:',int((C.y>=t).sum()))
print('Mean difference z:',T.z.mean()-C.z.mean())
print('Correlations y,z overall/control/treated:',df.y.corr(df.z),C.y.corr(C.z),T.y.corr(T.z))
print('Quantiles y by x')
print(df.groupby('x').y.quantile([0,.1,.25,.5,.75,.9,1]).to_string())
print('BIN SUMMARY')
bins=np.arange(0,101,5)
df['bin']=pd.cut(df.y,bins,include_lowest=True,right=False)
print(df.groupby(['bin','x'],observed=False).z.agg(['size','mean','std']).to_string())
print('OLS (descriptive) z~x+y, x*y; HC3')
for vars in [['x','y'],['x','y','xy']]:
    d=df.assign(xy=df.x*df.y)
    X=np.column_stack([np.ones(len(d))]+[d[v].to_numpy() for v in vars])
    b=np.linalg.lstsq(X,d.z.to_numpy(),rcond=None)[0]
    e=d.z.to_numpy()-X@b
    h=np.einsum('ij,jk,ik->i',X,np.linalg.inv(X.T@X),X)
    v=np.linalg.inv(X.T@X)@(X.T@np.diag((e/(1-h))**2)@X)@np.linalg.inv(X.T@X)
    se=np.sqrt(np.diag(v))
    print(vars, dict(zip(['const']+vars,b)),dict(zip(['const']+vars,se)))
print('Near-threshold raw means and counts')
for h in [2,3,5,7,10,15]:
    sub=df[(df.y>=t-h)&(df.y<t+h)]
    below=sub[sub.y<t]; above=sub[sub.y>=t]
    print(h,len(below),len(above),below.z.mean(),above.z.mean(),len(above[above.x==1]),len(above[above.x==0]))
