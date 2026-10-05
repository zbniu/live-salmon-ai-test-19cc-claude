"""Generate report from actual saved results, package, and verify delivery."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SUB = ROOT / 'submission'
OUT = SUB / 'results'
LOG = SUB / 'run_log.txt'
def record(text):
    with LOG.open('a', encoding='utf-8') as f:
        f.write(datetime.now(timezone.utc).isoformat()+' '+text+'\n')

record('BEGIN code/03_deliver.py; reads existing analysis outputs; no statistical analyses rerun.')
p = json.loads((OUT / 'primary_result.json').read_text())
validation = json.loads((OUT / 'inspection.json').read_text())
groups = pd.read_csv(OUT / 'group_summary.csv', index_col='x')
estimates = pd.read_csv(OUT / 'effect_estimates.csv')
matching = pd.read_csv(OUT / 'matching_sensitivity.csv')
adjusted = estimates.loc[~estimates.method.str.startswith('Unadjusted'), 'att']
sensitivity_min = min(adjusted.min(), matching.att.min())
sensitivity_max = max(adjusted.max(), matching.att.max())

report = f'''# Did tutoring increase gains for the students who attended?

**The evidence supports a positive average effect. My adopted estimate is that attending tutoring increased score gain by {p['att']:.2f} points on average for the 600 attendees, with an approximate 95% confidence interval of {p['ci95_low']:.2f} to {p['ci95_high']:.2f} points.** This adjusted average effect answers the research question. It is an estimate, not an exact determination of the attendees' unobserved counterfactual gains or of each student's individual effect.

The analysis uses only the supplied study description and the complete data.csv. All 2,000 students were read and validated: 600 attended and 1,400 did not; all three variables were present, with no missing values or duplicate rows. No external data or internet research was used.

## What the comparison shows

| Quantity | Attendees | Nonattendees |
|---|---:|---:|
| Number of students | 600 | 1,400 |
| Mean starting score | {groups.loc[1,'y_mean']:.2f} | {groups.loc[0,'y_mean']:.2f} |
| Mean observed score gain | {groups.loc[1,'z_mean']:.2f} | {groups.loc[0,'z_mean']:.2f} |

The unadjusted gain difference is {validation['raw_gain_difference']:.2f} points. **This is not the causal-effect estimate adopted for the question:** attendees started with substantially higher scores, and starting score also predicts gain among nonattendees. Subtracting the two overall group means mixes tutoring's effect with differences in starting score.

## Why adjustment is justified, and how the effect was estimated

The supplied assignment mechanism selects applicants using only starting score and a student-specific random number unrelated to student characteristics, then admits applicants in order of starting score. Thus, conditional on baseline scores in this cohort, the remaining attendance selection comes from those random numbers rather than another student characteristic. The stated absence of switching and interference supports interpreting a baseline-adjusted comparison as an attendance effect. Attendance was not randomized without regard to starting score.

The target is the average treatment effect on the treated: the average of each attendee's gain with tutoring minus that same attendee's gain without tutoring. The latter is unobserved and must be estimated from comparable nonattendees. For this target, comparison support is needed at attendees' starting scores; it is not necessary to estimate an effect for low-scoring students who never attended.

Attendees' starting scores range from {groups.loc[1,'y_min']:.2f} to {groups.loc[1,'y_max']:.2f}. Nonattendees span {groups.loc[0,'y_min']:.2f} to {groups.loc[0,'y_max']:.2f}, with {validation['controls_above_treated_min']} nonattendees at or above the lowest attendee score. Every attendee falls within the observed nonattendee score range, and every half-point stratum containing attendees has comparison students. This supplies practical support across the target range. The unreported application scores and applicant list are not required to perform this outcome adjustment.

I fitted untreated gain as a smooth function of starting score using all 1,400 nonattendees: an ordinary least-squares cubic B-spline with interior knots at 50, 55, 60, 65 and 70, and score-scale boundaries at 0 and 100. I predicted each attendee's gain without tutoring at their own starting score, then averaged observed minus predicted gains over all 600 attendees. This allows the average effect to reflect the attendees' score distribution and does not require a constant tutoring effect across starting scores.

The estimated mean gain without tutoring for these attendees is **{p['mean_counterfactual_gain']:.2f} points**, compared with their observed **{groups.loc[1,'z_mean']:.2f} points**. Their difference is the adopted **{p['att']:.2f}-point average effect**. The estimated standard error is {p['se']:.3f} points. The confidence interval combines HC3 robust covariance for the untreated regression with the sampling variance of attendees' adjusted gains. It is a conventional approximate interval under the regression and independent-error approximation; it is not an exact randomization interval for the fixed-capacity assignment and does not include outcome-model misspecification.

## Checks and limits

Sensitivity analyses used untreated linear through fourth-degree polynomial models; additional models using only controls in the attendee score range; attendee-weighted comparisons in 0.5-, 1-, 2-, 2.5- and 5-point strata; and nearest-control matching with replacement using 1, 5, 10 or 20 neighbors. Their adjusted point estimates range from {sensitivity_min:.2f} to {sensitivity_max:.2f} points. The one-point stratified estimate is {estimates.loc[estimates.method.eq('Attendee-weighted strata, width 1'),'att'].iloc[0]:.2f} points, with an approximate 95% interval of {estimates.loc[estimates.method.eq('Attendee-weighted strata, width 1'),'ci95_low'].iloc[0]:.2f} to {estimates.loc[estimates.method.eq('Attendee-weighted strata, width 1'),'ci95_high'].iloc[0]:.2f}. These checks support the direction and approximate magnitude of the primary result. Matching estimates are reported as point-estimate checks only; no naive matching confidence intervals were calculated.

Continuous starting scores preclude exact same-score comparisons, so estimation still relies on reasonable smoothness or sufficiently close comparisons. No finite dataset proves the untreated outcome model correct. The supplied design and consistent adjusted estimates support a positive average effect of about **1.2 points for attendees**, while not establishing a precise effect for every student or an average effect for all 2,000 students.

## Reproducibility

The accompanying submission includes the executed Python code, original input copies, numerical outputs, student-level untreated predictions, and an execution log. The log retains the initial directory-redirection failure and the missing-package failure; the failed Python source and traceback are preserved. These errors occurred before statistical calculations. The successful inspection and analysis each ran once; report generation reads those saved outputs.
'''

report_path = SUB / 'final_report.md'
report_path.write_text(report, encoding='utf-8')
readback = report_path.read_text(encoding='utf-8')
assert readback and readback == report
assert '1.20' in readback and '0.79 to 1.61' in readback
assert '600 attendees' in readback
record('WROTE and READ BACK final_report.md; nonempty UTF-8 and intended adopted effect and interval verified.')

inputs = SUB / 'inputs'
inputs.mkdir(exist_ok=True)
shutil.copyfile(ROOT / 'upload/data(9).csv', inputs / 'data.csv')
shutil.copyfile(ROOT / 'upload/STUDY_DESCRIPTION(9).md', inputs / 'STUDY_DESCRIPTION.md')
assert hashlib.sha256((inputs / 'data.csv').read_bytes()).hexdigest() == validation['input_sha256']['data(9).csv']
assert hashlib.sha256((inputs / 'STUDY_DESCRIPTION.md').read_bytes()).hexdigest() == validation['input_sha256']['STUDY_DESCRIPTION(9).md']
record('Copied supplied inputs into inputs/; SHA-256 verified against initial inspection.')

# Initially archive every artifact except the still-active execution record.
archive = ROOT / 'submission.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as zz:
    for path in sorted(SUB.rglob('*')):
        if path.is_file() and path != LOG:
            zz.write(path, path.relative_to(ROOT))
with zipfile.ZipFile(archive) as zz:
    names = zz.namelist()
    assert zz.testzip() is None
    assert zz.read('submission/final_report.md').decode('utf-8') == readback
    assert any(n.startswith('submission/code/') for n in names)
    assert any(n.startswith('submission/results/') for n in names)
    assert 'submission/code/01_inspect_failed.py' in names
    assert 'submission/results/01_inspect_failed_stdout.txt' in names

verified = {'report_nonempty': bool(readback), 'report_utf8_readback_matches': True,
            'report_bytes': report_path.stat().st_size,
            'adopted_att': p['att'], 'adopted_ci95': [p['ci95_low'], p['ci95_high']],
            'archive_report_matches': True, 'archive_code_present': True,
            'archive_results_present': True, 'archive_crc_check_passed': True,
            'original_inputs_hash_verified': True,
            'preserved_failed_python_execution': True,
            'note': 'Archive was inspected before appending this verification and the completed run log; final complete archive is also inspected by this script.'}
verification_path = OUT / '03_delivery_verification.json'
verification_path.write_text(json.dumps(verified, indent=2)+'\n', encoding='utf-8')
record('Archive inspected: report bytes match; code/results and failed-run records present; CRC check passed. WROTE results/03_delivery_verification.json.')
record('Code/03_deliver.py completed report generation and initial archive validation successfully. Appending this verification file and run_log.txt as final archive members; final inspection is emitted to the session, without a separate stdout file.')
with zipfile.ZipFile(archive, 'a', zipfile.ZIP_DEFLATED) as zz:
    zz.write(verification_path, verification_path.relative_to(ROOT))
    zz.write(LOG, LOG.relative_to(ROOT))
with zipfile.ZipFile(archive) as zz:
    names = zz.namelist()
    assert len(names) == len(set(names))
    assert zz.testzip() is None
    assert 'submission/run_log.txt' in names
    assert zz.read('submission/run_log.txt') == LOG.read_bytes()
    assert zz.read('submission/final_report.md').decode('utf-8') == readback
    assert all('submission/'+str(p.relative_to(SUB)) in names for p in SUB.rglob('*') if p.is_file())
    print('FINAL ARCHIVE INSPECTION PASSED: '+str(len(names))+' files; report, executed code, results, inputs, and run log present. CRC and report readback pass.')
    for name in names:
        print(name)
print('\nREAD-BACK FINAL REPORT\n'+readback)
