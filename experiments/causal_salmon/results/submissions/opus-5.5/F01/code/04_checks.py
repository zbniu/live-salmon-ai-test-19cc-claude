"""(a) Placebo cutoffs: jumps in E[z|y] where no treatment change occurs
    (below c: all students; above c: separately within x=0 and x=1).
(b) Within-y treated-vs-untreated contrast above c (biased by selection; shown for comparison only),
    and an assumption-dependent extrapolation: if the selection gap and the effect were constant in y,
    ATT = within-y contrast minus selection gap estimated at c."""
import pandas as pd, numpy as np
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
c = df.loc[df.x==1,'y'].min()
def jump(y, v, k, h=4):
    r = y-k; m = np.abs(r)<=h; r, v = r[m], v[m]; a=(r>=0).astype(float); w=np.clip(1-np.abs(r)/h,0,None)
    X = np.column_stack([np.ones(len(r)), a, r, a*r])
    XtW = X.T*w; b = np.linalg.solve(XtW@X, XtW@v)
    e = v-X@b; A=np.linalg.inv(XtW@X); V=A@((X.T*(w*e)**2)@X)@A
    return b[1], np.sqrt(V[1,1])
rows=[]
for k in [49,51,53]:
    s = df[df.y<c]; j,se = jump(s.y.values, s.z.values, k, h=min(4, k-45, c-k)); rows.append(('all, y<c',k,j,se))
for k in [60,63,66,69]:
    for g in [0,1]:
        s = df[(df.y>=c)&(df.x==g)]; j,se = jump(s.y.values, s.z.values, k); rows.append((f'x={g}, y>=c',k,j,se))
    s = df[df.y>=c]; j,se = jump(s.y.values, s.x.values.astype(float), k); rows.append(('P(x=1), y>=c',k,j,se))
pl = pd.DataFrame(rows, columns=['sample','placebo_cutoff','jump','se']); pl['t']=pl.jump/pl.se
print("Placebo jumps:"); print(pl.round(3).to_string(index=False)); pl.to_csv('results/04_placebo.csv',index=False)

# (b) within-y contrast above c, linear in y with interaction, averaged over treated
def contrast(d):
    a = d[d.y>=c]
    def fit(s): X=np.column_stack([np.ones(len(s)), s.y]); return np.linalg.lstsq(X, s.z, rcond=None)[0]
    b0, b1 = fit(a[a.x==0]), fit(a[a.x==1]); t=a[a.x==1]
    Xt = np.column_stack([np.ones(len(t)), t.y])
    return (Xt@b1 - Xt@b0).mean(), b0, b1
est, b0, b1 = contrast(df)
rng=np.random.default_rng(7); B=[contrast(df.sample(len(df),replace=True,random_state=rng.integers(1e9)))[0] for _ in range(1000)]
print(f"\nWithin-y treated-minus-untreated contrast above c, averaged over treated: {est:.3f} (boot SE {np.std(B):.3f})")
print("slope of z on y: untreated above c %.3f, treated %.3f" % (b0[1], b1[1]))
sel = pd.read_csv('results/03_selection_decomposition.csv').query("h==8 and quantity=='selection'").estimate.iloc[0]
print(f"Selection gap at c (h=8, from 03): {sel:.3f}")
print(f"Assumption-dependent extrapolated ATT (constant gap & effect): {est-sel:.3f}")
# binned within-y contrast
a=df[df.y>=c].copy(); a['bin']=pd.cut(a.y,[c,60,65,70,75.01],right=False)
g=a.groupby(['bin','x'],observed=True).z.mean().unstack(); g['diff']=g[1]-g[0]
print("\nBinned contrast above c:"); print(g.round(3))
