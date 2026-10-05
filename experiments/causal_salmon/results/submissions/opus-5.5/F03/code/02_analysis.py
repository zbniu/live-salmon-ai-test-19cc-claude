import pandas as pd, numpy as np, statsmodels.formula.api as smf
from scipy import stats
rng = np.random.default_rng(20261004)
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
t, c = df[df.x==1], df[df.x==0]

print("== Balance on baseline y ==")
print(f"mean y treated {t.y.mean():.3f}, control {c.y.mean():.3f}, diff {t.y.mean()-c.y.mean():.3f}")
print("Welch t-test y:", stats.ttest_ind(t.y, c.y, equal_var=False))
print("KS test y:", stats.ks_2samp(t.y, c.y))
print(f"SMD y: {(t.y.mean()-c.y.mean())/np.sqrt((t.y.var()+c.y.var())/2):.3f}")

print("\n== (A) Unadjusted difference in mean z ==")
d = t.z.mean()-c.z.mean()
se = np.sqrt(t.z.var()/len(t)+c.z.var()/len(c))
print(f"diff {d:.4f}, Neyman/Welch SE {se:.4f}, 95% CI [{d-1.96*se:.4f}, {d+1.96*se:.4f}]")
print("Welch t-test z:", stats.ttest_ind(t.z, c.z, equal_var=False))

print("\n== (B) ANCOVA: z ~ x + y (HC2) ==")
m1 = smf.ols("z ~ x + y", df).fit(cov_type="HC2"); print(m1.summary().tables[1])

print("\n== (C) Lin (2013) interacted, y centered at TREATED mean -> ATT-targeted (HC2) ==")
df["yc_t"] = df.y - t.y.mean()
m2 = smf.ols("z ~ x * yc_t", df).fit(cov_type="HC2"); print(m2.summary().tables[1])
print("\n   same, y centered at full-sample mean (ATE-targeted)")
df["yc"] = df.y - df.y.mean()
m3 = smf.ols("z ~ x * yc", df).fit(cov_type="HC2"); print(m3.summary().tables[1])

print("\n== Within-arm relation of z with y ==")
for g, dd in df.groupby("x"):
    r = smf.ols("z ~ y", dd).fit(cov_type="HC2")
    print(f"x={g}: slope {r.params['y']:.4f} (SE {r.bse['y']:.4f}), R2 {r.rsquared:.4f}, resid SD {np.sqrt(r.mse_resid):.3f}")
    rq = smf.ols("z ~ y + I(y**2)", dd).fit(cov_type="HC2")
    print(f"     quadratic term p={rq.pvalues['I(y ** 2)']:.3f}")

print("\n== Effect by baseline-y quintile (diff in mean z) ==")
df["q"] = pd.qcut(df.y, 5, labels=False)
for q, dd in df.groupby("q"):
    a, b = dd[dd.x==1].z, dd[dd.x==0].z
    s = np.sqrt(a.var()/len(a)+b.var()/len(b))
    print(f"q{q} y[{dd.y.min():.1f},{dd.y.max():.1f}] nT={len(a)} nC={len(b)} diff {a.mean()-b.mean():.3f} SE {s:.3f}")

print("\n== Distributional checks ==")
print("SD z treated/control:", round(t.z.std(),3), round(c.z.std(),3), " Levene:", stats.levene(t.z, c.z))
print("Median diff:", round(t.z.median()-c.z.median(),4))
for p in [10,25,50,75,90]:
    print(f"  quantile {p}: T {np.percentile(t.z,p):.3f}  C {np.percentile(c.z,p):.3f}  diff {np.percentile(t.z,p)-np.percentile(c.z,p):.3f}")
print("KS test z:", stats.ks_2samp(t.z, c.z))
print("Mann-Whitney z:", stats.mannwhitneyu(t.z, c.z))

print("\n== Randomization (permutation) inference, 10000 draws of 600 of 2000 ==")
z = df.z.values; x = df.x.values; y = df.y.values
X = np.column_stack([np.ones(len(df)), x, y])
def ancova(xx):
    Xp = X.copy(); Xp[:,1] = xx
    return np.linalg.lstsq(Xp, z, rcond=None)[0][1]
obs_d, obs_a = z[x==1].mean()-z[x==0].mean(), ancova(x)
pd_, pa = [], []
for _ in range(10000):
    xx = np.zeros(len(df)); xx[rng.choice(len(df), 600, replace=False)] = 1
    pd_.append(z[xx==1].mean()-z[xx==0].mean()); pa.append(ancova(xx))
pd_, pa = np.array(pd_), np.array(pa)
print(f"diff-in-means obs {obs_d:.4f}, perm two-sided p {(np.sum(np.abs(pd_)>=abs(obs_d))+1)/10001:.5f}, perm SD {pd_.std():.4f}")
print(f"ANCOVA obs {obs_a:.4f}, perm two-sided p {(np.sum(np.abs(pa)>=abs(obs_a))+1)/10001:.5f}, perm SD {pa.std():.4f}")

print("\n== Bootstrap (5000, stratified by arm) for Lin ATT estimate ==")
bs = []
ti, ci = np.where(x==1)[0], np.where(x==0)[0]
for _ in range(5000):
    idx = np.concatenate([rng.choice(ti, len(ti)), rng.choice(ci, len(ci))])
    dd = df.iloc[idx]; tt = dd[dd.x==1]
    yc = dd.y - tt.y.mean()
    Xb = np.column_stack([np.ones(len(dd)), dd.x, yc, dd.x*yc])
    bs.append(np.linalg.lstsq(Xb, dd.z.values, rcond=None)[0][1])
bs = np.array(bs)
print(f"Lin ATT point {m2.params['x']:.4f}; bootstrap SE {bs.std():.4f}; percentile 95% CI [{np.percentile(bs,2.5):.4f}, {np.percentile(bs,97.5):.4f}]")
