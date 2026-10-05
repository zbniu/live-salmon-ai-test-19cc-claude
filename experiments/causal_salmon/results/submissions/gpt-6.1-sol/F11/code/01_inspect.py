"""Inspect every row of the supplied dataset; no filtering or external data."""
from pathlib import Path
import hashlib, json, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[2]
source = root / 'upload/data(20261004-180818).csv'
out = root / 'submission/results'
df = pd.read_csv(source)
assert df.shape == (2000, 3)
assert list(df.columns) == ['x', 'y', 'z']
assert not df.isna().any().any()
assert set(df.x.unique()) == {0, 1}
assert np.isfinite(df.to_numpy()).all()
summary = df.groupby('x').agg(n=('z','size'), mean_y=('y','mean'), sd_y=('y','std'),
    min_y=('y','min'), max_y=('y','max'), mean_z=('z','mean'), sd_z=('z','std'))
summary.to_csv(out / 'group_summary.csv')
bins = np.arange(np.floor(df.y.min()/2)*2, np.ceil(df.y.max()/2)*2+2, 2)
df.assign(y_bin=pd.cut(df.y,bins,include_lowest=True)).groupby(['y_bin','x'], observed=False).agg(
    n=('z','size'), mean_z=('z','mean')).to_csv(out/'score_bins.csv')
treated = df[df.x==1]; controls=df[df.x==0]
nearest = np.min(np.abs(treated.y.to_numpy()[:,None]-controls.y.to_numpy()[None,:]), axis=1)
validation = {'n_rows':len(df),'n_treated':len(treated),'n_control':len(controls),
 'missing_values':int(df.isna().sum().sum()),'unique_y':int(df.y.nunique()),
 'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'treated_outside_observed_control_range':int(((treated.y<controls.y.min())|(treated.y>controls.y.max())).sum()),
 'nearest_control_score_distance_quantiles':dict(zip(['min','median','p90','p99','max'],map(float,np.quantile(nearest,[0,.5,.9,.99,1])))),
 'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__}
(out/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
print(summary.to_string())
print(json.dumps(validation,indent=2))
print((out/'score_bins.csv').read_text())
fig, ax=plt.subplots(1,2,figsize=(12,4))
for x,color,label in [(0,'#4063A3','Did not attend'),(1,'#C35C2E','Attended')]:
 d=df[df.x==x]
 ax[0].scatter(d.y,d.z,s=8,alpha=.35,c=color,label=label)
 ax[1].hist(d.y,bins=bins,alpha=.5,color=color,label=label)
ax[0].set(xlabel='Starting score y',ylabel='Score gain z (points)')
ax[1].set(xlabel='Starting score y',ylabel='Students')
for a in ax: a.legend()
fig.tight_layout();fig.savefig(out/'data_diagnostics.png',dpi=160)
