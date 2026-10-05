"""Logical ATT bounds from the 0–100 follow-up scale; no causal model imposed."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
df = pd.read_csv(ROOT / "upload/data(20261004-071210).csv")
t = df.loc[df.x == 1].copy()
t["followup"] = t.y + t.z
assert df.assign(followup=df.y + df.z).followup.between(0, 100).all()

# Each treated unit's unobserved change without Q can range from -y to 100-y.
# ATT = mean(observed z - counterfactual untreated change).
result = {
    "treated_n": len(t),
    "treated_observed_followup_range": [float(t.followup.min()), float(t.followup.max())],
    "treated_mean_followup": float(t.followup.mean()),
    "att_lower_bound_points": float((t.z + t.y - 100).mean()),
    "att_upper_bound_points": float((t.z + t.y).mean()),
    "constructive_examples": {
        "zero_effect": "Set untreated potential change equal to observed z for every treated unit.",
        "positive_three_points": "Set untreated potential follow-up equal to observed follow-up minus 3 for every treated unit.",
        "negative_three_points": "Set untreated potential follow-up equal to observed follow-up plus 3 for every treated unit.",
        "all_examples_feasible": bool(t.followup.between(3, 97).all()),
    },
}
path = ROOT / "submission/results/bounds.json"
path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
