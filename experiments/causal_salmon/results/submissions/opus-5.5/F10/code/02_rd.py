import pandas as pd, numpy as np
rng=np.random.default_rng(1)
d = pd.read_csv('/mnt/user-data/uploads/data.csv')
c = d.loc[d.x==1,'y'].min()
y,x,z = d.y.values,d.x.values,d.z.values

def ll(yv,v,side,h,c,kern='tri'):
    m = (yv>=c) if side=='R' else (yv<c)
    r = yv[m]-c; vv=v[m]; k = np.abs(r)<=h
    r,vv=r[k],vv[k]
    w = (1-np.abs(r)/h) if kern=='tri' else np.ones_like(r)
    X=np.c_[np.ones_like(r),r]; W=np.sqrt(w)
    b=np.linalg.lstsq(X*W[:,None],vv*W,rcond=None)[0]; return b[0], len(r)

def frd(yv,xv,zv,h,c,kern='tri'):
    zr,nr=ll(yv,zv,'R',h,c,kern); zl,nl=ll(yv,zv,'L',h,c,kern)
    xr,_=ll(yv,xv,'R',h,c,kern); xl,_=ll(yv,xv,'L',h,c,kern)
    return (zr-zl)/(xr-xl), zr-zl, xr-xl, nl, nr

out=[]
for kern in ['tri','uni']:
  for h in [3,4,5,6,8,10,12]:
    est,rf,fs,nl,nr = frd(y,x,z,h,c,kern)
    bs=[]
    for b in range(1000):
        i=rng.integers(0,len(y),len(y))
        bs.append(frd(y[i],x[i],z[i],h,c,kern)[0])
    se=np.std(bs)
    out.append(dict(kernel=kern,h=h,n_left=nl,n_right=nr,first_stage=fs,reduced_form=rf,LATT_at_cutoff=est,boot_se=se,
                    ci_lo=np.percentile(bs,2.5),ci_hi=np.percentile(bs,97.5)))
r=pd.DataFrame(out); print('cutoff',c); print(r.round(3).to_string())
r.to_csv('results/02_fuzzy_rd.csv',index=False)

# Quadratic global-ish fit within h=12 as check
def poly_side(yv,v,side,h,c,p):
    m=((yv>=c) if side=='R' else (yv<c)) & (np.abs(yv-c)<=h)
    r=yv[m]-c; X=np.vander(r,p+1,increasing=True)
    return np.linalg.lstsq(X,v[m],rcond=None)[0][0]
for h,p in [(12,2),(18,2),(18,3)]:
    rf=poly_side(y,z,'R',h,c,p)-poly_side(y,z,'L',h,c,p)
    fs=poly_side(y,x,'R',h,c,p)-poly_side(y,x,'L',h,c,p)
    print(f'poly p={p} h={h}: fs={fs:.3f} rf={rf:.3f} est={rf/fs:.3f}')
