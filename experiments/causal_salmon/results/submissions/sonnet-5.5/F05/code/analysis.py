import pandas as pd, numpy as np, statsmodels.formula.api as smf
from scipy import stats
d=pd.read_csv('/mnt/user-data/uploads/data.csv')
t=d[d.x==1]; c=d[d.x==0]
print("n treated/control",len(t),len(c))
print("group means z",t.z.mean(),c.z.mean(),"y",t.y.mean(),c.y.mean())
diff=t.z.mean()-c.z.mean()
se=np.sqrt(t.z.var()/len(t)+c.z.var()/len(c))
print("Diff in means",diff,"SE",se,"95% CI",diff-1.96*se,diff+1.96*se)
print("Welch t",stats.ttest_ind(t.z,c.z,equal_var=False))
print("Mann-Whitney",stats.mannwhitneyu(t.z,c.z))
print("Balance on baseline y:",stats.ttest_ind(t.y,c.y,equal_var=False))
print("KS y",stats.ks_2samp(t.y,c.y))
m0=smf.ols('z~x',d).fit(cov_type='HC3');print(m0.summary().tables[1])
m1=smf.ols('z~x+y',d).fit(cov_type='HC3');print(m1.summary().tables[1])
m2=smf.ols('z~x*I(y-y.mean())',d).fit(cov_type='HC3');print(m2.summary().tables[1])
m3=smf.ols('z~x+y+I(y**2)',d).fit(cov_type='HC3');print(m3.summary().tables[1])
# heterogeneity by baseline tertile
d['b']=pd.qcut(d.y,4,labels=False)
for b,g in d.groupby('b'):
    a=g[g.x==1].z;bb=g[g.x==0].z
    print("quartile",b,"n",len(a),len(bb),"diff",a.mean()-bb.mean(),"se",np.sqrt(a.var()/len(a)+bb.var()/len(bb)))
# permutation test
rng=np.random.default_rng(0);obs=diff;cnt=0;z=d.z.values;n1=600
perm=[]
for i in range(10000):
    p=rng.permutation(len(z));perm.append(z[p[:n1]].mean()-z[p[n1:]].mean())
perm=np.array(perm);print("perm p",(np.abs(perm)>=abs(obs)).mean())
print("z quantiles by group");print(d.groupby('x').z.quantile([.05,.25,.5,.75,.95]).unstack())
print("skew",stats.skew(t.z),stats.skew(c.z))
print("corr y,z",d[['y','z']].corr().iloc[0,1])
