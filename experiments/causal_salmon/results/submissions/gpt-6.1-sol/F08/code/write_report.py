"""Create the report from actual saved results; copy authorized inputs for reuse."""
from pathlib import Path
import json, shutil, hashlib

ROOT=Path(__file__).resolve().parents[2]
SUB=ROOT/'submission'
r=json.loads((SUB/'results/att_results.json').read_text())
e=json.loads((SUB/'results/exploration.json').read_text())
p=r['primary']; lo,hi=p['ci95']; boot=r['bootstrap_check']['percentile_ci95']
report=f'''# Effect of tutoring on score gains among attendees

**Answer:** The supplied study supports a positive average effect of attending tutoring on the score gain of the students who attended. My adopted estimate is **{p['att']:.2f} additional score points per attendee**, with an approximate **95% confidence interval of {lo:.2f} to {hi:.2f} points**. This is an estimate of the **average treatment effect among attendees (ATT)** and is the numerical result that answers the research question. It does not establish that every attendee benefited or identify the exact effect for each student.

## Data and causal comparison

I used all 2,000 rows of `data.csv`: 600 attendees and 1,400 nonattendees. The file has the three specified columns, no missing or nonfinite values, and the stated attendance counts. Only the two supplied files were used; no internet sources were accessed.

The attendees started with higher scores: their mean starting score was {e['group_summaries']['attended']['y']['mean']:.2f}, compared with {e['group_summaries']['did_not_attend']['y']['mean']:.2f} for nonattendees. Their observed mean gains were {r['observed_attendee_mean_gain']:.2f} and {e['group_summaries']['did_not_attend']['z']['mean']:.2f}, respectively. The resulting **raw difference of {r['raw_mean_difference']:.2f} points is descriptive, not the adopted causal effect**.

According to the study description, application and admission depended on the pretreatment score `y` and random numbers unrelated to student characteristics. Thus, starting score is the relevant adjustment variable: unmeasured student characteristics did not separately determine attendance. The unseen applicant list does not itself require an additional adjustment. Conditional comparisons by starting score use nonattendees to estimate what attendees would have gained without tutoring. The stated absence of switching and interference supports interpreting this as the effect of attendance.

There is useful observed comparison coverage. Attendees' starting scores range from {r['treated_y_range'][0]:.2f} to {r['treated_y_range'][1]:.2f}; nonattendees' scores range from {r['control_y_range'][0]:.2f} to {r['control_y_range'][1]:.2f}. All attendees lie within the nonattendee range, and {r['control_count_at_or_above_lowest_attendee_y']} nonattendees have starting scores at or above the lowest attendee score. Both groups occur in every one-point starting-score stratum containing attendees. This supports estimating an effect for attendees without extrapolating beyond the observed control range. It does not justify extrapolating the result to all students or other classes.

## Estimation and adopted result

I fitted the mean untreated gain as a smooth function of starting score using all 1,400 nonattendees: a cubic B-spline with five knot locations at the control-score minimum, quartiles, and maximum (seven basis functions). I then predicted the untreated mean gain at each of the 600 attendees' starting scores. The estimate is the attendee average of observed gain minus that predicted untreated mean:

`ATT estimate = mean over attendees [observed z - estimated mean untreated gain at y]`.

This averages over the actual attendees' score distribution and does not impose the same treatment effect at every starting score.

| Quantity | Score points |
|---|---:|
| Observed mean gain among attendees | {r['observed_attendee_mean_gain']:.3f} |
| Estimated mean gain for those attendees without tutoring | {p['estimated_untreated_gain_for_attendees']:.3f} |
| **Adopted ATT estimate: additional gain due to attendance** | **{p['att']:.3f}** |
| Approximate standard error | {p['se']:.3f} |
| Approximate 95% confidence interval | {lo:.3f} to {hi:.3f} |

The standard error combines variability of attendees' observed-minus-predicted gains with HC3 heteroskedasticity-robust uncertainty in the fitted control mean. A separate 2,000-replicate bootstrap, resampling students within attendance groups and refitting the spline, gives a percentile interval of {boot[0]:.2f} to {boot[1]:.2f} points.

## Sensitivity and limits

The conclusion is stable across alternative adjustments. Linear, quadratic, and cubic models fitted to controls yield ATT estimates of 1.17, 1.21, and 1.19 points. Cubic splines with 4, 6, 8, 10, or 15 knot locations yield 1.20–1.22 points. Direct comparisons within starting-score strata, weighted by the attendees' distribution, yield 1.16 points with one-point strata, 1.21 with two-point strata, and 1.31 with five-point strata. Wider strata can leave more differences in starting scores within strata. Every reported adjusted interval remains above zero.

The causal interpretation relies on the supplied assignment mechanism and on estimating the untreated mean adequately from students with similar starting scores. The spline is an estimated outcome relationship, not a disclosed data-generating formula; the alternative adjustments check sensitivity to its form. Confidence intervals are approximate and assume independent student outcome/sampling variation and adequate estimation of that mean. Neither the bootstrap nor the standard error recreates the fixed-seat admissions process, so these are not exact randomization intervals. Since every student in this study is observed, the intervals represent inferential uncertainty about counterfactual outcomes, not missing observed records. The individual counterfactual gains are unobserved, so the exact realized average effect for these 600 students cannot be read directly from the file.

Within these limits, the evidence supports **an average increase of about 1.2 points in score gain among attendees**, rather than the unadjusted 3.45-point group difference.
'''
(SUB/'final_report.md').write_text(report,encoding='utf-8')
inputs=SUB/'inputs'; inputs.mkdir(exist_ok=True)
for name in ['data(20261004-180753).csv','STUDY_DESCRIPTION(20261004-180753).md']:
 shutil.copy2(ROOT/'upload'/name,inputs/name)
