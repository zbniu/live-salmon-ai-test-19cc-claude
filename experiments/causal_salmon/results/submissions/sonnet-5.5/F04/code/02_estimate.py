import pandas as pd, numpy as np
from scipy import stats
import statsmodels.formula.api as smf
d = pd.read_csv('/mnt/user-data/uploads/data.csv')
a,b = d[d.x==1].z, d[d.x==0].z
diff = a.mean()-b.mean()
se = np.sqrt(a.var(ddof=1)/len(a)+b.var(ddof=1)/len(b))
print(f'Unadjusted diff in means: {diff:.4f}, Neyman SE {se:.4f}, 95% CI [{diff-1.96*se:.4f},{diff+1.96*se:.4f}]')
print(stats.ttest_ind(a,b,equal_var=False))
print('Mann-Whitney', stats.mannwhitneyu(a,b,alternative='greater'))
# randomization inference
rng = np.random.default_rng(1); z=d.z.values; n1=600
perm=np.array([ (lambda p: z[p[:n1]].mean()-z[p[n1:]].mean())(rng.permutation(len(z))) for _ in range(20000)])
print('RI p one-sided', (perm>=diff).mean(), 'two-sided', (np.abs(perm)>=abs(diff)).mean())
# ANCOVA
d['yc']=d.y-d.y.mean()
m1 = smf.ols('z~x',d).fit(cov_type='HC3'); print(m1.summary().tables[1])
m2 = smf.ols('z~x+yc',d).fit(cov_type='HC3'); print(m2.summary().tables[1]); print('R2',m2.rsquared)
m3 = smf.ols('z~x*yc',d).fit(cov_type='HC3'); print(m3.summary().tables[1])
m4 = smf.ols('z~x*(yc+I(yc**2)+I(yc**3))',d).fit(cov_type='HC3'); print(m4.summary().tables[1])
# nonlinearity check: F test of cubic terms vs linear (classical)
print('compare linear vs interaction', smf.ols('z~x+yc',d).fit().compare_f_test(smf.ols('z~x*(yc+I(yc**2)+I(yc**3))',d).fit()))
# residual diagnostics
r=m2.resid
print('resid sd',r.std(),'skew',stats.skew(r),'kurt',stats.kurtosis(r))
print('resid sd by arm', r[d.x==1].std(), r[d.x==0].std())
# effect by baseline tercile
d['bin']=pd.qcut(d.y,4,labels=False)
for k,g in d.groupby('bin'):
    A,B=g[g.x==1].z,g[g.x==0].z
    print(k, round(g.y.mean(),1), len(A), len(B), round(A.mean()-B.mean(),3), round(np.sqrt(A.var()/len(A)+B.var()/len(B)),3))
# quantile effects
for q in [.1,.25,.5,.75,.9]:
    qa=smf.quantreg('z~x+yc',d).fit(q=q); print('QR',q,round(qa.params['x'],3),round(qa.bse['x'],3))
