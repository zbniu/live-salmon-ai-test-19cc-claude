import pandas as pd, numpy as np
import statsmodels.formula.api as smf
df = pd.read_csv("/mnt/user-data/uploads/data.csv")

def att(d):
    # separate regressions of z on y in each arm; impute control outcome for treated students
    c=d[d.x==0]; t=d[d.x==1]
    b=np.polyfit(c.y,c.z,1)
    return t.z.mean()-np.polyval(b,t.y).mean()

est=att(df); print("Regression-adjusted ATT (control-arm model imputed for treated):", round(est,4))
rng=np.random.default_rng(7)
bs=[att(df.sample(len(df),replace=True,random_state=int(rng.integers(1e9)))) for _ in range(5000)]
print("bootstrap SE", round(np.std(bs),4), "95% CI", np.round(np.percentile(bs,[2.5,97.5]),4))

# Adjusted ATE (Lin) for comparison, delta from earlier: 1.0355 (CI 0.671-1.400)
m=smf.ols("z~x*I(y-%f)"%df.y.mean(),df).fit(cov_type="HC2")
print("Lin ATE:", round(m.params['x'],4), m.conf_int().loc['x'].round(4).tolist())
# Interaction test
print("x:y interaction p =", round(m.pvalues.iloc[-1],4))
# Variance reduction
print("Residual SD z|y,x:", round(np.sqrt(m.scale),3), "vs raw SD z:", round(df.z.std(),3))
