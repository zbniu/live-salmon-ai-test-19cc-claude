"""Baseline-adjusted sensitivity estimates; no external regression package."""
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from scipy import stats

root = Path(__file__).resolve().parents[1]
d = pd.read_csv(sys.argv[1])
x, y, z = (d[c].to_numpy(dtype=float) for c in ['x', 'y', 'z'])
# Center at the actual attendees' mean: coefficient of x estimates the
# treatment contrast standardized to their observed baseline distribution.
center = y[x == 1].mean()
u = y - center
q = u**2 - (u[x == 1]**2).mean()

def fit(name, X, labels):
    beta = np.linalg.lstsq(X, z, rcond=None)[0]
    residual = z - X @ beta
    bread = np.linalg.inv(X.T @ X)
    leverage = np.einsum('ij,jk,ik->i', X, bread, X)
    hc3 = bread @ (X.T @ ((residual/(1-leverage))**2)[:,None] * 0) if False else None
    weighted_X = X * (residual/(1-leverage))[:, None]
    hc3 = bread @ (weighted_X.T @ weighted_X) @ bread
    se = np.sqrt(np.diag(hc3))
    index = labels.index('x')
    estimate, uncertainty = float(beta[index]), float(se[index])
    critical = stats.norm.ppf(.975)
    return {
        'model': name, 'n': len(z), 'labels': labels,
        'coefficients': beta.tolist(), 'hc3_se': se.tolist(),
        'effect': estimate, 'effect_se': uncertainty,
        'ci95': [float(estimate-critical*uncertainty), float(estimate+critical*uncertainty)],
        'p_two_sided_normal': float(2*stats.norm.sf(abs(estimate/uncertainty))),
        'r_squared': float(1 - (residual@residual)/np.sum((z-z.mean())**2)),
        'max_leverage': float(leverage.max()),
        'baseline_center_attendees': float(center)
    }

models = [
    fit('Common-slope linear ANCOVA', np.column_stack([np.ones(len(x)), x, u]), ['intercept','x','y_centered']),
    fit('Separate-slope linear, standardized to attendees', np.column_stack([np.ones(len(x)),x,u,x*u]), ['intercept','x','y_centered','x_y_centered']),
    fit('Separate quadratic, standardized to attendees', np.column_stack([np.ones(len(x)),x,u,q,x*u,x*q]), ['intercept','x','y_centered','y_squared_centered','x_y_centered','x_y_squared_centered'])
]
(root/'results'/'03_adjusted.json').write_text(json.dumps(models,indent=2),encoding='utf-8')
pd.DataFrame([{k:m[k] for k in ['model','effect','effect_se','ci95','p_two_sided_normal','r_squared']} for m in models]).to_csv(root/'results'/'03_adjusted_summary.csv',index=False)
print(json.dumps(models,indent=2))
