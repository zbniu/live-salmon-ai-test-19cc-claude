"""ATT of arrangement Q on change z.
Design (STUDY_DESCRIPTION s.3): x=1 iff unit is a candidate AND y >= c (c = y of the
600th accepted candidate = min y among treated). Candidacy depends only on y plus
independent random noise, so for y >= c, x is independent of potential outcomes given y,
and every y >= c has positive probability of x=0. => ATT identified by adjusting for y
within the region y >= c."""
import pandas as pd, numpy as np
import statsmodels.formula.api as smf
from patsy import dmatrix
rng = np.random.default_rng(20261004)
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
c = df.loc[df.x==1,'y'].min()
R = df[df.y>=c].copy()

def est_all(d, full):
    out = {}
    r = d[d.y>=d.loc[d.x==1,'y'].min()]
    t = r[r.x==1]; k = r[r.x==0]
    out['naive_diff_all'] = full_diff(d)
    out['ols_additive'] = smf.ols('z ~ x + y', r).fit().params['x']
    # imputation: fit control outcome model, predict for treated
    for name, form, data in [('impute_linear','z ~ y',k),
                             ('impute_cubic','z ~ y + I(y**2) + I(y**3)',k),
                             ('impute_spline_allcontrols','z ~ bs(y, df=6, lower_bound=45, upper_bound=75)', d[d.x==0])]:
        m = smf.ols(form, data).fit()
        out[name] = (t.z - m.predict(t)).mean()
    # 1-NN matching on y with replacement (treated -> controls in region)
    ky = k.y.values; kz = k.z.values; o = np.argsort(ky); ky, kz = ky[o], kz[o]
    idx = np.searchsorted(ky, t.y.values).clip(1, len(ky)-1)
    left = ky[idx-1]; right = ky[idx]
    j = np.where(np.abs(t.y.values-left) <= np.abs(right-t.y.values), idx-1, idx)
    out['nn1_match'] = (t.z.values - kz[j]).mean()
    # 5-NN
    D = np.abs(t.y.values[:,None]-ky[None,:]); nn = np.argsort(D,axis=1)[:,:5]
    out['nn5_match'] = (t.z.values - kz[nn].mean(1)).mean()
    # ATT odds weighting with logistic propensity (cubic in y)
    ps = smf.logit('x ~ y + I(y**2) + I(y**3)', r).fit(disp=0).predict(r)
    w = ps/(1-ps); kk = r.x==0
    out['ipw_att'] = t.z.mean() - np.average(r.z[kk], weights=w[kk])
    # doubly robust (weighted regression on controls) 
    m = smf.wls('z ~ y', r[kk], weights=w[kk]).fit()
    out['dr_att'] = (t.z - m.predict(t)).mean()
    return out

def full_diff(d): return d.z[d.x==1].mean()-d.z[d.x==0].mean()

point = est_all(df, True)
B = 1000; boots = {k:[] for k in point}
for b in range(B):
    s = df.sample(len(df), replace=True, random_state=rng.integers(1e9))
    e = est_all(s, True)
    for k in e: boots[k].append(e[k])
rows=[]
for k,v in point.items():
    bb=np.array(boots[k]); rows.append((k,v,bb.std(ddof=1),np.percentile(bb,2.5),np.percentile(bb,97.5)))
res = pd.DataFrame(rows, columns=['estimator','ATT','boot_se','ci2.5','ci97.5'])
print("cutoff c =",c," n treated =",(R.x==1).sum()," n controls y>=c =",(R.x==0).sum())
print(res.to_string(index=False, float_format='%.3f'))
res.to_csv('results/02_att_estimates.csv', index=False)

# OLS model details & heterogeneity
m1 = smf.ols('z ~ x + y', R).fit(cov_type='HC2'); print(m1.summary().tables[1])
R['yc'] = R.y - R.loc[R.x==1,'y'].mean()
m2 = smf.ols('z ~ x*yc', R).fit(cov_type='HC2'); print(m2.summary().tables[1])
print("ATT (interaction model, coef on x at treated mean y):", m2.params['x'], m2.bse['x'])
# Check control outcome relationship continuity across c (placebo): fit controls below vs above
k = df[df.x==0]
for nm, sub in [('controls y<c',k[k.y<c]),('controls y>=c',k[k.y>=c])]:
    f = smf.ols('z ~ y', sub).fit(); print(nm, 'slope', round(f.params['y'],3), 'int', round(f.params['Intercept'],3), 'resid sd', round(np.sqrt(f.scale),3))
