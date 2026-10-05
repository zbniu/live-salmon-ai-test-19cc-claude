"""Estimate the effect of Q for treated units, adjusting for baseline y."""
import csv, json
from pathlib import Path
import numpy as np
from scipy.interpolate import BSpline
from scipy.spatial import cKDTree

SOURCE=Path('upload/data(20261004-071320).csv')
OUT=Path('submission/results')
with SOURCE.open(newline='',encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
assert len(rows)==2000 and set(rows[0])=={'x','y','z'}
a=np.array([[float(r[k]) for k in ('x','y','z')] for r in rows])
assert np.isfinite(a).all() and set(a[:,0])=={0.,1.}
x,y,z=a.T
tr=x==1; co=~tr
assert tr.sum()==600

# Fixed knots/boundaries allow the same basis for controls and treated, including bootstrap samples.
def design(v, df):
    # Cubic B-splines with fixed, evenly spaced internal knots.
    knots=np.r_[[45.]*4, np.linspace(45.,75.,df-2)[1:-1], [75.]*4]
    return BSpline.design_matrix(v, knots, 3).toarray()

def att_regression(y1,z1,y0,z0,df=5):
    fit=np.linalg.lstsq(design(y0,df),z0,rcond=None)[0]
    return float(np.mean(z1-design(y1,df)@fit))

# ATT counterfactual: fit E[z(0)|y] on untreated units, predict it for all 600 treated.
primary=att_regression(y[tr],z[tr],y[co],z[co])
rng=np.random.default_rng(20261004)
y1,z1=y[tr],z[tr]; y0,z0=y[co],z[co]
bootstrap=[]
for b in range(2000):
    i=rng.integers(len(y1),size=len(y1))
    j=rng.integers(len(y0),size=len(y0))
    bootstrap.append(att_regression(y1[i],z1[i],y0[j],z0[j]))
boot=np.array(bootstrap)

# Alternative smoothness choices and direct matching within the overlapping y range.
alternatives={f'control_spline_df_{d}':att_regression(y1,z1,y0,z0,d) for d in (4,6,8)}
for d in (1,2,3):
    # Centered polynomial regression on controls, evaluated on treated baselines.
    A=lambda v:np.stack([((v-60)/10)**k for k in range(d+1)],axis=1)
    beta=np.linalg.lstsq(A(y0),z0,rcond=None)[0]
    alternatives[f'control_polynomial_degree_{d}']=float(np.mean(z1-A(y1)@beta))
# Nearest-baseline untreated matches with replacement, 5 neighbors per treated unit.
tree=cKDTree(y0[:,None]); dist,indices=tree.query(y1[:,None],k=5)
alternatives['five_nearest_controls']=float(np.mean(z1-z0[indices].mean(axis=1)))

# Counts and distances for overlap, including the upper treated tail.
nearest=dist[:,0]
overlap={'control_count_within_treated_y_range':int(((y0>=y1.min())&(y0<=y1.max())).sum()),
         'treated_y_range':[float(y1.min()),float(y1.max())],
         'control_y_range':[float(y0.min()),float(y0.max())],
         'nearest_control_distance_median':float(np.median(nearest)),
         'nearest_control_distance_95th_percentile':float(np.quantile(nearest,.95)),
         'nearest_control_distance_max':float(nearest.max())}

result={'question_estimand':'Average change caused by Q among the 600 units that received Q (ATT), in points',
        'primary_estimate':primary,'primary_method':'Mean treated z minus predicted untreated z at each treated y; cubic B-spline regression of z on y using 1,400 controls, df=5',
        'predicted_untreated_change_for_treated':float(z1.mean()-primary),
        'observed_treated_change':float(z1.mean()),
        'bootstrap_standard_error':float(boot.std(ddof=1)),
        'bootstrap_percentile_95_interval':boot.quantile([.025,.975]).tolist() if hasattr(boot,'quantile') else np.quantile(boot,[.025,.975]).tolist(),
        'bootstrap_replicates':len(boot), 'bootstrap_seed':20261004,
        'unadjusted_treated_minus_control':float(z1.mean()-z0.mean()),
        'alternative_estimates':alternatives,'overlap':overlap}
OUT.joinpath('analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
