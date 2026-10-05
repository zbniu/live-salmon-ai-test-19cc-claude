import csv, json, math
import numpy as np
from scipy import stats
from pathlib import Path
p=Path('upload/data(20261004-071234).csv')
with p.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
a=np.array([[float(r[k]) for k in ('x','y','z')] for r in rows])
x,y,z=a.T
assert a.shape==(2000,3) and set(x)=={0,1} and np.isfinite(a).all()
t=z[x==1]; c=z[x==0]
d=t.mean()-c.mean(); se=math.sqrt(t.var(ddof=1)/len(t)+c.var(ddof=1)/len(c))
df=(t.var(ddof=1)/len(t)+c.var(ddof=1)/len(c))**2/((t.var(ddof=1)/len(t))**2/(len(t)-1)+(c.var(ddof=1)/len(c))**2/(len(c)-1))
ci=stats.t.interval(.95, df, loc=d, scale=se)
out={
 'n':len(x),'n_attended':int(x.sum()),'n_control':int((1-x).sum()),
 'mean_gain_attended':float(t.mean()),'mean_gain_control':float(c.mean()),
 'difference_in_mean_gain':float(d),'welch_se':float(se),'welch_df':float(df),
 'welch_95pct_ci':[float(v) for v in ci], 'welch_two_sided_p':float(2*stats.t.sf(abs(d/se),df)),
 'baseline_mean_attended':float(y[x==1].mean()),'baseline_mean_control':float(y[x==0].mean()),
 'baseline_difference':float(y[x==1].mean()-y[x==0].mean()),
 'gain_sd_attended':float(t.std(ddof=1)),'gain_sd_control':float(c.std(ddof=1))
}
Path('submission/results/analysis.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
