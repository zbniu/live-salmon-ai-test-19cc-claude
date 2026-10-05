"""Analyze the complete randomized study CSV; write reproducible results."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


def ols_hc2(x, outcome):
    """OLS coefficients and heteroskedastic robust HC2 standard errors."""
    x = np.asarray(x, dtype=float)
    outcome = np.asarray(outcome, dtype=float)
    inv = np.linalg.inv(x.T @ x)
    coefficients = inv @ x.T @ outcome
    residuals = outcome - x @ coefficients
    leverage = np.sum((x @ inv) * x, axis=1)
    weighted_x = x * np.sqrt(residuals**2 / (1 - leverage))[:, None]
    covariance = inv @ (weighted_x.T @ weighted_x) @ inv
    return coefficients, np.sqrt(np.diag(covariance))

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "upload/data(20261004-071245).csv"
OUT = ROOT / "submission/results"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA)
assert list(df.columns) == ["x", "y", "z"]
assert len(df) == 2000 and not df.isna().any().any()
assert set(df.x.unique()) == {0, 1}
assert (df.x == 1).sum() == 600 and (df.x == 0).sum() == 1400

t = df.loc[df.x == 1]
c = df.loc[df.x == 0]
nt, nc = len(t), len(c)
mt, mc = t.z.mean(), c.z.mean()
st, sc = t.z.std(ddof=1), c.z.std(ddof=1)
effect = mt - mc
se = np.sqrt(st**2 / nt + sc**2 / nc)
df_welch = (st**2 / nt + sc**2 / nc)**2 / (
    (st**2 / nt)**2 / (nt - 1) + (sc**2 / nc)**2 / (nc - 1)
)
ci = stats.t.interval(0.95, df_welch, loc=effect, scale=se)
p = 2 * stats.t.sf(abs(effect / se), df_welch)

# Pre-specified covariate is not stated. ANCOVA is a precision/sensitivity check.
ancova_b, ancova_se = ols_hc2(np.column_stack([np.ones(len(df)), df.x, df.y]), df.z)
# Allow a different linear baseline association in each randomized group.
yc = df.y - df.y.mean()
interaction_b, interaction_se = ols_hc2(
    np.column_stack([np.ones(len(df)), df.x, yc, df.x * yc]), df.z
)


def normal_ci(value, standard_error):
    return [float(value - stats.norm.ppf(.975) * standard_error),
            float(value + stats.norm.ppf(.975) * standard_error)]

results = {
    "data": {
        "rows": len(df), "columns": list(df.columns), "missing_cells": int(df.isna().sum().sum()),
        "n_treated": nt, "n_control": nc,
        "baseline_mean_treated": float(t.y.mean()), "baseline_mean_control": float(c.y.mean()),
        "baseline_difference": float(t.y.mean() - c.y.mean()),
        "baseline_sd_treated": float(t.y.std(ddof=1)), "baseline_sd_control": float(c.y.std(ddof=1)),
        "baseline_range": [float(df.y.min()), float(df.y.max())],
        "change_range": [float(df.z.min()), float(df.z.max())],
        "followup_outside_0_100": int(((df.y + df.z < 0) | (df.y + df.z > 100)).sum()),
    },
    "primary_unadjusted": {
        "mean_change_treated": float(mt), "mean_change_control": float(mc),
        "sd_change_treated": float(st), "sd_change_control": float(sc),
        "difference_points": float(effect), "standard_error": float(se),
        "welch_df": float(df_welch), "ci95": list(map(float, ci)), "two_sided_p": float(p),
    },
    "ancova_y": {
        "x_coefficient": float(ancova_b[1]), "hc2_se": float(ancova_se[1]),
        "ci95": normal_ci(ancova_b[1], ancova_se[1]),
        "p": float(2 * stats.norm.sf(abs(ancova_b[1] / ancova_se[1]))),
        "y_coefficient": float(ancova_b[2]),
    },
    "linear_interaction": {
        "x_at_overall_mean_y": float(interaction_b[1]),
        "hc2_se": float(interaction_se[1]),
        "ci95": normal_ci(interaction_b[1], interaction_se[1]),
        "x_y_interaction": float(interaction_b[3]),
        "interaction_p": float(2 * stats.norm.sf(abs(interaction_b[3] / interaction_se[3]))),
    },
}

(OUT / "analysis.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print(json.dumps(results, indent=2))
