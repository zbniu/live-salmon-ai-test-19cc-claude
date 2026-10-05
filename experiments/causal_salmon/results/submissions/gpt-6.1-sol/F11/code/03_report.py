"""Write the standalone report directly from actual saved analysis outputs."""
from pathlib import Path
import json
import pandas as pd
root=Path(__file__).resolve().parents[2]
s=root/'submission'
r=json.loads((s/'results/primary_results.json').read_text())
v=json.loads((s/'results/validation.json').read_text())
sens=pd.read_csv(s/'results/sensitivity_estimates.csv')
lo,hi=r['approximate_95_percent_bootstrap_CI']
report=f'''# Tutoring and score gain: final report

## Answer to the research question

The supplied study supports a positive average effect of tutoring for the students who attended. **The adopted estimate is an increase of {r['att_points']:.2f} score points in their average gain, with an approximate 95% confidence interval of {lo:.2f} to {hi:.2f} points.** This adjusted average effect for the 600 attendees is the numerical result that answers the research question. It is an estimate, not an exact reconstruction of their unobserved outcomes without tutoring; it does not establish that every attendee benefited.

## Data and causal comparison

Only the attached study description and complete data.csv were used. All 2,000 students were analyzed: 600 attended and 1,400 did not. The file has exactly the specified three columns, no missing or nonfinite values, and 2,000 distinct starting scores.

The relevant quantity is the average, among attendees, of their gain with tutoring minus the gain those same students would have had without tutoring (the average treatment effect on the treated, or ATT).

Attendees' mean starting score was 67.073, compared with 56.864 for nonattendees. Their observed mean gains were {r['mean_observed_attendee_gain']:.3f} and {r['mean_control_gain']:.3f}, respectively. Thus, the unadjusted gain difference is {r['unadjusted_difference_points']:.3f} points. **That unadjusted difference is not the adopted causal answer**, because higher starting scores influence attendance and are associated with larger gains.

The described assignment mechanism depends on starting score and independently generated randomness, with no other student characteristic entering selection. This provides a basis for comparing attendees with nonattendees at the same starting score, accounting for the score-based admissions ranking. The missing applicant list does not introduce an additional student characteristic that needs adjustment. The stated absence of switching and interference supports interpreting attendance as the treatment.

Observed overlap is adequate for the attendee target: attendee starting scores range from 58.213 to 74.972, within the nonattendee range of 45.007 to 74.991. All 600 attendees have an observed nonattendee within {v['nearest_control_score_distance_quantiles']['max']:.3f} starting-score points. No inference about a tutoring effect for the lowest-scoring students is needed to answer this question.

## Method and numerical results

I fitted the mean score gain without tutoring as a smooth function of starting score using all 1,400 nonattendees. The primary model was a restricted cubic spline with five knots fixed at the 5th, 27.5th, 50th, 72.5th, and 95th percentiles of the complete starting-score distribution. Knots were determined from starting scores, not from gains. I predicted the no-tutoring gain for each attendee and averaged their observed gain minus that prediction. This directly targets attendees and does not require a common treatment effect for all starting scores.

| Quantity for the 600 attendees | Score-gain points |
| --- | ---: |
| Observed mean gain with tutoring | {r['mean_observed_attendee_gain']:.3f} |
| Estimated mean gain without tutoring, at attendees' starting scores | {r['estimated_mean_attendee_gain_without_tutoring']:.3f} |
| **Adopted average effect of tutoring** | **+{r['att_points']:.3f}** |
| Approximate 95% confidence interval for that effect | {lo:.3f} to {hi:.3f} |

The interval uses 3,000 stratified bootstrap resamples, preserving the 600-attendee and 1,400-nonattendee group sizes, refitting the control regression in each resample, and taking the 2.5th and 97.5th percentiles. Its bootstrap standard error is {r['bootstrap_standard_error']:.3f} points; the random seed was 20261004.

Checks with linear, quadratic, and cubic control regressions, splines with four and seven knots, starting-score strata of widths 0.5, 1, and 2 points, and matching to 1, 5, 10, or 20 nearest nonattendees all retained the full 600-attendee target. Their estimates ranged from {sens.att_points.min():.2f} to {sens.att_points.max():.2f} points and were all positive. Outcome-model prediction checks showed similar errors across the regression forms. These checks support the stability of the primary estimate; they do not independently prove its assumptions.

## Limits of the answer

Causal interpretation relies on the supplied selection description: after accounting for starting score, the selection randomness must be unrelated to students' potential gains. Estimation also uses a smooth conditional mean for nonattendees; with distinct continuous scores, the data cannot reveal exact counterfactual gains without some statistical estimation. The observed overlap and agreement across methods make the fitted comparison credible.

The confidence interval is an approximate model/sampling interval. The bootstrap does not reproduce the fixed-capacity applicant/admission lottery, whose application scores and full probability law are unavailable, so it is not an exact finite-population randomization interval. The exact average causal gain for these particular 600 students is unobserved, and individual treatment effects are not identified. Subject to these limits, the evidence favors an average increase of about **1.24 points** for attendees, rather than the unadjusted 3.63-point difference. The conclusion concerns this simulated study and its attendees.
'''
(s/'final_report.md').write_text(report,encoding='utf-8')
(s/'README.md').write_text('''# Execution and reproduction

The two original supplied inputs are preserved unchanged in `inputs/`, with hashes in `results/input_sha256.json`. No outside data were used.

Actual analysis order in this session was `01_inspect.py`, `02_estimate.py`, and `03_report.py`, each executed through `run_step.py`. Standard output and errors are in the corresponding `results/*_console.txt`; run_log.txt retains execution order and exit status. Preliminary inline inspection commands are retained in `code/preliminary_commands.sh`, with their outputs summarized and missing standalone console captures disclosed in the run log. No analyses were repeated.

The analysis requires Python, numpy, pandas, scipy, and matplotlib. For reproducing the estimation from an extracted archive, run from the directory containing `submission/`:

```sh
python submission/code/run_step.py submission/code/02_estimate.py
python submission/code/run_step.py submission/code/03_report.py
```

`02_estimate.py` reads the archived `submission/inputs/` copies if the original `upload/` paths do not exist. The initial inspection script reads the original upload path; to reproduce it outside the original workspace, first copy the archived inputs into `upload/` with their original names. Reproduction overwrites analysis outputs and appends new execution records, so use a separate extracted copy if the delivered record must be preserved.

`04_package.py` packages and checks the delivery; it performs no statistical analysis. Individual observed-minus-predicted contrasts in attendee_standardization.csv are components of the average estimator, not identified individual causal effects. Bootstrap draws and every reported sensitivity estimate are actual execution outputs.
''',encoding='utf-8')
checks={'utf8_report_nonempty':bool(report.strip()),'primary_estimate':r['att_points'],
 'rounded_answer_present':f"{r['att_points']:.2f}" in report,'report_characters':len(report)}
assert all([checks['utf8_report_nonempty'],checks['rounded_answer_present']])
(s/'results/report_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
print('Wrote submission/final_report.md and submission/README.md from saved results.')
