"""Only public x,y,z enter these estimators; truth is attached separately."""
import math

import numpy as np


def unavailable(reason, details=None, status='unavailable'):
    return dict(status=status, E=None, se=None, ci=None, covered=None, reason=reason, details=details or {})


def not_applicable():
    return unavailable(None, status='not_applicable')


def result(E, se, details=None):
    if not np.isfinite([E, se]).all():
        return unavailable('nonfinite_estimate_or_se', details)
    return dict(status='ok', E=float(E), se=float(se), ci=[float(E-1.96*se),float(E+1.96*se)], covered=None, reason=None, details=details or {})


def with_interval(r, T):
    r = dict(r)
    if r['status'] == 'ok':
        r['ci'] = [r['E'] - 1.96*r['se'], r['E'] + 1.96*r['se']]
        r['covered'] = bool(r['ci'][0] <= T <= r['ci'][1])
    return r


def mean_difference(x, z):
    T, C = z[x == 1], z[x == 0]
    return result(T.mean()-C.mean(), np.sqrt(T.var(ddof=1)/len(T)+C.var(ddof=1)/len(C)))


def adjusted_ols(x, y, z):
    c = np.mean(y[x == 1])
    yc = y - c
    X = np.column_stack((np.ones(len(x)), x, yc, x*yc))
    rank = int(np.linalg.matrix_rank(X))
    if rank < 4:
        return unavailable('rank_below_four', {'rank':rank})
    xtx = X.T @ X
    try:
        coef = np.linalg.solve(xtx, X.T @ z)
        inv = np.linalg.inv(xtx)
    except np.linalg.LinAlgError as e:
        return unavailable('normal_equations_unsolvable', {'rank':rank,'error':str(e)})
    h = np.sum((X @ inv)*X, axis=1)
    details = {'rank':rank,'center':float(c),'h_max':float(h.max()),'coefficients':coef.tolist()}
    if np.any(h >= 1):
        return unavailable('leverage_at_least_one',details)
    residual = z - X@coef
    hc3 = inv @ (X.T @ ((residual**2/(1-h)**2)[:,None]*X)) @ inv
    se = np.sqrt(hc3[1,1])
    return result(coef[1],se,details)


def bin_counts(x, y):
    ids = np.flatnonzero(x == 1)
    t = y[ids[np.lexsort((ids,y[ids]))]]
    K = len(t)
    edges = [t[0], *[t[k*K//5] for k in range(1,5)], t[-1]]
    masks = [(y >= edges[k]) & ((y < edges[k+1]) if k < 4 else (y <= edges[k+1])) for k in range(5)]
    return {'edges':[float(v) for v in edges], 'treated':[int(np.sum(mask & (x==1))) for mask in masks], 'control':[int(np.sum(mask & (x==0))) for mask in masks]}


def segmented_difference(x, y, z):
    bins = bin_counts(x,y)
    if min(bins['treated']+bins['control']) < 2:
        return unavailable('segment_group_count_below_two',bins)
    E, variance, K = 0., 0., int(np.sum(x))
    for k in range(5):
        lo,hi = bins['edges'][k:k+2]
        mask = (y >= lo) & ((y < hi) if k < 4 else (y <= hi))
        t,c = z[mask & (x==1)],z[mask & (x==0)]
        weight = len(t)/K
        E += weight*(t.mean()-c.mean())
        variance += weight**2*(t.var(ddof=1)/len(t)+c.var(ddof=1)/len(c))
    return result(E,np.sqrt(variance),bins)


def sigmoid(t):
    p = np.empty_like(t,dtype=np.float64)
    positive = t >= 0
    p[positive] = 1/(1+np.exp(-t[positive]))
    e = np.exp(t[~positive])
    p[~positive] = e/(1+e)
    return p


def propensity_point(x,y,z,mu):
    mask = y >= np.min(y[x==1])
    xs,ys,zs = x[mask],y[mask],z[mask]
    s = (ys-mu)/15
    X = np.column_stack((np.ones(len(xs)),s,s**2))
    theta = np.zeros(3,dtype=np.float64)
    details = {'support_count':len(xs),'support_controls':int(np.sum(xs==0)),'support_min':float(np.min(ys)),'iterations':0}
    deltas=[]
    def fail(reason):
        details['max_delta_history']=deltas
        details['theta']=[float(v) if np.isfinite(v) else None for v in theta]
        return {'status':'unavailable','E':None,'reason':reason,'details':details,'max_weight':None,'ess':None}
    if not np.any(xs==0):
        return fail('no_supported_controls')
    converged=False
    for iteration in range(50):
        p=sigmoid(X@theta)
        if not np.isfinite(p).all():
            return fail('nonfinite_propensity')
        W=p*(1-p)
        H=X.T@(W[:,None]*X)
        g=X.T@(xs-p)
        try:
            delta=np.linalg.solve(H,g)
        except np.linalg.LinAlgError:
            details['hessian_rank']=int(np.linalg.matrix_rank(H))
            return fail('hessian_unsolvable')
        theta=theta+delta
        details['iterations']=iteration+1
        d=float(np.max(np.abs(delta)))
        deltas.append(d if np.isfinite(d) else None)
        if not np.isfinite(theta).all():
            return fail('nonfinite_coefficients')
        if d < 1e-10:
            converged=True
            break
    p=sigmoid(X@theta)
    details['p_min'],details['p_max']=float(p.min()),float(p.max())
    if not converged:
        return fail('newton_not_converged_50')
    pc=p[xs==0]
    with np.errstate(divide='ignore',invalid='ignore',over='ignore'):
        w=pc/(1-pc)
    if not np.isfinite(w).all():
        return fail('nonfinite_weights')
    total=np.sum(w)
    if total == 0:
        return fail('zero_weight_sum')
    if not np.isfinite(total):
        return fail('nonfinite_weights')
    E=np.mean(z[x==1])-np.sum(w*zs[xs==0])/total
    if not np.isfinite(E):
        return fail('nonfinite_estimate')
    return {'status':'ok','E':float(E),'reason':None,'max_weight':float(np.max(w/total)),'ess':float(total**2/np.sum(w*w)),'details':details}


def weighted_diagnostic(x,y,z,mu,seed,purpose,world_code):
    from src.data.generator import uniform, TAG
    point=propensity_point(x,y,z,mu)
    t,c=np.flatnonzero(x==1),np.flatnonzero(x==0)
    K,n=len(t),len(x)
    boot=[]
    for b in range(200):
        v=uniform([TAG,purpose,seed,world_code,20,b],n)
        ti=np.minimum(np.floor(v[:K]*K).astype(np.int64),K-1)
        ci=np.minimum(np.floor(v[K:]*(n-K)).astype(np.int64),n-K-1)
        ids=np.r_[t[ti],c[ci]]
        fit=propensity_point(x[ids],y[ids],z[ids],mu)
        boot.append({'index':b,'status':fit['status'],'E':fit['E'],'reason':fit['reason'],'details':fit['details']})
    failures=[v['index'] for v in boot if v['status']!='ok']
    if point['status']=='ok' and not failures:
        r=result(point['E'],np.std([v['E'] for v in boot],ddof=1),point['details'])
    else:
        r=unavailable(point['reason'] or 'bootstrap_unavailable',point['details'])
        r['E']=point['E']
    r.update(max_weight=point['max_weight'],ess=point['ess'],bootstrap_successes=200-len(failures),bootstrap_failures=failures)
    return r,boot
