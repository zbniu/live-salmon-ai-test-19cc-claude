import pandas as pd, numpy as np
import statsmodels.formula.api as smf
from scipy import stats
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
rng = np.random.default_rng(20261004)

# 1. Balance check on baseline
print("Baseline balance (Welch t):", stats.ttest_ind(df.y[df.x==1], df.y[df.x==0], equal_var=False))

# 2. Unadjusted difference in means (Neyman SE)
m1, m0 = df.z[df.x==1].mean(), df.z[df.x==0].mean()
se = np.sqrt(df.z[df.x==1].var()/600 + df.z[df.x==0].var()/1400)
print(f"Diff in means: {m1-m0:.4f}  SE {se:.4f}  95% CI [{m1-m0-1.96*se:.4f}, {m1-m0+1.96*se:.4f}]")

# 3. ANCOVA adjusted for baseline (HC2), and Lin (2013) interacted estimator
r1 = smf.ols("z ~ x + y", df).fit(cov_type="HC2"); print(r1.summary().tables[1])
df["yc"] = df.y - df.y.mean()
r2 = smf.ols("z ~ x*yc", df).fit(cov_type="HC2"); print(r2.summary().tables[1])
# ATT version of Lin: center at treated mean of y
df["yt"] = df.y - df.y[df.x==1].mean()
r3 = smf.ols("z ~ x*yt", df).fit(cov_type="HC2"); print("ATT-centred interacted:"); print(r3.summary().tables[1])

# 4. Baseline-z relation by arm (heterogeneity check)
for a in (0,1):
    s = df[df.x==a]; print(f"arm {a}: slope z~y", np.polyfit(s.y, s.z, 1))
# effect by baseline tercile
df["tert"] = pd.qcut(df.y, 3, labels=["low","mid","high"])
print(df.groupby(["tert","x"]).z.agg(["mean","std","count"]).unstack())

# 5. Randomization test (difference in means and ANCOVA coef), 10000 permutations
obs_d = m1-m0; obs_b = r1.params["x"]
X = df.x.values; Z = df.z.values; Y = df.y.values
resid = Z - np.polyval(np.polyfit(Y, Z, 1), Y)
pd_, pb = 0, 0
for _ in range(10000):
    p = rng.permutation(X)
    d = Z[p==1].mean()-Z[p==0].mean()
    b = resid[p==1].mean()-resid[p==0].mean()
    pd_ += abs(d) >= abs(obs_d); pb += abs(b) >= abs(obs_b)
print("Permutation p (diff means):", (pd_+1)/10001, " (residualised):", (pb+1)/10001)

# 6. Distribution: quantile differences
for q in (0.1,0.25,0.5,0.75,0.9):
    print(q, round(np.quantile(Z[X==1],q)-np.quantile(Z[X==0],q),3))
print("Var ratio z (T/C):", df.z[df.x==1].var()/df.z[df.x==0].var(), stats.levene(df.z[df.x==1], df.z[df.x==0]))
