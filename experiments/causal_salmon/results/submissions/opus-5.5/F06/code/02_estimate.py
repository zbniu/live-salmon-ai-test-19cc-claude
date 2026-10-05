"""02_estimate.py - estimate the effect of tutoring on score gain z among attendees (ATT).

Estimators:
 A. Unadjusted difference in means (Welch / HC2 SE).
 B. ANCOVA: z ~ x + y (HC2 SE).
 C. Fully interacted regression (Lin 2013): z ~ x + (y - ybar_treated) + x*(y - ybar_treated);
    centring y at the treated-group mean makes the x coefficient the sample ATT.
 D. Regression imputation ATT: fit z ~ f(y) on controls, predict for treated, average
    (observed - predicted) over treated; f linear and cubic. Bootstrap SE.
Also: heterogeneity by y, linearity checks, Fisher randomization test, bootstrap CIs.
"""
import numpy as np
import pandas as pd
from scipy import stats

rng = np.random.default_rng(20261004)
OUT = "/home/claude/submission/results/02_estimate.txt"
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
x = df.x.values.astype(float); y = df.y.values; z = df.z.values
n = len(df); t = x == 1; c = ~t
lines = []; p = lines.append


def ols(X, yv, hc="HC2"):
    X = np.asarray(X, float)
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ yv
    e = yv - X @ b
    h = np.einsum("ij,jk,ik->i", X, XtXi, X)
    w = e**2 / (1 - h) if hc == "HC2" else e**2
    V = XtXi @ (X.T * w) @ X @ XtXi
    return b, np.sqrt(np.diag(V)), e


def fmt(name, est, se, dof=None):
    zc = stats.t.ppf(0.975, dof) if dof else 1.959964
    return f"{name}: estimate = {est:.4f}, SE = {se:.4f}, 95% CI = [{est-zc*se:.4f}, {est+zc*se:.4f}], p = {2*(1-stats.norm.cdf(abs(est/se))):.2e}"

results = {}
# A. difference in means
dm = z[t].mean() - z[c].mean()
se_dm = np.sqrt(z[t].var(ddof=1)/t.sum() + z[c].var(ddof=1)/c.sum())
p(fmt("A. Difference in means", dm, se_dm)); results["A_diff_means"] = (dm, se_dm)

# B. ANCOVA
b, se, _ = ols(np.column_stack([np.ones(n), x, y]), z)
p(fmt("B. ANCOVA z ~ x + y (HC2)", b[1], se[1]) + f"; slope on y = {b[2]:.4f} (SE {se[2]:.4f})")
results["B_ancova"] = (b[1], se[1])

# C. Lin interacted, centred at treated mean -> sample ATT
yc = y - y[t].mean()
b, se, _ = ols(np.column_stack([np.ones(n), x, yc, x*yc]), z)
p(fmt("C. Interacted (centred at treated mean of y) -> ATT (HC2)", b[1], se[1]))
p(f"   control slope on y = {b[2]:.4f} (SE {se[2]:.4f}); treated-minus-control slope = {b[3]:.4f} (SE {se[3]:.4f}, p = {2*(1-stats.norm.cdf(abs(b[3]/se[3]))):.2e})")
results["C_lin_att"] = (b[1], se[1])
# same, centred at full-sample mean -> sample ATE (for comparison)
yc2 = y - y.mean()
b2, se2, _ = ols(np.column_stack([np.ones(n), x, yc2, x*yc2]), z)
p(fmt("C'. Interacted (centred at full-sample mean) -> ATE (HC2)", b2[1], se2[1]))
results["C2_lin_ate"] = (b2[1], se2[1])


# D. regression imputation ATT
def att_impute(xa, ya, za, deg):
    tt = xa == 1; cc = ~tt
    coef = np.polyfit(ya[cc], za[cc], deg)
    return np.mean(za[tt] - np.polyval(coef, ya[tt]))

