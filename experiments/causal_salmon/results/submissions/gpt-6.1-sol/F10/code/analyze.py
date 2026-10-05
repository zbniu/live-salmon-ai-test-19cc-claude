"""Analyze only the supplied study files; no network calls or imputation.

Run from the workspace root with the bundled Python runtime.
The target is the finite-study average treatment effect on the treated (ATT).
Regressions are explicitly descriptive, not identified causal estimators.
"""
from pathlib import Path
import hashlib
import json
import platform
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
INPUT = ROOT / "inputs" / "data.csv"
df = pd.read_csv(INPUT)
assert list(df.columns) == ["x", "y", "z"]
assert len(df) == 2000
assert not df.isna().any().any()
assert np.isfinite(df.to_numpy()).all()
assert set(df.x.unique()) == {0, 1}
assert int(df.x.sum()) == 600
assert df.y.between(0, 100).all()
df["end_score"] = df.y + df.z
assert df.end_score.between(0, 100).all()
treated = df.loc[df.x == 1].copy()
control = df.loc[df.x == 0].copy()

summary = df.groupby("x").agg(
    n=("z", "size"), mean_y=("y", "mean"), min_y=("y", "min"),
    max_y=("y", "max"), mean_z=("z", "mean"), sd_z=("z", "std"),
    mean_end_score=("end_score", "mean"), min_end_score=("end_score", "min"),
    max_end_score=("end_score", "max"),
)
summary.to_csv(OUT / "group_summary.csv", float_format="%.12g")

raw = float(treated.z.mean() - control.z.mean())
x = df.x.to_numpy(dtype=float)
y_scaled = (df.y.to_numpy(dtype=float) - df.y.mean()) / df.y.std(ddof=0)
z = df.z.to_numpy(dtype=float)
associations = [{"model": "Unadjusted mean gain difference", "x_coefficient": raw,
                 "interpretation": "descriptive association; not ATT"}]
for degree in [1, 3]:
    design = np.column_stack([np.ones(len(df)), x] +
                             [y_scaled ** k for k in range(1, degree + 1)])
    coefficients, _, rank, _ = np.linalg.lstsq(design, z, rcond=None)
    assert rank == design.shape[1]
    associations.append({"model": f"OLS with common degree-{degree} polynomial in y",
                         "x_coefficient": float(coefficients[1]),
                         "interpretation": "model-dependent adjusted association; not ATT"})
pd.DataFrame(associations).to_csv(OUT / "associations.csv", index=False,
                                 float_format="%.12g")

# All rows enter these fixed-width bins. Empty treatment cells are left empty.
bins = pd.cut(df.y, bins=np.arange(0, 101, 10), include_lowest=True)
df.assign(y_bin=bins).groupby(["y_bin", "x"], observed=False).agg(
    n=("z", "size"), mean_y=("y", "mean"), mean_z=("z", "mean")
).to_csv(OUT / "score_bin_summary.csv", float_format="%.12g")

# For attendees, z(1) is observed. A 0-100 counterfactual end score implies
# -y <= z(0) <= 100-y; hence ATT in [mean(end(1))-100, mean(end(1))].
lower = float(treated.end_score.mean() - 100)
upper = float(treated.end_score.mean())

# Explicit observationally indistinguishable counterfactual completions.
# They are hypothetical possibilities, never estimated or claimed actual.
# Setting end(0) to 0 or 100 attains the scale-only endpoint bounds.
potential = pd.DataFrame({
    "source_row_1based": treated.index.to_numpy() + 1,
    "y": treated.y.to_numpy(), "observed_z1": treated.z.to_numpy(),
    "observed_end1": treated.end_score.to_numpy(),
    "end0_zero_effect": treated.end_score.to_numpy(),
    "end0_lower_bound": np.full(len(treated), 100.0),
    "end0_upper_bound": np.zeros(len(treated)),
})
margin = float(min(treated.end_score.min(), 100 - treated.end_score.max()))
delta = min(1.0, margin / 2.0)
assert delta > 0
potential["end0_positive_effect"] = potential.observed_end1 - delta
potential["end0_negative_effect"] = potential.observed_end1 + delta
for column in potential.columns:
    if column.startswith("end0_"):
        assert potential[column].between(0, 100).all()
potential.to_csv(OUT / "counterfactual_completions.csv", index=False,
                 float_format="%.17g")

