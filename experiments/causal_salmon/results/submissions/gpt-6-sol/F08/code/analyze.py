"""Analyze the complete simulated tutoring study from the two supplied files."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import SplineTransformer


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "upload" / "data(20261004-071337).csv"
OUT = ROOT / "submission" / "results"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA)
assert list(df.columns) == ["x", "y", "z"]
assert df.shape == (2000, 3) and not df.isna().any().any()
assert set(df.x.unique()) == {0, 1} and df.x.sum() == 600
assert df.y.between(0, 100).all()
assert (df.y + df.z).between(0, 100).all()

t = df.loc[df.x == 1].copy()
c = df.loc[df.x == 0].copy()
summary = {
    "n": len(df), "treated": len(t), "controls": len(c),
    "treated_y_range": [float(t.y.min()), float(t.y.max())],
    "control_y_range": [float(c.y.min()), float(c.y.max())],
    "mean_z_treated": float(t.z.mean()), "mean_z_controls": float(c.z.mean()),
    "unadjusted_difference": float(t.z.mean() - c.z.mean()),
    "mean_y_treated": float(t.y.mean()), "mean_y_controls": float(c.y.mean()),
}

# Each treated student has a nearby untreated peer on the baseline score.
tree = cKDTree(c[["y"]].to_numpy())
dist, ind = tree.query(t[["y"]].to_numpy(), k=1)
summary["nearest_control_y_distance"] = {
    "median": float(np.median(dist)), "p95": float(np.quantile(dist, .95)),
    "max": float(np.max(dist)),
}

bins = np.arange(0, 101, 5)
df["y_bin"] = pd.cut(df.y, bins, right=False, include_lowest=True)
by_bin = df.groupby(["y_bin", "x"], observed=False).agg(n=("z", "size"), mean_z=("z", "mean")).reset_index()
by_bin.to_csv(OUT / "baseline_bins.csv", index=False)

def spline_fit(control, knots):
    """Fit cubic B-spline control regression with fixed score quantile knots."""
    positions = np.quantile(c.y, np.linspace(0, 1, knots))[:, None]
    basis = SplineTransformer(degree=3, knots=positions, include_bias=False,
                              extrapolation="linear")
    design = basis.fit_transform(control[["y"]])
    reg = LinearRegression().fit(design, control.z)
    return basis, reg


def predict(fit, rows):
    basis, reg = fit
    return reg.predict(basis.transform(rows[["y"]]))


estimates = []
for knots in (4, 6, 8, 10, 12):
    fitted = spline_fit(c, knots)
    residual_effects = t.z.to_numpy() - predict(fitted, t)
    control_resid = c.z.to_numpy() - predict(fitted, c)
    estimates.append({
        "method": f"control cubic spline, {knots} quantile knots",
        "ATT": float(np.mean(residual_effects)),
        "control_R2": float(1 - np.sum(control_resid**2) / np.sum((c.z - c.z.mean())**2)),
        "control_RMSE": float(np.sqrt(np.mean(control_resid**2))),
    })

# Check the outcome pattern across treated scores without imposing a common effect.
fixed_knots = np.quantile(c.y, np.linspace(0, 1, 6))[:, None]
interaction_basis = SplineTransformer(degree=3, knots=fixed_knots,
                                      include_bias=False, extrapolation="linear")
B = interaction_basis.fit_transform(df[["y"]])
interaction_design = np.column_stack([B, df.x.to_numpy(), B * df.x.to_numpy()[:, None]])
interaction = LinearRegression().fit(interaction_design, df.z)
grid = pd.DataFrame({"y": [55, 60, 65, 70, 75, 80, 85, 90, 95]})
grid1 = grid.assign(x=1)
grid0 = grid.assign(x=0)
G = interaction_basis.transform(grid[["y"]])
grid["estimated_effect"] = interaction.predict(np.column_stack([G, np.ones(len(G)), G])) - interaction.predict(np.column_stack([G, np.zeros(len(G)), np.zeros_like(G)]))
grid.to_csv(OUT / "conditional_effects.csv", index=False)

# ATT is the treated mean minus the untreated conditional mean, standardized
# to the observed baseline scores of the 600 attendees. The application draw
# is independent of student characteristics; above the admission cutoff it
# provides untreated peers at the same y. Bootstrap the entire calculation.
base = estimates[1]["ATT"]  # six knots preselected as primary smooth adjustment
rng = np.random.default_rng(20261004)
boot = []
for _ in range(2000):
    cb = c.iloc[rng.integers(len(c), size=len(c))]
    tb = t.iloc[rng.integers(len(t), size=len(t))]
    fitted = spline_fit(cb, 6)
    boot.append(float((tb.z.to_numpy() - predict(fitted, tb)).mean()))
boot = np.array(boot)
summary["primary_ATT"] = base
summary["bootstrap_percentile_95_CI"] = np.quantile(boot, [.025, .975]).tolist()
summary["bootstrap_SE"] = float(boot.std(ddof=1))
summary["bootstrap_draws"] = len(boot)

# A local comparison allows all high-score controls to be reused. Report
# proximity diagnostics as well as the comparison, since close matches alone
# do not prove balance on unmeasured potential outcomes.
for k in (1, 5, 10):
    d, ix = tree.query(t[["y"]].to_numpy(), k=k)
    peer_mean = c.z.to_numpy()[ix].mean(axis=1) if k > 1 else c.z.to_numpy()[ix]
    estimates.append({
        "method": f"{k} nearest controls on y, with replacement",
        "ATT": float(np.mean(t.z.to_numpy() - peer_mean)),
        "median_farthest_y_gap": float(np.median(d[:, -1] if k > 1 else d)),
        "p95_farthest_y_gap": float(np.quantile(d[:, -1] if k > 1 else d, .95)),
    })

pd.DataFrame(estimates).to_csv(OUT / "estimates.csv", index=False)
(OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
print("\nEstimates:\n" + pd.DataFrame(estimates).to_string(index=False))
print("\nConditional-effect grid:\n" + grid.to_string(index=False))
