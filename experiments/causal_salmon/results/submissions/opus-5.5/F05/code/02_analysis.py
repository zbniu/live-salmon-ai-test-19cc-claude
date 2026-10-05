import pandas as pd, numpy as np
import statsmodels.formula.api as smf
from scipy import stats
rng = np.random.default_rng(20261004)
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
t, c = df[df.x==1], df[df.x==0]

# Balance
print("== Balance on baseline y ==")
print("mean diff y (T-C):", t.y.mean()-c.y.mean(), stats.ttest_ind(t.y, c.y, equal_var=False))
print("KS y:", stats.ks_2samp(t.y, c.y))

# 1. Difference in means (Welch)
d = t.z.mean()-c.z.mean()
se = np.sqrt(t.z.var()/len(t)+c.z.var()/len(c))
print("\n== Difference in means of z ==")
print(f"est={d:.4f} se={se:.4f} 95%CI=({d-1.96*se:.4f},{d+1.96*se:.4f})", stats.ttest_ind(t.z, c.z, equal_var=False))

# 2. ANCOVA, HC2
m2 = smf.ols("z ~ x + y", df).fit(cov_type="HC2")
print("\n== ANCOVA z ~ x + y (HC2) ==\n", m2.summary().tables[1])

# 3. Lin (2013) interacted, centred at treated-group mean of y -> ATT-targeted
df["yc_t"] = df.y - t.y.mean()
m3 = smf.ols("z ~ x * yc_t", df).fit(cov_type="HC2")
print("\n== Interacted, y centred at treated mean (ATT) HC2 ==\n", m3.summary().tables[1])
df["yc_all"] = df.y - df.y.mean()
m3b = smf.ols("z ~ x * yc_all", df).fit(cov_type="HC2")
print("\n== Interacted, y centred at full-sample mean (ATE) HC2 ==\n", m3b.summary().tables[1])

# Nonlinearity checks
m4 = smf.ols("z ~ x * (y + I(y**2))", df).fit(cov_type="HC2")
print("\n== Quadratic interacted ==\n", m4.summary().tables[1])
for g, s in [("C", c), ("T", t)]:
    print(g, "corr(y,z)=", np.corrcoef(s.y, s.z)[0,1])

# ATT by imputation: fit control-model z~f(y), predict for treated
for form in ["z ~ y", "z ~ y + I(y**2) + I(y**3)"]:
    mc = smf.ols(form, c).fit()
    att = (t.z - mc.predict(t)).mean()
    print(f"\nImputation ATT ({form}): {att:.4f}")

# Bootstrap for imputation ATT (linear) and diff-in-means
B=2000; bs=[]
for b in range(B):
    tb = t.sample(len(t), replace=True, random_state=rng.integers(1e9))
    cb = c.sample(len(c), replace=True, random_state=rng.integers(1e9))
    mc = smf.ols("z ~ y", cb).fit()
    bs.append((tb.z - mc.predict(tb)).mean())
bs=np.array(bs); print("bootstrap imputation ATT se:", bs.std(ddof=1), "pct CI:", np.percentile(bs,[2.5,97.5]))

# Randomization (permutation) test of sharp null on diff in means and ANCOVA coefficient
obs = m2.params["x"]; perm=[]
X = df.x.values.copy()
yv, zv = df.y.values, df.z.values
A = np.column_stack([np.ones(len(df)), X, yv])
for i in range(5000):
    xp = rng.permutation(X)
    A[:,1]=xp
    perm.append(np.linalg.lstsq(A, zv, rcond=None)[0][1])
perm=np.array(perm)
print("\nPermutation p (ANCOVA coef, two-sided):", (np.abs(perm)>=abs(obs)).mean())

# Heterogeneity by baseline quintile
df["q"] = pd.qcut(df.y, 5, labels=False)
print("\n== Diff in means by baseline quintile ==")
for q, s in df.groupby("q"):
    a, b_ = s[s.x==1].z, s[s.x==0].z
    print(q, f"y[{s.y.min():.1f},{s.y.max():.1f}] nT={len(a)} nC={len(b_)} diff={a.mean()-b_.mean():.3f} se={np.sqrt(a.var()/len(a)+b_.var()/len(b_)):.3f}")

# Distributional: quantile differences, variance
print("\nVar z T/C:", t.z.var(), c.z.var(), stats.levene(t.z, c.z))
for p in [0.1,0.25,0.5,0.75,0.9]:
    print(f"q{p}: T-C = {t.z.quantile(p)-c.z.quantile(p):.3f}")
# residual sd ratio after y
rT = smf.ols("z~y",t).fit().resid.std(); rC = smf.ols("z~y",c).fit().resid.std()
print("resid sd T, C:", rT, rC)