for deg in (1, 3):
    est = att_impute(x, y, z, deg)
    boots = np.empty(2000)
    for i in range(2000):
        # stratified bootstrap keeps 600/1400 split
        it = rng.choice(np.where(t)[0], t.sum()); ic = rng.choice(np.where(c)[0], c.sum())
        idx = np.concatenate([it, ic])
        boots[i] = att_impute(x[idx], y[idx], z[idx], deg)
    bse = boots.std(ddof=1)
    p(fmt(f"D. Imputation ATT, control model poly deg {deg} (bootstrap SE, B=2000)", est, bse)
      + f"; percentile CI = [{np.percentile(boots,2.5):.4f}, {np.percentile(boots,97.5):.4f}]")
    results[f"D_impute_deg{deg}"] = (est, bse)

# Linearity check in controls & treated: compare deg 1 vs 3 via F test
p("")
p("Linearity of E[z|y] within each arm (F test cubic vs linear):")
for name, m in (("control", c), ("treated", t)):
    r1 = np.sum((z[m] - np.polyval(np.polyfit(y[m], z[m], 1), y[m]))**2)
    r3 = np.sum((z[m] - np.polyval(np.polyfit(y[m], z[m], 3), y[m]))**2)
    dfd = m.sum() - 4
    F = ((r1 - r3)/2) / (r3/dfd)
    p(f"  {name}: F(2,{dfd}) = {F:.3f}, p = {1-stats.f.cdf(F,2,dfd):.4f}; linear fit: {np.polyfit(y[m], z[m], 1)}")

# Heterogeneity: effect by quintile of y (difference in means and ANCOVA within bin)
p("")
p("Effect by quintile of start-of-term score y (within-bin difference in means):")
q = pd.qcut(df.y, 5, labels=False)
for k in range(5):
    m = (q == k).values
    d = z[m & t].mean() - z[m & c].mean()
    s = np.sqrt(z[m & t].var(ddof=1)/(m & t).sum() + z[m & c].var(ddof=1)/(m & c).sum())
    p(f"  Q{k+1} y in [{y[m].min():.1f},{y[m].max():.1f}]: n_t={(m&t).sum()}, n_c={(m&c).sum()}, diff = {d:.3f} (SE {s:.3f})")

# residual SD per arm after linear fit in y
for name, m in (("control", c), ("treated", t)):
    res = z[m] - np.polyval(np.polyfit(y[m], z[m], 1), y[m])
    p(f"Residual SD of z given y, {name}: {res.std(ddof=2):.4f}")
lev = stats.levene(z[t] - np.polyval(np.polyfit(y[t], z[t], 1), y[t]),
                   z[c] - np.polyval(np.polyfit(y[c], z[c], 1), y[c]))
p(f"Levene test equal residual variance: W = {lev.statistic:.3f}, p = {lev.pvalue:.4f}")

# Fisher randomization test (sharp null of no effect for anyone), statistic = ANCOVA coefficient
p("")
def ancova_coef(xv):
    X = np.column_stack([np.ones(n), xv, y])
    return np.linalg.lstsq(X, z, rcond=None)[0][1]
obs = ancova_coef(x); R = 5000; cnt = 0; perm_stats = np.empty(R)
for i in range(R):
    xp = np.zeros(n); xp[rng.choice(n, 600, replace=False)] = 1
    perm_stats[i] = ancova_coef(xp)
pval = (1 + np.sum(np.abs(perm_stats) >= abs(obs))) / (R + 1)
p(f"Fisher randomization test (sharp null, ANCOVA statistic, R={R}): observed = {obs:.4f}, max |permuted| = {np.abs(perm_stats).max():.4f}, p = {pval:.5f}")

# relative effect
p("")
p(f"Control-group mean gain: {z[c].mean():.4f}; treated-group mean y: {y[t].mean():.4f}")
att, att_se = results["C_lin_att"]
p(f"Adopted ATT (estimator C) relative to imputed untreated mean gain of attendees: "
  f"{att:.4f} / {z[t].mean()-att:.4f} = {100*att/(z[t].mean()-att):.1f}%")

pd.DataFrame([(k, v[0], v[1], v[0]-1.96*v[1], v[0]+1.96*v[1]) for k, v in results.items()],
             columns=["estimator", "estimate", "se", "ci95_lo", "ci95_hi"]).to_csv(
    "/home/claude/submission/results/02_estimates_table.csv", index=False)
txt = "\n".join(lines); open(OUT, "w").write(txt); print(txt)
