import pandas as pd, numpy as np
from scipy import stats
import statsmodels.formula.api as smf
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("/mnt/user-data/uploads/data.csv")
print("shape", df.shape); print(df.dtypes); print(df.isna().sum())
print(df.describe().T)
print("x counts", df.x.value_counts().to_dict())
print(df.groupby("x")[["y","z"]].agg(["mean","std","median","min","max"]).T)

t, c = df[df.x==1], df[df.x==0]
# Balance on pre-treatment y
print("\n== Balance on y ==")
print(stats.ttest_ind(t.y, c.y, equal_var=False), "diff", t.y.mean()-c.y.mean())
print(stats.ks_2samp(t.y, c.y))

# Primary: difference in means (randomized)
print("\n== Difference in means on z ==")
d = t.z.mean()-c.z.mean()
se = np.sqrt(t.z.var(ddof=1)/len(t)+c.z.var(ddof=1)/len(c))
print(f"diff={d:.4f} se={se:.4f} 95%CI=({d-1.96*se:.4f},{d+1.96*se:.4f})")
print(stats.ttest_ind(t.z, c.z, equal_var=False))
print(stats.mannwhitneyu(t.z, c.z))
# randomization inference
rng = np.random.default_rng(1)
zv = df.z.values; n=len(df); obs=d
perm=[]
for _ in range(10000):
    idx = rng.permutation(n)
    perm.append(zv[idx[:600]].mean()-zv[idx[600:]].mean())
print("randomization p", (np.abs(perm)>=abs(obs)).mean())

# Regression OLS with robust SE
print("\n== OLS z ~ x (HC2) ==")
print(smf.ols("z~x",df).fit(cov_type="HC2").summary().tables[1])
print("\n== OLS z ~ x + y (HC2) ==")
print(smf.ols("z~x+y",df).fit(cov_type="HC2").summary().tables[1])
# Lin interaction estimator
df["yc"]=df.y-df.y.mean()
print("\n== Lin-adjusted: z ~ x + yc + x:yc (HC2) ==")
m=smf.ols("z~x*yc",df).fit(cov_type="HC2"); print(m.summary().tables[1])
# Nonlinearity checks
print("\n== Flexible: z ~ x*(yc+yc^2+yc^3) ==")
m2=smf.ols("z~x*(yc+I(yc**2)+I(yc**3))",df).fit(cov_type="HC2"); print(m2.summary().tables[1])
print("\n== Control group z ~ y relation (does gain depend on y absent treatment?) ==")
print(smf.ols("z~yc+I(yc**2)",c.assign(yc=c.y-df.y.mean())).fit(cov_type="HC2").summary().tables[1])

# Heterogeneity by y quintile
print("\n== Effect by y quintile ==")
df["q"]=pd.qcut(df.y,5,labels=False)
rows=[]
for q,g in df.groupby("q"):
    a,b=g[g.x==1].z,g[g.x==0].z
    dd=a.mean()-b.mean(); s=np.sqrt(a.var(ddof=1)/len(a)+b.var(ddof=1)/len(b))
    rows.append(dict(q=q,ymin=g.y.min(),ymax=g.y.max(),n_t=len(a),n_c=len(b),diff=dd,se=s,lo=dd-1.96*s,hi=dd+1.96*s))
print(pd.DataFrame(rows).round(3).to_string())

# Distribution diagnostics
print("\n== z distribution by arm ==")
print(df.groupby("x").z.describe())
print("skew", df.groupby("x").z.apply(stats.skew).to_dict(), "kurt", df.groupby("x").z.apply(stats.kurtosis).to_dict())
print("Levene", stats.levene(t.z,c.z))
# quantile effects
print("\n== Quantile differences ==")
for qq in [.1,.25,.5,.75,.9]:
    print(qq, round(t.z.quantile(qq)-c.z.quantile(qq),3))
# Bootstrap CI
bs=[]
for _ in range(5000):
    a=t.z.sample(len(t),replace=True,random_state=int(rng.integers(1e9))).mean()
    b=c.z.sample(len(c),replace=True,random_state=int(rng.integers(1e9))).mean()
    bs.append(a-b)
print("bootstrap 95% CI", np.percentile(bs,[2.5,97.5]))

fig,ax=plt.subplots(1,3,figsize=(15,4))
for k,g in df.groupby("x"): ax[0].hist(g.z,bins=40,alpha=.5,label=f"x={k}",density=True)
ax[0].legend(); ax[0].set_title("z by arm")
for k,g in df.groupby("x"): ax[1].hist(g.y,bins=40,alpha=.5,label=f"x={k}",density=True)
ax[1].legend(); ax[1].set_title("y by arm")
for k,g in df.groupby("x"): ax[2].scatter(g.y,g.z,s=3,alpha=.4,label=f"x={k}")
ax[2].legend(); ax[2].set_title("z vs y")
plt.tight_layout(); plt.savefig("results/diagnostics.png",dpi=100)
