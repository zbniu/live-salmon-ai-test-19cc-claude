"""Decompose the cutoff comparison. Just below c everyone is untreated (applicants + non-applicants).
Just above c, untreated = non-applicants, treated = applicants.
Local-linear limits at c:
  m_below = lim E[z | y->c-]        (mix of applicants' and non-applicants' z0)
  m_c0    = lim E[z | x=0, y->c+]   (non-applicants' z0)
  m_c1    = lim E[z | x=1, y->c+]   (applicants' z1)
  p       = lim P(x=1 | y->c+)      (applicant share)
Implied applicants' z0 at c: m_a0 = (m_below - (1-p) m_c0)/p
Selection bias at c = m_a0 - m_c0 ; ATT at c = m_c1 - m_a0 (equals fuzzy-RD Wald).
Naive within-cutoff contrast = m_c1 - m_c0. Bootstrap SEs."""
import pandas as pd, numpy as np
df = pd.read_csv("/mnt/user-data/uploads/data.csv")
c = df.loc[df.x==1,'y'].min(); df['r']=df.y-c
def limit(r, v, h, side):
    m = (r>=0) if side=='+' else (r<0)
    m &= np.abs(r)<=h
    rr, vv = r[m], v[m]; w = np.clip(1-np.abs(rr)/h,0,None)
    X = np.column_stack([np.ones(len(rr)), rr]); W = w
    b = np.linalg.solve(X.T@(X*W[:,None]), X.T@(vv*W)); return b[0]
def est(d,h):
    r, z, x = d.r.values, d.z.values, d.x.values
    m_below = limit(r,z,h,'-')
    a = r>=0
    m_c0 = limit(r[a&(x==0)], z[a&(x==0)], h, '+')
    m_c1 = limit(r[a&(x==1)], z[a&(x==1)], h, '+')
    p = limit(r, x.astype(float), h, '+')
    m_a0 = (m_below-(1-p)*m_c0)/p
    return dict(m_below=m_below, m_c0=m_c0, m_c1=m_c1, p=p, m_a0=m_a0,
                selection=m_a0-m_c0, att_c=m_c1-m_a0, naive_c=m_c1-m_c0, nonapp_jump=m_c0-m_below)
rng = np.random.default_rng(20261004)
out=[]
for h in [4,6,8,10,19.4]:
    e = est(df,h)
    B = pd.DataFrame([est(df.sample(len(df),replace=True,random_state=rng.integers(1e9)),h) for _ in range(1000)])
    for k,v in e.items():
        out.append(dict(h=h, quantity=k, estimate=v, boot_se=B[k].std(),
                        ci_lo=B[k].quantile(.025), ci_hi=B[k].quantile(.975)))
res = pd.DataFrame(out)
pd.set_option('display.width',200)
print("cutoff", c); print(res.round(3).to_string(index=False))
res.to_csv('results/03_selection_decomposition.csv', index=False)
