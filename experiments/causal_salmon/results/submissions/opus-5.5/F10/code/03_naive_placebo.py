import pandas as pd, numpy as np
import statsmodels.formula.api as smf
d = pd.read_csv('/mnt/user-data/uploads/data.csv')
c = d.loc[d.x==1,'y'].min()
print('--- Naive comparisons (confounded by unrecorded applicant circumstances) ---')
print('raw diff in means:', d[d.x==1].z.mean()-d[d.x==0].z.mean())
m1=smf.ols('z~x+y',d).fit(cov_type='HC1'); print('z~x+y all:', m1.params['x'], m1.bse['x'])
a=d[d.y>=c].copy(); a['r']=a.y-c
m2=smf.ols('z~x*r',a).fit(cov_type='HC1'); print(m2.summary().tables[1])
print('within y>=c, treated-untreated gap at cutoff (x coef):',m2.params['x'],' slope of gap per y point:',m2.params['x:r'])
print('--- Slope of untreated z on y, below vs above cutoff (untreated only) ---')
b=d[d.x==0].copy(); b['r']=b.y-c; b['above']=(b.y>=c).astype(int)
m3=smf.ols('z~r*above',b).fit(cov_type='HC1'); print(m3.summary().tables[1])
print('--- Placebo cutoffs for reduced-form jump in z (local linear, uniform, h=4, within one side of c) ---')
def jump(sub,cc,h=4):
    L=sub[(sub.y<cc)&(sub.y>=cc-h)]; R=sub[(sub.y>=cc)&(sub.y<cc+h)]
    fl=np.polyfit(L.y-cc,L.z,1)[1]; fr=np.polyfit(R.y-cc,R.z,1)[1]; return fr-fl
for cc in [50,52,54]:
    print('placebo below c at',cc,':',round(jump(d[d.y<c],cc),3))
for cc in [62,65,68,71]:
    print('placebo above c at',cc,':',round(jump(d[d.y>=c],cc),3))
