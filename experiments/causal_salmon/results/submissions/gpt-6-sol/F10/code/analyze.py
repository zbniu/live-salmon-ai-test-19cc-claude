"""Analyze the complete supplied study CSV; write machine-readable and text results."""
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

BASE = Path(__file__).resolve().parents[2]
SOURCE = BASE / "upload" / "data(20261004-071403).csv"
OUT = BASE / "submission" / "results"
OUT.mkdir(parents=True, exist_ok=True)

with SOURCE.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    assert reader.fieldnames == ["x", "y", "z"], reader.fieldnames
    rows = list(reader)
assert len(rows) == 2000
data = np.array([[float(row[k]) for k in ("x", "y", "z")] for row in rows])
assert np.isfinite(data).all()
x, y, z = data.T
assert set(x) == {0.0, 1.0} and int(x.sum()) == 600
assert np.all((y >= 0) & (y <= 100))
assert np.all((y + z >= -1e-10) & (y + z <= 100 + 1e-10))
cutoff = float(y[x == 1].min())
assert not np.any((x == 1) & (y < cutoff))

def summary(mask):
    return {"n": int(mask.sum()), "mean_y": float(y[mask].mean()),
            "mean_z": float(z[mask].mean()), "sd_z": float(z[mask].std(ddof=1)),
            "mean_end_score": float((y[mask] + z[mask]).mean())}

def weighted_regression(outcome, design, weights=None):
    """WLS coefficients and heteroskedasticity-robust HC1 covariance."""
    n, p = design.shape
    if weights is None:
        weights = np.ones(n)
    xtwx_inv = np.linalg.inv(design.T @ (weights[:, None] * design))
    beta = xtwx_inv @ (design.T @ (weights * outcome))
    residual = outcome - design @ beta
    scores = design * (weights * residual)[:, None]
    covariance = xtwx_inv @ (scores.T @ scores) @ xtwx_inv * n / (n - p)
    return beta, covariance, residual, scores, xtwx_inv

treated = x == 1
control = ~treated
groups = {"attended": summary(treated), "did_not_attend": summary(control)}
raw = groups["attended"]["mean_z"] - groups["did_not_attend"]["mean_z"]
raw_se = math.sqrt(groups["attended"]["sd_z"]**2 / 600
                   + groups["did_not_attend"]["sd_z"]**2 / 1400)

adjusted = {}
for name, design in [
    ("linear_y", np.column_stack((np.ones(len(x)), x, y))),
    ("quadratic_y", np.column_stack((np.ones(len(x)), x, y, y**2))),
    ("quadratic_y_interactions", np.column_stack((np.ones(len(x)), x, y, y**2,
                                                  x*y, x*y**2))),
]:
    beta, cov, *_ = weighted_regression(z, design)
    adjusted[name] = {"x_coefficient": float(beta[1]),
                      "robust_se": float(math.sqrt(cov[1, 1]))}

local = []
for bandwidth in [3, 5, 8, 10, 15, 20]:
    distance = y - cutoff
    keep = abs(distance) < bandwidth
    d = distance[keep]
    above = (d >= 0).astype(float)
    design = np.column_stack((np.ones(len(d)), d, above, d*above))
    weights = 1 - abs(d) / bandwidth
    bz, cz, rz, sz, inv = weighted_regression(z[keep], design, weights)
    bx, cx, rx, sx, _ = weighted_regression(x[keep], design, weights)
    jump_z, jump_x = float(bz[2]), float(bx[2])
    # Joint HC1 covariance of the two discontinuities, for a delta-method Wald SE.
    cross = inv @ (sz.T @ sx) @ inv * len(d) / (len(d) - design.shape[1])
    wald = jump_z / jump_x
    wald_var = (cz[2, 2] / jump_x**2
                + jump_z**2 * cx[2, 2] / jump_x**4
                - 2*jump_z * cross[2, 2] / jump_x**3)
    local.append({"bandwidth_points": bandwidth, "n_below": int((d < 0).sum()),
                  "n_at_or_above": int((d >= 0).sum()),
                  "treated_at_or_above": int(x[keep][d >= 0].sum()),
                  "outcome_jump": jump_z, "outcome_jump_se": float(math.sqrt(cz[2, 2])),
                  "treatment_jump": jump_x, "treatment_jump_se": float(math.sqrt(cx[2, 2])),
                  "wald_ratio": wald, "wald_se": float(math.sqrt(max(0, wald_var)))})

# With only the 0--100 range for a student's no-tutoring final score,
# the treated group's average untreated final score could range from 0 to 100.
att_lower = groups["attended"]["mean_end_score"] - 100
att_upper = groups["attended"]["mean_end_score"]
result = {
    "source": str(SOURCE.relative_to(BASE)), "rows": len(rows),
    "validation": "2000 complete rows; x binary with 600 treated; score ranges valid",
    "cutoff_min_treated_y": cutoff,
    "y_range": [float(y.min()), float(y.max())],
    "groups": groups,
    "raw_mean_gain_difference_treated_minus_control": raw,
    "raw_difference_se": raw_se,
    "adjusted_associations": adjusted,
    "local_linear_triangular_kernel": local,
    "att_bounds_from_score_range_only": [att_lower, att_upper],
    "interpretation": "Observed comparisons and cutoff estimates do not identify the ATT without extra assumptions."
}
(OUT / "analysis.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
lines = [
    f"Rows {len(rows)}; treated {int(x.sum())}; min treated y {cutoff:.6f}",
    f"Mean gain treated {groups['attended']['mean_z']:.4f}; untreated {groups['did_not_attend']['mean_z']:.4f}",
    f"Raw gain difference {raw:.4f} (SE {raw_se:.4f})",
    f"ATT bounds based only on final-score range: [{att_lower:.4f}, {att_upper:.4f}] points",
    "Cutoff estimates: bandwidth, counts below/above, treatment jump, gain jump, ratio, ratio SE"
]
for r in local:
    lines.append(f"{r['bandwidth_points']:>2}  {r['n_below']:>3}/{r['n_at_or_above']:<3}  "
                 f"{r['treatment_jump']:.3f}  {r['outcome_jump']:.3f}  "
                 f"{r['wald_ratio']:.3f}  {r['wald_se']:.3f}")
(OUT / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
