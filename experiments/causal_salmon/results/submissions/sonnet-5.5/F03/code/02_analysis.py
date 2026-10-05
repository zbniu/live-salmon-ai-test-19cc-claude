import pandas as pd, numpy as np
import statsmodels.formula.api as smf
from scipy import stats
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
t, c = df[df.x==1], df[df.x==0]
print("== Balance on baseline y (randomization check) ==")
print("mean y treat/control:", t.y.mean(), c.y.mean())
print(stats.ttest_ind(t.y, c.y, equal_var=False))
print(stats.ks_2samp(t.y, c.y))

print("\n== Unadjusted difference in means (Neyman, Welch) ==")
d = t.z.mean()-c.z.mean()
se = np.sqrt(t.z.var(ddof=1)/len(t)+c.z.var(ddof=1)/len(c))
print(f"diff={d:.4f} se={se:.4f} 95%CI=({d-1.96*se:.4f},{d+1.96*se:.4f})")
print(stats.ttest_ind(t.z, c.z, equal_var=False))

print("\n== OLS z ~ x, HC2 ==")
m0 = smf.ols("z~x", df).fit(cov_type="HC2"); print(m0.summary().tables[1])

print("\n== Covariate-adjusted z ~ x + y, HC2 ==")
m1 = smf.ols("z~x+y", df).fit(cov_type="HC2"); print(m1.summary().tables[1]); print(m1.conf_int().loc["x"].values)

print("\n== Lin (2013) interacted, centered y ==")
df["yc"] = df.y-df.y.mean()
m2 = smf.ols("z~x*yc", df).fit(cov_type="HC2"); print(m2.summary().tables[1]); print("ATE CI", m2.conf_int().loc["x"].values)

print("\n== Heterogeneity: quartile of y ==")
df["yq"] = pd.qcut(df.y,4,labels=False)
for q,g in df.groupby("yq"):
    a,b = g[g.x==1].z, g[g.x==0].z
    dd=a.mean()-b.mean(); s=np.sqrt(a.var(ddof=1)/len(a)+b.var(ddof=1)/len(b))
    print(q, round(g.y.min(),1), round(g.y.max(),1), len(a), len(b), f"diff={dd:.3f} se={s:.3f}")
print("Nonlinear check: z~x*(y+y^2)")
m3 = smf.ols("z~x*(yc+I(yc**2))", df).fit(cov_type="HC2"); print(m3.summary().tables[1])
print("Wald interaction terms:", m3.wald_test("x:yc=0, x:I(yc ** 2)=0", scalar=True))

print("\n== Residual checks for model z~x+y ==")
r = m1.resid
print("resid sd by arm:", r[df.x==1].std(), r[df.x==0].std(), "skew",stats.skew(r),"kurt",stats.kurtosis(r))
print("Levene z by arm:", stats.levene(t.z, c.z))
print("Nonlinearity in y for control, quadratic term:")
print(smf.ols("z~yc+I(yc**2)", df[df.x==0]).fit(cov_type="HC2").summary().tables[1])

print("\n== Randomization (permutation) inference, unadjusted, 20000 perms ==")
rng = np.random.default_rng(1); z=df.z.values; n1=600
obs=d; cnt=0; N=20000
for _ in range(N):
    idx=rng.permutation(len(z)); s=z[idx[:n1]].mean()-z[idx[n1:]].mean()
    cnt+= abs(s)>=abs(obs)
print("perm p =", (cnt+1)/(N+1))

print("\n== Bootstrap CI of adjusted & unadjusted effect (2000 reps) ==")
bs0=[];bs1=[]
for _ in range(2000):
    s=df.sample(len(df),replace=True,random_state=int(rng.integers(1e9)))
    bs0.append(s[s.x==1].z.mean()-s[s.x==0].z.mean())
    X=np.column_stack([np.ones(len(s)),s.x,s.y]); bs1.append(np.linalg.lstsq(X,s.z.values,rcond=None)[0][1])
print("unadj", np.percentile(bs0,[2.5,97.5]), "adj", np.percentile(bs1,[2.5,97.5]))