min_treated_y = float(treated.y.min())
support = {
    "smallest_observed_attendee_start_score": min_treated_y,
    "nonattendees_below_that_score": int((control.y < min_treated_y).sum()),
    "nonattendees_at_or_above_that_score": int((control.y >= min_treated_y).sum()),
    "note": "This is an empirical support boundary, not an independently observed admission cutoff.",
}
results = {
    "estimand": "mean[z(1)-z(0)] among the 600 actual attendees",
    "causal_effect_identified": False,
    "validation": {"rows": len(df), "attendees": len(treated),
                   "nonattendees": len(control), "missing_values": int(df.isna().sum().sum()),
                   "all_start_and_observed_end_scores_in_0_100": True,
                   "rows_dropped": 0},
    "group_summary": summary.reset_index().to_dict(orient="records"),
    "associations": associations,
    "support": support,
    "scale_only_ATT_bounds_points": [lower, upper],
    "hypothetical_constant_ATT_examples_points": [0.0, delta, -delta],
    "counterfactuals_are_hypothetical_not_estimated": True,
    "versions": {"python": platform.python_version(), "numpy": np.__version__,
                 "pandas": pd.__version__},
    "inputs": {path.name: {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                           "size_bytes": path.stat().st_size}
               for path in sorted((ROOT / "inputs").iterdir())},
}
(OUT / "analysis_summary.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

report = f"""# Does tutoring increase score gains for its attendees?

**Answer: the supplied material does not establish whether tutoring increased the attendees' gains, or by how much.** The average causal effect for the 600 attendees is not identified. No numerical point estimate is adopted as the answer to the causal research question.

## What the complete data show

All 2,000 students were analyzed: 600 attended and 1,400 did not. The three supplied variables had no missing values, and no rows were excluded. Starting scores and reconstructed observed end scores (`y + z`) were within 0–100.

| Observed group | Students | Mean starting score | Mean score gain |
| --- | ---: | ---: | ---: |
| Attended | 600 | {treated.y.mean():.3f} | {treated.z.mean():.3f} |
| Did not attend | 1,400 | {control.y.mean():.3f} | {control.z.mean():.3f} |

The observed mean gain difference is **{raw:.3f} points** (attendees minus nonattendees). This is an association between attendance and gain, **not the causal effect asked for**. As descriptive checks, ordinary least squares using all rows gives an attendance coefficient of {associations[1]['x_coefficient']:.3f} points after linear adjustment for starting score, and {associations[2]['x_coefficient']:.3f} points with a common cubic starting-score curve. These coefficients depend on the adjustment model and do not remove possible selection on unrecorded circumstances. No causal significance test or causal confidence interval is justified by those fits.

## Why the causal answer is undetermined

Let `z(1)` and `z(0)` denote a student's gain with and without tutoring. The question's target is the average of `z(1) - z(0)` over the 600 actual attendees. Their `z(1)` values are observed; their `z(0)` values are not.

The application score combined starting score, unrecorded circumstances, and an independent random number. The top 900 application scores determined applicants; starting-score ranking among applicants then determined the 600 attendees. The independent random component does not make attendance a randomized treatment: applicants were selected using other characteristics, and the application scores, applicant indicators, and random numbers are unavailable. The study does not establish that those unrecorded circumstances are unrelated to untreated gains, or that attendance is independent of potential gains after conditioning on starting score. Every student's having some chance of applying does not establish that independence. Adjustment for `y` therefore does not identify the effect.

There are {support['nonattendees_at_or_above_that_score']} nonattendees at or above the smallest observed attendee starting score ({min_treated_y:.3f}); attendance is not simply a deterministic threshold in starting score for all students. A possible discontinuity analysis would require further assumptions about continuity of potential outcomes and applicant selection at a cutoff. Those assumptions are not supplied or established by these data. Even if justified, a local cutoff effect would not by itself identify the average effect over all 600 attendees. The uniform class, no switching, no interference, complete records, and blinded outcome recording are useful design features, but do not supply the missing counterfactual comparison.

The ambiguity can be made concrete without changing any observed row or the described attendance process. For attendees, set each unobserved end score without tutoring equal to their observed end score: the average effect is zero. Alternatively set it {delta:.3f} points lower or {delta:.3f} points higher: the average effects are respectively +{delta:.3f} and −{delta:.3f} points. All these counterfactual end scores stay within 0–100. The unobserved treated outcomes of nonattendees can also be completed within the scale, with the same treatment rule and no interference. These are logically compatible possibilities, not estimates of the hidden data-generating process.

## Numerical information about the causal target

The stated 0–100 end-score scale gives only broad logical bounds. For an attendee, an untreated end score can range from 0 to 100, so their effect can range from `observed_end_score - 100` to `observed_end_score`. The mean observed end score among attendees is {treated.end_score.mean():.3f}. Thus the finite-study average causal effect can range from **{lower:.3f} to {upper:.3f} points** using the supplied scale restrictions alone. These bounds concern the research question's target; they are neither a confidence interval nor evidence of a positive effect. Both endpoints can be attained by assigning all attendees' untreated end scores to 100 or 0, respectively, without altering the observations. Harm, no effect, and benefit remain compatible with the supplied information.

## Reproducibility

Only the two supplied files were used as study evidence; no internet or external dataset was accessed. `code/analyze.py` generated the group summaries, descriptive regressions, score-bin summaries, logical bounds, and explicitly hypothetical counterfactual examples. Machine-readable outputs are in `results/`; input copies and their hashes are included, and `run_log.txt` records execution. The report's causal conclusion is non-identification, not the raw or adjusted association.
"""
(ROOT / "final_report.md").write_text(report, encoding="utf-8")
print(json.dumps({"rows_analyzed": len(df), "raw_gain_difference_points": raw,
                  "adjusted_associations": associations[1:],
                  "scale_only_ATT_bounds_points": [lower, upper],
                  "hypothetical_ATT_examples": [0, delta, -delta],
                  "causal_effect_identified": False}, indent=2))
print("Wrote final_report.md and six analysis output files in results/.")

