"""Write the standalone report from retained, actually executed results."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'submission/results'
analysis=json.loads((OUT/'analysis_results.json').read_text(encoding='utf-8'))
recipient=json.loads((OUT/'recipient_inference.json').read_text(encoding='utf-8'))
p=analysis['primary']
b=analysis['baseline']
m=analysis['baseline_adjusted_models']
s=analysis['stratified_sensitivity']
report=f'''# Effect of arrangement Q on change

The data provide strong statistical evidence that arrangement Q increased **average change `z` among the 600 recipients**. The numerical answer adopted for the research question is an estimated increase of **{recipient['adopted_estimate']:.3f} points**, with an **approximate 95% confidence interval of {recipient['approximate_95_ci_low']:.3f} to {recipient['approximate_95_ci_high']:.3f} points**. This estimates the additional change caused by Q, beyond the change that would have occurred without Q. It does not establish that every recipient benefited.

## Data and causal comparison

Only the supplied study description and complete CSV were used. All 2,000 rows were analyzed: 600 units received Q and 1,400 did not. The columns and assignment counts matched the description, and all values were finite and nonmissing. No units were excluded.

| Observed quantity | Q recipients | Controls |
|---|---:|---:|
| Number of units | {p['treated_n']} | {p['control_n']} |
| Mean baseline `y` | {b['treated_mean']:.3f} | {b['control_mean']:.3f} |
| Mean change `z` | {p['treated_mean_change']:.3f} | {p['control_mean_change']:.3f} |
| Standard deviation of change | 4.524 | 4.239 |

The adopted estimate is the difference in mean change: {p['treated_mean_change']:.6f} − {p['control_mean_change']:.6f} = {recipient['adopted_estimate']:.6f} points. The recipients' observed increase of 11.104 points is not itself Q's estimated effect: controls also increased by 9.994 points.

The study description establishes that exactly 600 units were selected by an equal-probability random draw using no unit information. All selected units received Q, there was no switching or interference, measurement was uniform, follow-up recorders were blinded, and all units were retained. These features justify using the control group to estimate what recipients' changes would have been without Q. Baseline adjustment is not needed to remove treatment-selection confounding in this design.

## Uncertainty for the recipients' average effect

Let `z_i(1)` and `z_i(0)` denote a unit's changes with and without Q. The target is the mean of `z_i(1) − z_i(0)` over the actual 600 recipients. For the unadjusted estimate, estimation error equals the recipients' mean `z_i(0)` minus the controls' mean `z_i(0)`. Under the complete random draw, that error has mean zero and variance `(1/600 + 1/1400) × S_0²`, where `S_0²` is the finite-study variance of changes without Q.

The control sample variance, {recipient['control_sample_variance']:.6f}, estimates `S_0²`. It gives a recipient-effect standard error of {recipient['randomization_error_se']:.6f} points. The adopted interval uses the estimate ± 1.96 standard errors. This is a large-sample randomization approximation; it does not assume every unit has the same Q effect. Its coverage concerns repeated random assignments, rather than an exact conditional guarantee for this particular selected set.

For comparison, the conventional difference-in-means Welch analysis gives SE {p['se']:.6f}, a 95% interval of {p['ci_low']:.3f} to {p['ci_high']:.3f}, and a two-sided p-value of {p['p_two_sided']:.3g}. That interval concerns the usual all-unit average-effect comparison and is retained as a supporting result. The recipient-specific interval above is the interval adopted for the stated question.

## Baseline sensitivity checks

Recipients' mean baseline was {abs(b['mean_difference']):.3f} points lower than controls'. Because baseline predicts change, separate regressions were fitted within each assignment group and their predicted mean differences were averaged over the recipients' baseline values. This allows the groups to have different baseline relationships. All rows contributed to every fit.

| Baseline adjustment, standardized to recipients | Estimated additional change (points) |
|---|---:|
| Separate linear regressions | {m[0]['estimate']:.3f} |
| Separate quadratic regressions | {m[1]['estimate']:.3f} |
| Separate cubic regressions | {m[2]['estimate']:.3f} |
| Six five-point baseline bands, weighted by recipient counts | {s['estimate']:.3f} |

These are sensitivity estimates, not replacements for the adopted randomized mean comparison. Their agreement suggests that the small observed baseline imbalance does not drive the conclusion. Polynomial adjustments assume an adequate regression approximation; the bands can leave residual differences within bands. The saved HC3 regression intervals describe model-based sensitivity uncertainty and are not the adopted recipient randomization interval.

## What remains unknown

The recipients' changes without Q were not observed. Their exact realized average effect and individual effects therefore cannot be recovered with certainty from these files. Randomization nevertheless supports the positive average-effect estimate and its statistical uncertainty. No claim is made that Q helped every recipient, that effects are constant, or that this estimate applies outside the 2,000 study units.

The executed code, numerical tables, validation results, and ordered execution log accompany this report. An initial exploration attempt failed because `statsmodels` was unavailable; that failure and the successful replacement using NumPy, pandas, and SciPy are retained. No analysis was rerun to erase that record.
'''
(ROOT/'submission/final_report.md').write_text(report,encoding='utf-8')
assert len(report.strip()) > 100
print(report)
print('Output: submission/final_report.md. This report uses existing results; no statistical analysis was rerun.')
