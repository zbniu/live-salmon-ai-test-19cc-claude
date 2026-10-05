import csv, json
import numpy as np
from scipy.stats import binned_statistic
from pathlib import Path
p=Path('upload/data(20261004-071320).csv')
with p.open(newline='') as f: rows=list(csv.DictReader(f))
a=np.array([[float(r[k]) for k in ('x','y','z')] for r in rows])
x,y,z=a.T
out={'n':len(a),'missing':int(np.isnan(a).sum()),'treated':int(sum(x==1)),'control':int(sum(x==0)),
     'group_summaries':{str(g):{'y_mean':float(y[x==g].mean()),'y_range':[float(y[x==g].min()),float(y[x==g].max())],
        'z_mean':float(z[x==g].mean()),'z_sd':float(z[x==g].std(ddof=1))} for g in (0,1)},
     'bins':[]}
for lo in range(0,100,5):
  m=(y>=lo)&(y<lo+5)
  out['bins'].append({'y':f'{lo}-{lo+5}','n1':int(sum(m&(x==1))),'n0':int(sum(m&(x==0))),
    'z1':float(z[m&(x==1)].mean()) if sum(m&(x==1)) else None,
    'z0':float(z[m&(x==0)].mean()) if sum(m&(x==0)) else None})
Path('submission/results/exploration.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
