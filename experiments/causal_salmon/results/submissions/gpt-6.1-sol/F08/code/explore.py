from pathlib import Path
import hashlib, json, sys
import numpy as np
import scipy
from scipy import stats
import sklearn
from sklearn.preprocessing import SplineTransformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'submission/results'
data_path=ROOT/'upload/data(20261004-180753).csv'
description_path=ROOT/'upload/STUDY_DESCRIPTION(20261004-180753).md'
d=np.genfromtxt(data_path,delimiter=',',names=True)
x,y,z=d['x'],d['y'],d['z']
t=x==1; c=x==0
assert d.dtype.names==('x','y','z') and len(d)==2000
assert np.isfinite(np.column_stack([x,y,z])).all()
assert set(x)=={0,1} and t.sum()==600

def summary(a):
 return {'n':len(a),'mean':float(a.mean()),'sd':float(a.std(ddof=1)),
         'min':float(a.min()),'max':float(a.max()),
         'quantiles':np.quantile(a,[0,.1,.25,.5,.75,.9,1]).tolist()}
result={'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [data_path,description_path]},
        'versions':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
                    'sklearn':sklearn.__version__,'matplotlib':matplotlib.__version__},
        'n':len(d),'group_summaries':{},'bins':[]}
for name,mask in [('attended',t),('did_not_attend',c)]:
 result['group_summaries'][name]={'y':summary(y[mask]),'z':summary(z[mask])}
result['raw_gain_difference']=float(z[t].mean()-z[c].mean())
result['treated_above_control_max']=int(np.sum(t & (y>y[c].max())))
result['treated_below_control_min']=int(np.sum(t & (y<y[c].min())))
for lo in np.arange(0,100,5):
 row={'y_lower':int(lo),'y_upper':int(lo+5)}
 for name,mask in [('treated',t),('control',c)]:
  m=mask & (y>=lo) & (y<lo+5)
  row[name+'_n']=int(m.sum()); row[name+'_mean_gain']=float(z[m].mean()) if m.any() else None
 result['bins'].append(row)

# Exploratory standardization, with ATT always averaged over all 600 attendees.
fits=[]
v=(y-60)/20
for degree in range(1,7):
 B=np.column_stack([v**j for j in range(degree+1)])
 coef=np.linalg.lstsq(B[c],z[c],rcond=None)[0]
 residual=z[c]-B[c]@coef
 pred=B[t]@coef
 fits.append({'method':'control_polynomial','degree':degree,
              'ATT':float(np.mean(z[t]-pred)),
              'control_residual_sd':float(np.sqrt(np.mean(residual**2)))})
for knots in [4,5,6,8,10,15]:
 sp=SplineTransformer(n_knots=knots,degree=3,knots='quantile',include_bias=True)
 # Fit spline basis on controls only; predict counterfactual gains for attendees.
 Bc=sp.fit_transform(y[c,None]); Bt=sp.transform(y[t,None])
 coef=np.linalg.lstsq(Bc,z[c],rcond=None)[0]
 fits.append({'method':'control_cubic_spline','knots':knots,
              'ATT':float(np.mean(z[t]-Bt@coef)),
              'control_residual_sd':float(np.sqrt(np.mean((z[c]-Bc@coef)**2)))})
result['exploratory_standardizations']=fits
np.savetxt(OUT/'complete_data_numeric.csv',np.column_stack([x,y,z]),delimiter=',',header='x,y,z',comments='',fmt='%.17g')
(OUT/'exploration.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
fig,axes=plt.subplots(1,2,figsize=(12,4.4))
for mask,label,color in [(c,'Did not attend','#496a89'),(t,'Attended','#d17d2f')]:
 axes[0].scatter(y[mask],z[mask],s=8,alpha=.35,label=label,color=color)
 axes[1].hist(y[mask],bins=np.arange(0,101,5),alpha=.55,label=label,color=color)
axes[0].set(xlabel='Start-of-term score y',ylabel='Gain z (points)')
axes[1].set(xlabel='Start-of-term score y',ylabel='Number of students')
for a in axes: a.legend(); a.grid(alpha=.15)
fig.tight_layout(); fig.savefig(OUT/'data_overview.png',dpi=160); plt.close(fig)
print('Outputs: exploration.json, complete_data_numeric.csv, data_overview.png; all 2000 rows used.')
