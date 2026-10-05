"""Descriptive comparisons (NOT causal answers) and a check for selection on unrecorded factors."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
from rdrobust import rdrobust
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
c = df.loc[df.x==1,'y'].min(); df['r']=df.y-c
print("Naive difference in mean z (treated - untreated): %.3f" % (df[df.x==1].z.mean()-df[df.x==0].z.mean()))
m = smf.ols("z ~ x + y", df).fit(cov_type='HC1'); print("OLS z~x+y (all):  x=%.3f se %.3f" % (m.params.x, m.bse.x))
a = df[df.y>=c]
m2 = smf.ols("z ~ x + y", a).fit(cov_type='HC1'); print("OLS z~x+y (y>=c): x=%.3f se %.3f" % (m2.params.x, m2.bse.x))
m3 = smf.ols("z ~ x*r", a).fit(cov_type='HC1'); print("OLS z~x*r (y>=c): x at c=%.3f se %.3f, x:r=%.3f se %.3f" % (m3.params.x,m3.bse.x,m3.params['x:r'],m3.bse['x:r']))
print("\nSlope of z on y: below c (all untreated) %.3f; above c treated %.3f; above c untreated %.3f" % (
    smf.ols("z~y",df[df.y<c]).fit().params.y, smf.ols("z~y",a[a.x==1]).fit().params.y, smf.ols("z~y",a[a.x==0]).fit().params.y))
# Selection check at c: untreated above c are non-candidates; units just below c are a mix.
# If candidacy (driven partly by unrecorded factors) were related to untreated change, these would differ.
sub = pd.concat([df[df.y<c], a[a.x==0]])
f = rdrobust(y=sub.z.values, x=sub.r.values, c=0)
print("\nJump at c in E[z] comparing all units below c with NON-candidates (x=0) above c: %.3f, robust CI [%.3f, %.3f], h=%.2f"
      % (f.coef.values[0,0], f.ci.values[2,0], f.ci.values[2,1], f.bws.iloc[0,0]))
# Treated just above c vs all just below c
sub2 = pd.concat([df[df.y<c], a[a.x==1]])
f2 = rdrobust(y=sub2.z.values, x=sub2.r.values, c=0)
print("Jump at c comparing all below c with TREATED above c: %.3f, robust CI [%.3f, %.3f]" % (f2.coef.values[0,0], f2.ci.values[2,0], f2.ci.values[2,1]))
