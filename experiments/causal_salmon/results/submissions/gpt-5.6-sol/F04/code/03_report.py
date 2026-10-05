"""Write the standalone report from the saved, actually executed results."""
from pathlib import Path
import json
import shutil
import pandas as pd

root = Path(__file__).resolve().parents[1]
r = json.loads((root/'results'/'att_inference.json').read_text())
all_results = json.loads((root/'results'/'estimates.json').read_text())
w = all_results['unadjusted']
a = all_results['adjusted_sensitivity']
s = pd.read_csv(root/'results'/'group_summary.csv').set_index('x')
report = f"""# Effect of arrangement Q on change

The supplied randomized study provides strong evidence that receiving arrangement Q **increased change `z` on average among its recipients**. The adopted estimate is **{r['estimate_points']:.2f} points**, with an approximate **95% randomization confidence interval of {r['ci95_lower']:.2f} to {r['ci95_upper']:.2f} points**. This average causal effect, rather than the recipients' total observed change, answers the research question. The data do not reveal the exact counterfactual effect for these particular recipients or establish that every recipient benefited.

## Data and causal comparison

Only the supplied `STUDY_DESCRIPTION(5).md` and the complete `data(5).csv` were used. All 2,000 rows were analyzed; no observations were excluded and there were no missing values. Exactly 600 units received Q and 1,400 did not.

| Group | Units | Mean baseline `y` | Mean change `z` | SD of change |
|---|---:|---:|---:|---:|
| Received Q | 600 | {s.loc[1,'baseline_mean']:.3f} | {s.loc[1,'change_mean']:.3f} | {s.loc[1,'change_sd']:.3f} |
| Did not receive Q | 1,400 | {s.loc[0,'baseline_mean']:.3f} | {s.loc[0,'change_mean']:.3f} | {s.loc[0,'change_sd']:.3f} |

The primary estimate is the difference in mean changes: {s.loc[1,'change_mean']:.6f} minus {s.loc[0,'change_mean']:.6f} = {r['estimate_points']:.6f} points. The 11.10-point increase observed within the Q group is not itself Q's effect, because controls also improved substantially.

The study description states that the 600 recipients were selected by an equal-chance random draw using no unit information. It also establishes full adherence, no effects on other units, consistent measurement, blinded follow-up recording, and complete observation. These facts support treating the control group as a randomized comparison for recipients' changes without Q. No assumption that all units have the same treatment effect is needed for the primary point estimate.

## Uncertainty and target

The target is the average of `z(1) - z(0)` over the 600 actual recipients, where `z(1)` and `z(0)` denote change with and without Q. Each recipient's `z(0)` is unobserved. Under the stated random assignment, the difference in observed means is unbiased, over repeated draws, for this recipient-average effect: its estimation error is the treated-minus-control difference in `z(0)`.

For this target, the randomization variance of that error is `(1/600 + 1/1400) × S0²`, where `S0²` is the finite-study variance of untreated potential changes. The observed control sample variance, {r['untreated_potential_outcome_variance_estimated_from_controls']:.6f}, estimates `S0²`. This yields a standard error of {r['se_randomization_ATT']:.6f} points. A large-sample normal interval gives the adopted 95% interval above. Its coverage is approximate over repeated random assignments, for the recipients selected in each draw; it is not an exact reconstruction of these recipients' missing outcomes.

As a conventional two-group check, a Welch analysis gives the same {w['estimate']:.2f}-point estimate, a 95% interval of {w['ci95_lower']:.2f} to {w['ci95_upper']:.2f}, and a two-sided p-value of {w['p_two_sided']:.3g}. Its standard error uses both arms' observed variances; the primary interval instead uses the randomization error appropriate to the recipient-average target. Both intervals lie above zero.

## Baseline adjustment and limits

Recipients' mean baseline was slightly lower. Exploratory baseline-adjusted regressions allowed separate baseline trends in each arm and averaged the fitted contrasts over the actual recipients' baseline values. Linear, quadratic, and cubic trends gave estimates of {a[0]['estimate']:.3f}, {a[1]['estimate']:.3f}, and {a[2]['estimate']:.3f} points, respectively. The linear model's HC3 robust interval was {a[0]['ci95_lower']:.2f} to {a[0]['ci95_upper']:.2f} points. These model-based sensitivity results support the positive conclusion; they do not replace the adopted design-based estimate or identify individual effects. No model was selected by its p-value.

The supported conclusion is an average causal increase of about **1.11 points** for Q recipients in this study, with the uncertainty stated above. The supplied material does not establish exact individual effects, a common effect across units, persistence beyond the measured follow-up, or effects in an external population.
"""
(root/'final_report.md').write_text(report, encoding='utf-8')
inputs = root/'inputs'
inputs.mkdir(exist_ok=True)
for name in ['data(5).csv', 'STUDY_DESCRIPTION(5).md']:
    shutil.copy2(root.parent/'upload'/name, inputs/name)
(root/'README.md').write_text("""# Execution archive

The report is final_report.md. Numerical results and actual stdout/stderr are
in results/. The append-only analysis execution record is run_log.txt.

code/01_analysis_initial.py is the exact first attempted analysis; it failed
on importing the unavailable statsmodels package, before data analysis.
code/01_analysis.py is the corrected analysis actually executed, implementing
OLS and HC3 covariance with NumPy. code/02_att_inference.py computes the
recipient-average randomization interval and independent arithmetic checks.
code/03_report.py writes the report from the saved results. code/run_step.py
records execution. code/04_package.py packages and verifies the deliverables.

inputs/ contains byte-for-byte copies of the two supplied sources. To reproduce
the successful analysis in a new directory, place these files in an upload/
directory alongside submission/ (the original scripts retain their executed
paths). With Python, NumPy, pandas and SciPy available, run from the parent:

    python submission/code/run_step.py submission/code/01_analysis.py rerun_analysis
    python submission/code/run_step.py submission/code/02_att_inference.py rerun_att
    python submission/code/run_step.py submission/code/03_report.py rerun_report

The failed initial version is retained for audit, not required for rerunning.
No internet access is required.
""", encoding='utf-8')
readback = (root/'final_report.md').read_text(encoding='utf-8')
assert readback.strip() and '1.11' in readback and '0.70 to 1.52' in readback
assert readback == report
print(readback)
print('Report readback passed; original input copies and README saved.')
