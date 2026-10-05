"""Analyze the randomized tutoring study using only the supplied CSV."""

import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "upload" / "data(20261004-071310).csv"
RESULTS = ROOT / "submission" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

with DATA.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    assert reader.fieldnames == ["x", "y", "z"]
    rows = list(reader)

x = np.array([int(r["x"]) for r in rows])
y = np.array([float(r["y"]) for r in rows])
z = np.array([float(r["z"]) for r in rows])
assert len(rows) == 2000 and np.isin(x, [0, 1]).all()
assert np.isfinite(y).all() and np.isfinite(z).all()
assert np.count_nonzero(x) == 600

treated, control = x == 1, x == 0
zt, zc = z[treated], z[control]
yt, yc = y[treated], y[control]
n1, n0 = len(zt), len(zc)
diff = zt.mean() - zc.mean()
v1, v0 = zt.var(ddof=1), zc.var(ddof=1)
se = math.sqrt(v1 / n1 + v0 / n0)
df = (v1 / n1 + v0 / n0) ** 2 / ((v1 / n1) ** 2 / (n1 - 1) + (v0 / n0) ** 2 / (n0 - 1))
tstat = diff / se
pval = 2 * stats.t.sf(abs(tstat), df)
ci = [diff - stats.t.ppf(.975, df) * se, diff + stats.t.ppf(.975, df) * se]


def ols_hc2(design, outcome, treatment_column=1):
    """OLS coefficient and HC2 standard error for the treatment column."""
    inv = np.linalg.inv(design.T @ design)
    beta = inv @ design.T @ outcome
    residual = outcome - design @ beta
    leverage = np.einsum("ij,jk,ik->i", design, inv, design)
    meat = design.T @ ((residual**2 / (1 - leverage))[:, None] * design)
    cov = inv @ meat @ inv
    b = float(beta[treatment_column])
    s = float(np.sqrt(cov[treatment_column, treatment_column]))
    return {"effect": b, "se_hc2": s,
            "ci95_normal": [b - 1.96 * s, b + 1.96 * s],
            "p_two_sided_normal": float(2 * stats.norm.sf(abs(b / s)))}


yc0 = y - y.mean()
adjusted_linear = ols_hc2(np.column_stack([np.ones(len(x)), x, yc0]), z)
adjusted_quadratic = ols_hc2(np.column_stack([np.ones(len(x)), x, yc0, yc0**2]), z)

quartile_edges = np.quantile(y, [0, .25, .5, .75, 1])
quartiles = []
for i in range(4):
    in_bin = (y >= quartile_edges[i]) & (y < quartile_edges[i+1] if i < 3 else y <= quartile_edges[i+1])
    a, b = z[in_bin & treated], z[in_bin & control]
    quartiles.append({"bin": i+1, "y_range": [float(quartile_edges[i]), float(quartile_edges[i+1])],
                      "n_treated": len(a), "n_control": len(b),
                      "mean_gain_treated": float(a.mean()), "mean_gain_control": float(b.mean()),
                      "difference": float(a.mean() - b.mean())})

result = {
    "data_check": {"rows": len(x), "treated": n1, "control": n0,
                   "columns": ["x", "y", "z"], "missing_or_nonfinite": 0,
                   "y_range": [float(y.min()), float(y.max())],
                   "z_range": [float(z.min()), float(z.max())]},
    "baseline_y": {"mean_treated": float(yt.mean()), "mean_control": float(yc.mean()),
                   "difference": float(yt.mean() - yc.mean())},
    "primary_unadjusted": {
        "mean_gain_treated": float(zt.mean()), "mean_gain_control": float(zc.mean()),
        "sd_treated": float(zt.std(ddof=1)), "sd_control": float(zc.std(ddof=1)),
        "median_treated": float(np.median(zt)), "median_control": float(np.median(zc)),
        "difference_points": float(diff), "welch_se": se, "welch_df": df,
        "welch_t": tstat, "p_two_sided": pval, "ci95": ci},
    "baseline_adjusted_linear_hc2": adjusted_linear,
    "baseline_adjusted_quadratic_hc2": adjusted_quadratic,
    "baseline_quartiles": quartiles,
}

with (RESULTS / "analysis.json").open("w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
    f.write("\n")
print(json.dumps(result, indent=2))
