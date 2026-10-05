"""Public-projection estimators, independently derived from planning A.9."""
import math
import numpy as np


def absent(reason, status="unavailable"):
    return dict(status=status, E=None, se=None, ci=None, covered=None, reason=reason)


def result(E, se):
    if not np.isfinite(E) or not np.isfinite(se):
        return absent("nonfinite_estimate_or_standard_error")
    return dict(status="ok", E=float(E), se=float(se), ci=[float(E-1.96*se), float(E+1.96*se)], covered=None, reason=None)


def coverage(r, truth):
    r = dict(r)
    r["covered"] = r["ci"][0] <= truth <= r["ci"][1] if r["ci"] is not None else None
    return r


def difference(x, z):
    t, c = z[x == 1], z[x == 0]
    E = np.mean(t)-np.mean(c)
    se = math.sqrt(np.var(t, ddof=1)/len(t)+np.var(c, ddof=1)/len(c))
    return result(E, se)


def standardized(x, y, z):
    centered = y-np.mean(y[x == 1])
    X = np.column_stack((np.ones(len(x)), x, centered, x*centered))
    rank = int(np.linalg.matrix_rank(X))
    if rank < 4:
        return absent("design_rank_below_four"), {"rank": rank}
    gram = X.T @ X
    try:
        beta = np.linalg.solve(gram, X.T @ z)
        inv = np.linalg.inv(gram)
    except np.linalg.LinAlgError:
        return absent("normal_equations_unsolvable"), {"rank": rank}
    residual = z-X @ beta
    leverage = np.sum((X @ inv)*X, axis=1)
    detail = dict(rank=rank, max_leverage=float(np.max(leverage)), coefficients=beta.tolist())
    if np.any(leverage >= 1):
        return absent("leverage_at_least_one"), detail
    inflated = residual**2/(1-leverage)**2
    covariance = inv @ (X.T @ (inflated[:, None]*X)) @ inv
    variance = covariance[1, 1]
    se = np.sqrt(variance) if variance >= 0 else np.nan
    return result(beta[1], se), detail


def partitions(x, y):
    t = np.flatnonzero(x == 1)
    ordered = t[np.lexsort((t, y[t]))]
    K = len(t)
    q = np.array([y[ordered[0]], *[y[ordered[k*K//5]] for k in range(1, 5)], y[ordered[-1]]])
    masks = [(y >= q[k]) & ((y < q[k+1]) if k < 4 else (y <= q[k+1])) for k in range(5)]
    bins = dict(edges=q.tolist(), treated=[int(np.sum(m & (x == 1))) for m in masks], control=[int(np.sum(m & (x == 0))) for m in masks])
    return bins, masks


def stratified_difference(x, y, z):
    bins, masks = partitions(x, y)
    if min(bins["treated"]+bins["control"]) < 2:
        return absent("bin_group_count_below_two"), bins
    total = np.sum(x)
    E, variance = 0., 0.
    for m in masks:
        t, c = z[m & (x == 1)], z[m & (x == 0)]
        share = len(t)/total
        E += share*(np.mean(t)-np.mean(c))
        variance += share**2*(np.var(t, ddof=1)/len(t)+np.var(c, ddof=1)/len(c))
    return result(E, np.sqrt(variance)), bins


def sigmoid(t):
    p = np.empty_like(t)
    pos = t >= 0
    p[pos] = 1/(1+np.exp(-t[pos]))
    exp = np.exp(t[~pos])
    p[~pos] = exp/(1+exp)
    return p


def weighted_point(x, y, z, center=None):
    support_min = float(np.min(y[x == 1]))
    support = y >= support_min
    xs, ys = x[support], y[support]
    controls = xs == 0
    detail = dict(support_min=support_min, support_n=int(sum(support)), support_control_n=int(sum(controls)), iterations=0, newton=[]) 
    def fail(reason):
        return dict(status="unavailable", E=None, max_weight=None, ess=None, reason=reason, details=detail)
    if not np.any(controls):
        return fail("no_controls_in_support")
    # Calibration passes registered mu_y; hand fixtures may use a public centering constant.
    s = (ys-(np.mean(y) if center is None else center))/15.
    X = np.column_stack((np.ones(len(xs)), s, s*s))
    theta = np.zeros(3)
    for iteration in range(50):
        p = sigmoid(X @ theta)
        H = X.T @ ((p*(1-p))[:, None]*X)
        g = X.T @ (xs-p)
        detail["iterations"] = iteration+1
        try:
            delta = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            return fail("hessian_unsolvable")
        theta = theta+delta
        step = float(np.max(np.abs(delta)))
        detail["newton"].append(dict(iteration=iteration+1, max_delta=step if np.isfinite(step) else None, min_p=float(np.min(p)), max_p=float(np.max(p)), hessian_rank=int(np.linalg.matrix_rank(H))))
        if not np.all(np.isfinite(theta)):
            return fail("nonfinite_coefficients")
        if step < 1e-10:
            break
    else:
        return fail("newton_not_converged_in_50_steps")
    p = sigmoid(X @ theta)
    detail.update(coefficients=theta.tolist(), min_p=float(np.min(p)), max_p=float(np.max(p)))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        w = p[controls]/(1-p[controls])
    if not np.all(np.isfinite(p)) or not np.all(np.isfinite(w)):
        return fail("nonfinite_propensity_or_weight")
    total = np.sum(w)
    if total == 0:
        return fail("zero_control_weight_sum")
    normalized = w/total
    E = np.mean(z[x == 1])-np.sum(normalized*z[support][controls])
    if not np.isfinite(E):
        return fail("nonfinite_weighted_estimate")
    return dict(status="ok", E=float(E), max_weight=float(np.max(normalized)), ess=float(total**2/np.sum(w*w)), reason=None, details=detail)
