"""Observed summaries and logical bounds for the treated-unit average effect."""
import json
import numpy as np
import pandas as pd
from scipy import stats

D=pd.read_csv('upload/data(20261004-071351).csv')
assert D.shape==(2000,3) and list(D)==['x','y','z'] and not D.isna().any().any()
assert (D.x==1).sum()==600
T=D.loc[D.x==1]
C=D.loc[D.x==0]
follow=T.y+T.z
# For every treated unit, its unobserved control follow-up can lie in [0,100].
# Hence z(0) lies in [-y,100-y], and ATT = E[z(1)-z(0)|x=1].
lo=float((T.z+T.y-100).mean())
hi=float((T.z+T.y).mean())
raw=float(T.z.mean()-C.z.mean())
se=float(np.sqrt(T.z.var(ddof=1)/len(T)+C.z.var(ddof=1)/len(C)))
# The following are *feasibility witnesses*, not fitted causal effects.
# Taking z(0)=z(1)-delta for treated units leaves every observed value unchanged.
examples={str(delta):bool(((follow-delta)>=0).all() and ((follow-delta)<=100).all()) for delta in [-3,0,3,5]}
result={
 'rows':len(D),'treated':len(T),'untreated':len(C),
 'treated_mean_baseline':float(T.y.mean()),
 'untreated_mean_baseline':float(C.y.mean()),
 'treated_mean_change':float(T.z.mean()),
 'untreated_mean_change':float(C.z.mean()),
 'observed_mean_change_difference':raw,
 'observed_difference_welch_standard_error':se,
 'observed_difference_welch_approx_95pct_interval':[raw-1.96*se,raw+1.96*se],
 'treated_minimum_baseline':float(T.y.min()),
 'untreated_above_treated_minimum_baseline':int((C.y>=T.y.min()).sum()),
 'treated_mean_observed_followup':float(follow.mean()),
 'ATT_logical_lower_bound':lo,'ATT_logical_upper_bound':hi,
 'treated_counterfactual_examples_feasible':examples,
 'missing_records':int(D.isna().sum().sum())
}
with open('submission/results/02_identification.json','w',encoding='utf-8') as f:
 json.dump(result,f,indent=2,allow_nan=False)
print(json.dumps(result,indent=2))
