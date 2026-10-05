# ATT (effect among attendees) via separate regressions per arm, imputing control outcome for treated; bootstrap CI
import pandas as pd, numpy as np
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
def att(s):
    t,c=s[s.x==1],s[s.x==0]
    b=np.polyfit(c.y,c.z,1)           # control outcome model
    return (t.z-np.polyval(b,t.y)).mean()
est=att(df); rng=np.random.default_rng(7)
bs=[att(df.sample(len(df),replace=True,random_state=int(rng.integers(1e9)))) for _ in range(2000)]
print(f"ATT regression-imputation estimate={est:.4f}, bootstrap 95% CI={np.percentile(bs,[2.5,97.5]).round(4)}, boot SE={np.std(bs):.4f}")
