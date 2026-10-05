"""Diagnostics: decomposition of the naive treated-untreated gap at c, placebo cutoffs,
density of y, and (confounded, for comparison only) regression estimates above c."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
from rdrobust import rdrobust
from rddensity import rddensity
d = pd.read_csv('/mnt/user-data/uploads/data.csv')
c = d.loc[d.x==1,'y'].min(); d['r']=d.y-c; d['D']=(d.r>=0).astype(int)
def ll_at0(s, side, h):
    s = s[(s.r.abs()<=h) & ((s.r>=0) if side=='R' else (s.r<0))]
    w = 1 - s.r.abs()/h
    m = smf.wls('z ~ r', s, weights=w).fit(cov_type='HC1'); return m.params['Intercept'], m.bse['Intercept'], len(s)
print("cutoff", c)
for h in (3,5,7.5,10):
    L,_,nL = ll_at0(d,'L',h); T,_,nT = ll_at0(d[d.x==1],'R',h); U,_,nU = ll_at0(d[d.x==0],'R',h)
    pi = d[(d.r>=0)&(d.r<=h)].x.mean()   # crude share treated just above (first stage ~ local share)
    pi_ll = rdrobust(d.x, d.y, c=c, h=h).coef.values[0,0]
    z0_cand = (L - (1-pi_ll)*U)/pi_ll       # implied E[z(0) | candidate, y=c]
    print(f"h={h}: E[z|c-]={L:.2f} (n={nL}); E[z|treated,c+]={T:.2f} (n={nT}); E[z|untreated,c+]={U:.2f} (n={nU}); "
          f"P(cand|c)={pi_ll:.3f}; naive gap at c={T-U:.2f}; implied E[z0|cand,c]={z0_cand:.2f}; "
          f"implied effect at c={T-z0_cand:.2f}; implied selection bias at c={z0_cand-U:.2f}")

print("\n=== Jump at c among UNTREATED only (composition: above c untreated = non-candidates) ===")
r = rdrobust(d.loc[d.x==0,'z'], d.loc[d.x==0,'y'], c=c); print(r.coef.T, r.ci)

print("\n=== Placebo cutoffs (sharp RD on z, using only one side of the true cutoff) ===")
rows=[]
for pc in (49,51,53):
    s = d[d.y<c]; r = rdrobust(s.z, s.y, c=pc); rows.append(('below', pc, r.coef.values[0,0], *r.ci.values[2]))
for pc in (60,63,66,69):
    s = d[d.y>=c]; r = rdrobust(s.z, s.y, c=pc, fuzzy=s.x) if False else rdrobust(s.z, s.y, c=pc)
    rf = rdrobust(s.x, s.y, c=pc); rows.append(('above(z)', pc, r.coef.values[0,0], *r.ci.values[2]))
    rows.append(('above(x)', pc, rf.coef.values[0,0], *rf.ci.values[2]))
pl = pd.DataFrame(rows, columns=['side','placebo_c','jump','rob_ci_lo','rob_ci_hi']); print(pl.round(3).to_string())
pl.to_csv('results/03_placebo.csv', index=False)

print("\n=== Density test of y at c (rddensity) ===")
try:
    dt = rddensity(X=d.y.values, c=c); print(dt)
except Exception as e: print("rddensity error:", repr(e))

print("\n=== For comparison only (CONFOUNDED by unrecorded circumstances): OLS among y>=c ===")
a = d[d.y>=c]
for f in ('z ~ x', 'z ~ x + y', 'z ~ x + y + I(y**2)', 'z ~ x*y'):
    m = smf.ols(f, a).fit(cov_type='HC1'); print(f, " coef x =", round(m.params['x'],3), " se =", round(m.bse['x'],3))
m = smf.ols('z ~ x + y', d).fit(cov_type='HC1'); print("all units z ~ x + y: coef x =", round(m.params['x'],3), round(m.bse['x'],3))
print("raw difference in means:", round(d[d.x==1].z.mean()-d[d.x==0].z.mean(),3))
