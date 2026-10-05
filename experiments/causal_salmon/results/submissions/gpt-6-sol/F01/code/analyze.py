"""Analyze the complete attached study data; write machine-readable results."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "upload" / "data(20261004-171728).csv"
OUT = ROOT / "submission" / "results"
OUT.mkdir(parents=True, exist_ok=True)

d = pd.read_csv(DATA)
assert list(d.columns) == ["x", "y", "z"]
assert len(d) == 2000 and not d.isna().any().any()
assert set(d.x.unique()) == {0, 1} and int(d.x.sum()) == 600
assert d.y.between(0, 100).all() and (d.y + d.z).between(0, 100).all()

t, u = d.loc[d.x == 1], d.loc[d.x == 0]
c = float(t.y.min())
assert not ((d.x == 1) & (d.y < c)).any()
treated_end = t.y + t.z
summary = {
    "n_total": len(d), "n_treated": len(t), "n_untreated": len(u),
    "minimum_treated_start_score": c,
    "mean_gain_treated": float(t.z.mean()),
    "mean_gain_untreated": float(u.z.mean()),
    "unadjusted_mean_difference": float(t.z.mean() - u.z.mean()),
    "mean_start_score_treated": float(t.y.mean()),
    "mean_start_score_untreated": float(u.y.mean()),
    "mean_observed_end_score_treated": float(treated_end.mean()),
    "observed_end_score_range_treated": [float(treated_end.min()), float(treated_end.max())],
    "logical_att_lower_bound": float(treated_end.mean() - 100),
    "logical_att_upper_bound": float(treated_end.mean()),
    "bound_interpretation": "For each treated student, unobserved no-tutoring end score could be any value in [0,100]. These bounds use only the score scale and are not confidence intervals."
}


def local_jump(data, cutoff, bandwidth, outcome):
    """Separate local linear trends, triangular kernel; return right-left jump."""
    q = data.loc[(data.y >= cutoff - bandwidth) & (data.y <= cutoff + bandwidth)]
    v = q.y.to_numpy() - cutoff
    right = (v >= 0).astype(int)
    design = np.column_stack((np.ones(len(q)), right, v, v * right))
    weights = 1 - np.abs(v) / bandwidth
    sw = np.sqrt(weights)
    coefficients = np.linalg.lstsq(design * sw[:, None], q[outcome].to_numpy() * sw, rcond=None)[0]
    return float(coefficients[1]), int(sum(v < 0)), int(sum(v >= 0))


rows = []
for h in [2.0, 3.0, 4.0, 5.0, 6.0, 8.0]:
    jx, below, above = local_jump(d, c, h, "x")
    jz, _, _ = local_jump(d, c, h, "z")
    rows.append({"bandwidth_points": h, "n_below": below, "n_above": above,
                 "attendance_jump": jx, "gain_jump_points": jz,
                 "local_wald_points": jz / jx if abs(jx) > 1e-10 else None})
rd = pd.DataFrame(rows)
rd.to_csv(OUT / "cutoff_sensitivity.csv", index=False, float_format="%.10f")

# A conditional bootstrap for the illustrative local-Wald analysis. It fixes the
# data-derived minimum treated score as cutoff, so is not a complete inferential
# procedure for the original sample-dependent admission threshold.
h = 4.0
rng = np.random.default_rng(20261004)
sample = d.loc[(d.y >= c - h) & (d.y <= c + h)].reset_index(drop=True)
vals = []
for _ in range(2000):
    b = sample.iloc[rng.integers(0, len(sample), len(sample))]
    try:
        jx, left, right = local_jump(b, c, h, "x")
        jz, _, _ = local_jump(b, c, h, "z")
        if left >= 10 and right >= 10 and jx > .05:
            vals.append(jz / jx)
    except (np.linalg.LinAlgError, ValueError, ZeroDivisionError):
        pass
bootstrap = {
    "bandwidth_points": h, "replicates_attempted": 2000,
    "replicates_retained": len(vals),
    "percentile_interval_95_conditional": np.quantile(vals, [.025, .975]).tolist(),
    "caveat": "Illustrative row bootstrap fixes a cutoff chosen from the same sample and does not establish identification of the full attendee average."
}
summary["illustrative_local_rd_bootstrap"] = bootstrap

with (OUT / "summary.json").open("w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, allow_nan=False)
    f.write("\n")
print(json.dumps(summary, indent=2))
print("\nCutoff sensitivity:\n" + rd.to_string(index=False))
