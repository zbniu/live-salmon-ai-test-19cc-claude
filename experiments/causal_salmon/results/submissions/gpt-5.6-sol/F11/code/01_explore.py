from pathlib import Path
import json
import platform
import numpy as np
import pandas as pd
import scipy
import statsmodels.api as sm
import sklearn
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1]
d = pd.read_csv(root / 'inputs/data.csv')
assert d.shape == (2000, 3) and list(d.columns) == ['x', 'y', 'z']
assert d.notna().all().all() and set(d.x.unique()) == {0, 1}
print('VERSIONS', platform.python_version(), np.__version__, pd.__version__, scipy.__version__, sklearn.__version__)
print('COMPLETE DATA', d.shape, 'missing', int(d.isna().sum().sum()), 'duplicate rows', int(d.duplicated().sum()))
s = d.groupby('x').agg(n=('z','size'), y_min=('y','min'), y_max=('y','max'), y_mean=('y','mean'), z_mean=('z','mean'), z_sd=('z','std'))
print(s.to_string())
s.to_csv(root / 'results/group_summary.csv')
edges = np.linspace(d.y.min()-1e-8, d.y.max()+1e-8, 21)
d['bin'] = pd.cut(d.y, edges)
b = d.groupby(['bin','x'], observed=False).agg(n=('z','size'),y_mean=('y','mean'),z_mean=('z','mean'),z_sd=('z','std')).reset_index()
print('BINS\n', b.to_string(index=False))
b.to_csv(root / 'results/starting_score_bins.csv',index=False)
t=d[d.x==1]; c=d[d.x==0]
print('Treated outside control y range', int(((t.y<c.y.min()) | (t.y>c.y.max())).sum()))
print('Controls above min treated', int((c.y>=t.y.min()).sum()))
print('TREATED Y QUANTILES', t.y.quantile([0,.01,.1,.25,.5,.75,.9,.99,1]).to_dict())
print('CONTROL Y QUANTILES', c.y.quantile([0,.01,.1,.25,.5,.75,.9,.99,1]).to_dict())
for deg in [1,2,3,4,5]:
    yc=(d.y-50)/10
    X=np.column_stack([np.ones(len(d)),d.x]+[yc**i for i in range(1,deg+1)])
    fit=sm.OLS(d.z,X).fit(cov_type='HC3')
    print('Additive polynomial degree',deg,'treatment',fit.params.iloc[1], 'SE',fit.bse.iloc[1], 'R2',fit.rsquared)
fig,axs=plt.subplots(1,2,figsize=(12,4))
for x, color, label in [(0,'#3977a3','Did not attend'),(1,'#d47a28','Attended')]:
    a=d[d.x==x]
    axs[0].scatter(a.y,a.z,s=7,alpha=.3,color=color,label=label)
    axs[1].hist(a.y,bins=edges,alpha=.5,color=color,label=label)
axs[0].set(xlabel='Starting score y',ylabel='Score gain z (points)')
axs[1].set(xlabel='Starting score y',ylabel='Student count')
for ax in axs: ax.legend()
fig.tight_layout(); fig.savefig(root/'results/raw_data_and_overlap.png',dpi=180)
print('Outputs: group_summary.csv, starting_score_bins.csv, raw_data_and_overlap.png')