(SUB/'code/README.md').write_text('''# Executed analysis

All statistical analyses used the complete attached CSV and the attached study
description. The scripts in this directory are the code actually executed.
`initial_inspection.py` and `environment_check.py` were originally executed
inline before the logging runner existed; the run log identifies their missing
file-based stdout records. They were not rerun.

Execution order: initial inspection, environment check, `explore.py`,
`estimate_att.py`, `write_report.py`, then packaging and validation. The original
stdout/stderr for the three main scripts is in `results/`. Python/library
versions and source hashes are in `results/exploration.json`.

To reproduce after extracting the archive, place the two files from
`submission/inputs/` into a sibling `upload/` directory alongside `submission/`.
Run from that parent directory using Python with numpy, scipy, scikit-learn,
and matplotlib installed:

```
python submission/code/run_recorded.py submission/code/explore.py
python submission/code/run_recorded.py submission/code/estimate_att.py
python submission/code/run_recorded.py submission/code/write_report.py
```

The original executed scripts expect the original attached filenames, retained
unchanged in `inputs/`. Re-execution overwrites statistical outputs and appends
new executions to the log; use a separate extracted copy to preserve the
delivered records. Bootstrap seed: 20261004; 2000 replicates. Generated prediction
rows are estimates of conditional means, not individual counterfactual outcomes.
''',encoding='utf-8')
readback=(SUB/'final_report.md').read_text(encoding='utf-8')
assert readback.strip() and f'{p["att"]:.2f} additional score points' in readback
assert 'average treatment effect among attendees' in readback
validation={'report_nonempty':True,'report_readback_matches_written_report':readback==report,
            'adopted_att_present':True,'report_bytes':(SUB/'final_report.md').stat().st_size,
            'report_sha256':hashlib.sha256((SUB/'final_report.md').read_bytes()).hexdigest()}
(SUB/'results/report_validation.json').write_text(json.dumps(validation,indent=2)+'\n')
print('Created final_report.md, code/README.md, and exact copies of the authorized inputs.')
print('READ BACK FINAL REPORT:\n'+readback)
print('Validation: '+json.dumps(validation))
