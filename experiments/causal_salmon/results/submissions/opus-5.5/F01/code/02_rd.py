"""Fuzzy RD at the admission cutoff c = min y among treated.
Below c nobody is treated; above c the treated are exactly the applicants (one-sided noncompliance),
so the Wald ratio identifies the effect for treated students at y = c."""
import pandas as pd, numpy as np
import statsmodels.api as sm
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
c = df.loc[df.x==1,'y'].min()
df['r'] = df.y - c
df['above'] = (df.r >= 0).astype(int)
def tri(r,h): return np.clip(1-np.abs(r)/h,0,None)
def llr(d, h, kernel='tri', p=1):
    s = d[np.abs(d.r) <= h].copy()
    w = tri(s.r,h) if kernel=='tri' else np.ones(len(s))
    cols = {'above': s.above}
    for k in range(1,p+1):
        cols[f'r{k}'] = s.r**k; cols[f'ar{k}'] = s.above*s.r**k
    X = sm.add_constant(pd.DataFrame(cols))
    fs = sm.WLS(s.x, X, weights=w).fit(cov_type='HC1')
    rf = sm.WLS(s.z, X, weights=w).fit(cov_type='HC1')
    # 2SLS (IV) for SE of the ratio
    Xex = X.drop(columns='above'); Z = X
    Xen = pd.concat([Xex, s.x.rename('x')], axis=1)
    W = np.sqrt(np.asarray(w, dtype=float))[:,None]
    Zw, Xw, yw = Z.values*W, Xen.values*W, s.z.values*W[:,0]
    PZ = Zw @ np.linalg.pinv(Zw.T@Zw) @ Zw.T
    b = np.linalg.solve(Xw.T@PZ@Xw, Xw.T@PZ@yw)
    e = yw - Xw@b
    A = np.linalg.inv(Xw.T@PZ@Xw); Xh = PZ@Xw
    V = A @ (Xh.T @ (Xh*(e**2)[:,None])) @ A * len(e)/(len(e)-Xw.shape[1])
    return dict(h=h, kernel=kernel, p=p, n=len(s), n_below=int((s.r<0).sum()), n_above=int((s.r>=0).sum()),
                fs_jump=fs.params['above'], fs_se=fs.bse['above'],
                rf_jump=rf.params['above'], rf_se=rf.bse['above'],
                late=b[-1], late_se=np.sqrt(V[-1,-1]))
rows=[]
for p in [1,2]:
    for h in [2,3,4,5,6,8,10,19.4]:
        for k in ['tri','uni']:
            rows.append(llr(df,h,k,p))
res = pd.DataFrame(rows)
pd.set_option('display.width',200)
print("cutoff c =", c)
print(res.round(3).to_string(index=False))
res.to_csv('results/02_rd_estimates.csv', index=False)
