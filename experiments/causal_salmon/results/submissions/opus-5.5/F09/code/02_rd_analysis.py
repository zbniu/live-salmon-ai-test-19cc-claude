"""Fuzzy regression discontinuity at the acceptance cutoff c = min(y | x=1).
Below c no unit can be treated; above c, x=1 iff the unit was a candidate.
The Wald ratio (jump in E[z|y]) / (jump in P(x=1|y)) identifies the effect of Q
for treated units (= candidates) with baseline at c."""
import pandas as pd, numpy as np
from rdrobust import rdrobust, rdbwselect
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
c = df.loc[df.x==1,'y'].min()
print(f"cutoff c = {c:.4f}")
r = df.y - c
# Assign the boundary unit (y==c, treated) to the right side: rdrobust uses r>=0 as right.
print("\n=== rdrobust fuzzy RD, MSE-optimal bw, triangular, p=1 ===")
fit = rdrobust(y=df.z.values, x=r.values, fuzzy=df.x.values, c=0, p=1, kernel='triangular', bwselect='mserd')
print(fit)
print("coef:", fit.coef.values.ravel(), "\nse:", fit.se.values.ravel(), "\nci:", fit.ci.values)
print("first stage / reduced form via sharp RD:")
fs = rdrobust(y=df.x.values, x=r.values, c=0, h=float(fit.bws.iloc[0,0]), b=float(fit.bws.iloc[1,0]))
rf = rdrobust(y=df.z.values, x=r.values, c=0, h=float(fit.bws.iloc[0,0]), b=float(fit.bws.iloc[1,0]))
print("first stage jump:", fs.coef.values.ravel(), "se", fs.se.values.ravel())
print("reduced form jump:", rf.coef.values.ravel(), "se", rf.se.values.ravel())

# Manual local-linear Wald estimates across bandwidths (uniform kernel) with bootstrap SE
def wald(d, h):
    s = d[(d.r.abs()<=h)]
    def jump(v):
        X = np.column_stack([np.ones(len(s)), s.D, s.r, s.D*s.r])
        b = np.linalg.lstsq(X, s[v].values, rcond=None)[0]; return b[1]
    return jump('z')/jump('x'), jump('x'), jump('z'), len(s)
d = df.assign(r=r, D=(r>=0).astype(float))
rng = np.random.default_rng(20261004)
rows=[]
for h in [3,4,5,6,8,10,12]:
    est, fs_, rf_, n = wald(d,h)
    bs=[wald(d.iloc[rng.integers(0,len(d),len(d))],h)[0] for _ in range(500)]
    rows.append(dict(h=h,n=n,first_stage=fs_,reduced_form=rf_,wald=est,boot_se=np.std(bs,ddof=1)))
tab=pd.DataFrame(rows); print("\n=== manual local-linear Wald, uniform kernel ===\n", tab.round(3).to_string(index=False))
tab.to_csv("results/02_bandwidth_sensitivity.csv", index=False)

print("\n=== rdrobust with p=2 and with uniform kernel ===")
for p,k in [(2,'triangular'),(1,'uniform'),(1,'epanechnikov')]:
    f=rdrobust(y=df.z.values, x=r.values, fuzzy=df.x.values, c=0, p=p, kernel=k)
    print(p,k,"conv coef %.3f se %.3f | robust CI [%.3f, %.3f] | h=%.2f"%(f.coef.values[0,0],f.se.values[0,0],f.ci.values[2,0],f.ci.values[2,1],f.bws.iloc[0,0]))

# Placebo cutoffs (where nothing changes) on z, sharp RD
print("\n=== placebo cutoffs (reduced-form jump in z) ===")
for pc in [50,53,62,66,70]:
    sub = df[(df.y<c) if pc<c else (df.y>=c)]
    if pc>c: sub=sub  # among y>=c only; treatment share smooth there
    f=rdrobust(y=sub.z.values, x=(sub.y-pc).values, c=0)
    print(f"placebo {pc}: jump {f.coef.values[0,0]:.3f}, robust p {f.pv.values[2,0]:.3f}")
