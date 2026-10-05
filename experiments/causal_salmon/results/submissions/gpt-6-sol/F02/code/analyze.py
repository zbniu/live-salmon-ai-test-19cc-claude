"""Descriptive and local threshold analyses of the complete supplied CSV."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "upload/data(20261004-071210).csv"
OUT = ROOT / "submission/results"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(SOURCE)
assert list(df.columns) == ["x", "y", "z"]
assert len(df) == 2000 and df.notna().all().all()
assert set(df.x.unique()) == {0, 1} and int(df.x.sum()) == 600
assert df.y.between(0, 100).all()

c = float(df.loc[df.x == 1, "y"].min())
def summary(frame):
    return {"n": len(frame), "treated": int(frame.x.sum()),
            "mean_y": float(frame.y.mean()) if len(frame) else None,
            "mean_z": float(frame.z.mean()) if len(frame) else None,
            "sd_z": float(frame.z.std()) if len(frame) > 1 else None}

results = {
    "data": {"rows": len(df), "columns": list(df.columns), "missing": df.isna().sum().to_dict()},
    "threshold_minimum_treated_y": c,
    "groups": {str(x): summary(df[df.x == x]) for x in (0, 1)},
    "raw_mean_z_difference_treated_minus_untreated": float(df.loc[df.x == 1, "z"].mean() - df.loc[df.x == 0, "z"].mean()),
    "above_threshold": summary(df[df.y >= c]),
    "below_threshold": summary(df[df.y < c]),
    "baseline_bins": [],
    "local_linear": [],
}
for lo, hi in [(0, 40), (40, 50), (50, 60), (60, 65), (65, 70),
               (70, 75), (75, 80), (80, 90), (90, 101)]:
    b = df[(df.y >= lo) & (df.y < hi)]
    results["baseline_bins"].append({"range": [lo, hi], **summary(b)})

# The intercept jump of a two-sided local-linear fit gives the reduced form
# and first stage. Its ratio is a local Wald estimate, not the treated ATT.
for h in (3, 5, 7.5, 10, 15, 20):
    b = df[(df.y >= c-h) & (df.y <= c+h)].copy()
    centered = b.y.to_numpy() - c
    right = (centered >= 0).astype(float)
    X = np.column_stack((np.ones(len(b)), centered, right, centered*right))
    def robust_fit(outcome):
        beta = np.linalg.lstsq(X, outcome, rcond=None)[0]
        residual = outcome - X @ beta
        bread = np.linalg.inv(X.T @ X)
        meat = X.T @ ((residual[:, None] ** 2) * X)
        variance = bread @ meat @ bread * len(b)/(len(b)-X.shape[1])
        return beta, np.sqrt(np.maximum(np.diag(variance), 0))
    bx, sex = robust_fit(b.x.to_numpy())
    bz, sez = robust_fit(b.z.to_numpy())
    fx, fz = float(bx[2]), float(bz[2])
    results["local_linear"].append({
        "bandwidth": h, "n": len(b), "n_left": int((right == 0).sum()),
        "n_right": int(right.sum()), "first_stage_jump": fx,
        "first_stage_se_HC1": float(sex[2]),
        "outcome_jump": fz, "outcome_jump_se_HC1": float(sez[2]),
        "wald_ratio": fz/fx if fx else None,
    })

with (OUT / "analysis.json").open("w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, allow_nan=False)
print(json.dumps(results, indent=2))
