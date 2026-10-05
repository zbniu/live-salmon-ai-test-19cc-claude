"""Estimate the average tutoring effect for the 600 attendees.

The study's independent application random number makes applicant status
independent of potential gains conditional on the start score. Above the
lowest admitted start score, applicant status equals attendance; hence
untreated students at the same start score identify the counterfactual.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from sklearn.preprocessing import SplineTransformer

ROOT = Path(__file__).resolve().parents[2]
df = pd.read_csv(ROOT / "upload/data(20261004-071413).csv")
treated = df.loc[df.x.eq(1), ["y", "z"]].reset_index(drop=True)
lower = treated.y.min()
upper = treated.y.max()
control = df.loc[df.x.eq(0) & df.y.between(lower, upper), ["y", "z"]].reset_index(drop=True)


def features(y, kind):
    y = np.asarray(y, dtype=float).reshape(-1, 1)
    if kind == "linear":
        return np.column_stack((np.ones(len(y)), y[:, 0] - 65))
    if kind == "quadratic":
        v = (y[:, 0] - 65) / 10
        return np.column_stack((np.ones(len(y)), v, v * v))
    knots_count = int(kind.removeprefix("spline"))
    # Fixed boundaries and knots keep the bootstrap's fitted target identical.
    knots = np.linspace(58, 75, knots_count).reshape(-1, 1)
    basis = SplineTransformer(degree=3, knots=knots, include_bias=False).fit(y)
    return np.column_stack((np.ones(len(y)), basis.transform(y)))


def estimate(t, c, kind):
    # Construct on the pooled score vector so basis columns agree exactly.
    y = np.concatenate((c.y.to_numpy(), t.y.to_numpy()))
    B = features(y, kind)
    Bc, Bt = B[:len(c)], B[len(c):]
    beta = np.linalg.lstsq(Bc, c.z.to_numpy(), rcond=None)[0]
    counterfactual = Bt @ beta
    return float(np.mean(t.z.to_numpy() - counterfactual)), float(np.mean(counterfactual))


models = {}
for kind in ("linear", "quadratic", "spline4", "spline5", "spline6"):
    att, mean_z0 = estimate(treated, control, kind)
    models[kind] = {"att": att, "mean_counterfactual_z0": mean_z0}

# Primary: cubic B-spline with five equally spaced knots over the observed
# common range. Separate resampling by treatment status accounts for variation
# in both observed treated gains and the estimated control response curve.
rng = np.random.default_rng(20261004)
boot = np.empty(2000)
for b in range(len(boot)):
    t = treated.iloc[rng.integers(0, len(treated), len(treated))]
    c = control.iloc[rng.integers(0, len(control), len(control))]
    boot[b], _ = estimate(t, c, "spline5")

# A direct score match is an additional check on functional form. Matching
# is with replacement, and is not used for the primary uncertainty interval.
dist, idx = cKDTree(control[["y"]].to_numpy()).query(treated[["y"]].to_numpy())
matched_att = float(np.mean(treated.z.to_numpy() - control.z.to_numpy()[idx]))

result = {
    "estimand": "average effect of attendance on score gain for the 600 attendees (ATT), points",
    "sample": {"total": len(df), "attendees": len(treated), "nonattendees": int((df.x == 0).sum()),
               "nonattendees_in_attendee_score_range": len(control),
               "attendee_score_range": [float(lower), float(upper)],
               "controls_in_range_score_range": [float(control.y.min()), float(control.y.max())]},
    "unadjusted_difference": float(treated.z.mean() - df.loc[df.x.eq(0), "z"].mean()),
    "observed_mean_gain_attendees": float(treated.z.mean()),
    "models": models,
    "primary": {"model": "spline5", "att": models["spline5"]["att"],
                "mean_counterfactual_gain_without_tutoring": models["spline5"]["mean_counterfactual_z0"],
                "bootstrap_replicates": len(boot),
                "bootstrap_seed": 20261004,
                "bootstrap_standard_error": float(boot.std(ddof=1)),
                "percentile_95_interval": [float(v) for v in np.quantile(boot, [.025, .975])],
                "bootstrap_two_sided_p_approx": float(2 * min(np.mean(boot <= 0), np.mean(boot >= 0)))},
    "nearest_score_match": {"att": matched_att,
                            "median_absolute_score_gap": float(np.median(dist)),
                            "max_absolute_score_gap": float(np.max(dist))},
}
out = ROOT / "submission/results/02_estimate.json"
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {out.relative_to(ROOT)}; ATT={result['primary']['att']:.6f}; 95% bootstrap interval={result['primary']['percentile_95_interval']}")
