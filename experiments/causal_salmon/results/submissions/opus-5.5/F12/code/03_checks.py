"""Diagnostics: (a) continuity of E[z|y,x=0] across the cutoff c (controls above c are
non-candidates; if the design holds, no jump expected); (b) ATT by y-tercile among treated."""
import pandas as pd, numpy as np
import statsmodels.formula.api as smf
df=pd.read_csv("/mnt/user-data/uploads/data.csv")
c=df.loc[df.x==1,'y'].min()
C=df[df.x==0].assign(above=lambda d:(d.y>=c).astype(int), yc=lambda d:d.y-c)
m=smf.ols("z ~ above*yc",data=C).fit(cov_type='HC2')
print("(a) controls only: jump/slope change at c"); print(m.summary().tables[1])
m2=smf.ols("z ~ yc + I(yc**2)",data=C).fit(cov_type='HC2')
print("controls, quadratic over full range, R2=%.3f"%m2.rsquared)
S=df[df.y>=c]; cc=S[S.x==0]
b=np.polyfit(cc.y,cc.z,1)
t=S[S.x==1].assign(eff=lambda d:d.z-np.polyval(b,d.y))
t['tercile']=pd.qcut(t.y,3)
print("\n(b) ATT by y-tercile of treated (linear control fit within y>=c)")
print(t.groupby('tercile',observed=True).eff.agg(['size','mean','sem']).round(3))
