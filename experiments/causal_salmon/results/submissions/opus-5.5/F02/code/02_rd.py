"""Fuzzy regression discontinuity at the cutoff implied by the assignment rule.
Below c nobody can be treated (candidates are accepted in descending y until slots fill),
so the fuzzy-RD Wald ratio = effect of Q on treated units at y = c."""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from rdrobust import rdrobust, rdbwselect
d = pd.read_csv('/mnt/user-data/uploads/data.csv')
c = d.loc[d.x==1,'y'].min()
d['r'] = d.y - c; d['D'] = (d.r >= 0).astype(float)
out = []
def tsls(h, p=1, kernel='tri'):
    s = d[d.r.abs() <= h].copy()
    w = (1 - s.r.abs()/h) if kernel=='tri' else np.ones(len(s))
    cols = [np.ones(len(s))]
    for k in range(1,p+1):
        cols += [s.r**k, s.D*s.r**k]
    W = np.column_stack(cols)
    Z = np.column_stack([s.D] + [W]); X = np.column_stack([s.x] + [W]); Y = s.z.values
    sw = np.sqrt(w.values if hasattr(w,'values') else w)
    Zw, Xw, Yw = Z*sw[:,None], X*sw[:,None], Y*sw
    # first stage, reduced form
    fs = np.linalg.lstsq(Zw, X[:,0]*sw, rcond=None)[0][0]
    rf = np.linalg.lstsq(Zw, Yw, rcond=None)[0][0]
    PzX = Zw @ np.linalg.lstsq(Zw, Xw, rcond=None)[0]
    b = np.linalg.lstsq(PzX, Yw, rcond=None)[0]
    e = Yw - Xw @ b
    A = np.linalg.inv(PzX.T @ PzX)
    V = A @ (PzX.T * e**2) @ PzX @ A * len(s)/(len(s)-X.shape[1])
    return dict(h=h, p=p, kernel=kernel, n=len(s), n_right=int(s.D.sum()), first_stage=fs,
                reduced_form=rf, tau=b[0], se=np.sqrt(V[0,0]))
for p in (1,2):
    for h in (2,3,4,5,6,7.5,9,10.5):
        out.append(tsls(h,p))
for h in (3,5,7.5): out.append(tsls(h,1,'uni'))
res = pd.DataFrame(out); res['ci_lo']=res.tau-1.96*res.se; res['ci_hi']=res.tau+1.96*res.se
pd.set_option('display.width',200)
print("cutoff c =", c)
print(res.round(3).to_string()); res.to_csv('results/02_rd_manual_grid.csv', index=False)

print("\n=== rdrobust (MSE-optimal bw, triangular, p=1, robust bias-corrected CI) ===")
for p in (1,2):
    r = rdrobust(d.z, d.y, c=c, fuzzy=d.x, p=p)
    print(f"--- p={p}"); print(r)
    print("coef:", r.coef.values.ravel(), "\nse:", r.se.values.ravel(), "\nci:\n", r.ci)
print("\n=== rdrobust sharp RD on x (first stage) and z (reduced form), p=1 ===")
print(rdrobust(d.x, d.y, c=c)); print(rdrobust(d.z, d.y, c=c))

# plot
d['bin'] = pd.cut(d.r, np.arange(np.floor(d.r.min()), np.ceil(d.r.max())+1, 1))
g = d.groupby('bin', observed=True).agg(r=('r','mean'), z=('z','mean'), x=('x','mean'))
fig, ax = plt.subplots(1,2, figsize=(11,4))
ax[0].scatter(g.r, g.x); ax[0].axvline(0, color='k', ls='--'); ax[0].set(xlabel='y - c', ylabel='share treated (x)')
ax[1].scatter(g.r, g.z, label='all units'); ax[1].axvline(0, color='k', ls='--'); ax[1].set(xlabel='y - c', ylabel='mean z')
for k,lab in ((1,'treated'),(0,'untreated')):
    gg = d[d.x==k].groupby('bin', observed=True).agg(r=('r','mean'), z=('z','mean'))
    ax[1].plot(gg.r, gg.z, '.', alpha=.6, label=lab)
ax[1].legend(); plt.tight_layout(); plt.savefig('results/02_rd_plot.png', dpi=110)
