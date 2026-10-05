"""Sensitivity of the regression ATT to flexibility of the control outcome model E[z|y,x=0], y>=c,
with 10-fold CV prediction error for each control model, plus NN matching with different M."""
import pandas as pd, numpy as np
from patsy import dmatrix
df=pd.read_csv("/mnt/user-data/uploads/data.csv"); c=df.loc[df.x==1,'y'].min(); R=df[df.y>=c]
lb,ub=R.y.min()-1e-6,R.y.max()+1e-6
def B(y,kind):
    if kind.startswith('poly'):
        p=int(kind[4:]); u=(y-65)/5; return np.column_stack([u**j for j in range(p+1)])
    k=int(kind[6:]); return np.asarray(dmatrix(f"bs(y, df={k}, degree=3, lower_bound=lb, upper_bound=ub)",{"y":y,"lb":lb,"ub":ub}))
k=R[R.x==0]; t=R[R.x==1]; rng=np.random.default_rng(1); fold=rng.integers(0,10,len(k))
rows=[]
for kind in ['poly1','poly2','poly3','poly4','spline4','spline5','spline6','spline8','spline10']:
    b=np.linalg.lstsq(B(k.y.values,kind),k.z.values,rcond=None)[0]
    att=(t.z.values-B(t.y.values,kind)@b).mean()
    cv=[]
    for f in range(10):
        tr,te=fold!=f,fold==f
        bb=np.linalg.lstsq(B(k.y.values[tr],kind),k.z.values[tr],rcond=None)[0]
        cv.append(((k.z.values[te]-B(k.y.values[te],kind)@bb)**2).mean())
    rows.append([kind,att,np.mean(cv)])
print(pd.DataFrame(rows,columns=['control_model','ATT','cv_MSE']).to_string(index=False,float_format=lambda v:f"{v:.4f}"))
ky,kz=k.y.values,k.z.values
for M in [1,5,10,20,40]:
    e=[zv-kz[np.argsort(np.abs(ky-yv))[:M]].mean() for yv,zv in zip(t.y.values,t.z.values)]
    print(f"NN matching M={M}: ATT={np.mean(e):.3f}")
# slope check: is E[z|y] slope same for treated & controls? (OLS with interaction)
X=np.column_stack([np.ones(len(R)),R.x,R.y-65,R.x*(R.y-65)]); b=np.linalg.lstsq(X,R.z.values,rcond=None)[0]
res=R.z.values-X@b; XtXi=np.linalg.inv(X.T@X); V=XtXi@(X.T*res**2)@X@XtXi
print("z ~ x + (y-65) + x*(y-65): coef",b.round(3)," HC0 SE",np.sqrt(np.diag(V)).round(3))
