"""Write the report from executed results, package, and verify delivery files.

This script does not rerun any statistical analysis.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import zipfile

root = Path(__file__).resolve().parents[1]
archive = root.parent / 'submission.zip'
results = json.loads((root / 'results' / 'analysis.json').read_text(encoding='utf-8'))
control, treated = results['group_summary']
linear, cubic = results['descriptive_regressions']
bound = results['range_bounds_if_both_potential_end_scores_are_in_0_100']

report = f'''# Did tutoring increase score gains for the students who attended?

**The supplied material does not support a definite answer. Neither the sign nor the average size of the causal effect for attendees is identified. I do not adopt a numerical point estimate of that effect.** The positive differences below describe associations, not the answer to the causal research question.

## Question and data

The target is the average effect among the 600 students who attended: the mean of each attendee's gain with tutoring minus that same student's gain without tutoring. In potential-outcome notation, the finite-study target is ATT = (1/600) × sum over attendees of [z(1) − z(0)]. Their z(1) is observed; their z(0) is not. Because baseline score y precedes attendance, the effect on gain is also the effect on end-of-term score.

Only the supplied `STUDY_DESCRIPTION.md` and `data.csv` were used. Code analyzed all 2,000 rows, with exactly the stated three columns, 600 attendees and 1,400 nonattendees. There were no missing or nonfinite values, exclusions, or imputations. All observed end-of-term scores, calculated as y + z, lie within 0–100.

## Observed results

| Group | Students | Mean initial score y | Mean gain z | Mean end score y + z |
| --- | ---: | ---: | ---: | ---: |
| Attended | {treated['n']} | {treated['y_mean']:.3f} | {treated['z_mean']:.3f} | {treated['end_score_mean']:.3f} |
| Did not attend | {control['n']} | {control['y_mean']:.3f} | {control['z_mean']:.3f} | {control['end_score_mean']:.3f} |

The unadjusted difference in mean gain is **{results['crude_gain_difference_points']:.3f} points**. Attendees also started **{results['crude_baseline_difference_points']:.3f} points** higher on average. Neither the attendees' own mean gain nor the between-group gain difference establishes how much tutoring caused them to improve.

As descriptive checks, ordinary least squares on all 2,000 students gives an attendance coefficient of **{linear['x_coefficient']:.3f} points** when controlling linearly for initial score, and **{cubic['x_coefficient']:.3f} points** when controlling with a cubic polynomial in initial score. These are adjusted associations under the specified regression models. HC3 standard errors and model-based intervals are recorded in the results files, but they do not resolve causal identification and are not confidence intervals for the target causal effect.

## Why the causal answer is undetermined

The description says the top 900 application scores determined applicants, and the 600 applicants with the highest initial scores attended. Application scores depended on initial score, unrecorded circumstances, and an independent random component. An independent random component in this selection rule does not make attendance random: admission still depends on the other score components and on initial score. The random component itself is unavailable and cannot be used as an observed instrument.

The unrecorded circumstances could also predict gains without tutoring. Nothing supplied states or establishes that attendees and nonattendees have the same untreated potential gains after conditioning on initial score. Regression or matching on y therefore requires an additional, unsupported causal assumption. The same tutoring class for all attendees does not imply an equal treatment effect for every student. Complete follow-up, consistent measurement, blinding, and lack of spillovers address other problems but do not remove selection bias.

Attendance begins at an observed initial score of {results['score_support']['min_treated_y']:.3f}, yet {results['score_support']['controls_at_or_above_min_treated_y']} nonattendees have scores at or above that value. The score threshold applies to applicants, whose identities are unavailable. A regression-discontinuity interpretation would need additional continuity and related identification assumptions not supplied here. Even a valid discontinuity estimate would concern students near the admission threshold, rather than automatically answering the average-effect question for all 600 attendees.

The missing counterfactuals illustrate the ambiguity directly. Write S1 = y + z for an attendee's observed end score and S0 for their unobserved end score without tutoring. Leaving every observed row and the assignment process unchanged, S0 = S1 gives zero effect. S0 = 0.99 × S1 gives a positive average effect of {results['hypothetical_counterfactual_examples']['positive_effect']['ATT_points']:.3f} points. S0 = 0.99 × S1 + 1 gives a negative average effect of {results['hypothetical_counterfactual_examples']['negative_effect']['ATT_points']:.3f} points. All these hypothetical untreated scores remain within 0–100. The supplied material places no outcome restriction that selects one of these alternatives. These are identification examples, not estimates or reconstructed observations.

If both potential end scores are constrained to 0–100, the purely scale-based bound on the average effect is **[{bound['lower_points']:.3f}, {bound['upper_points']:.3f}] points**, obtained by allowing each attendee's untreated end score to range from 100 to 0. This is a conditional identification bound, not a confidence interval. It includes harm, no effect, and benefit. If the scale description does not constrain counterfactual scores, even this bound is unavailable.

**Answer to the research question:** attendees had higher observed gains, but these two files do not determine whether tutoring increased their gains, or by how much. A causal point estimate would require additional identification assumptions or information about assignment and untreated outcomes.

## Execution records

`code/analyze.py` performed the analysis once, invoked by `code/run_analysis.py`. `results/analysis.json`, the CSV summaries, and the preserved stdout/stderr contain the actual execution outputs. `code/finalize.py` assembled this report from those outputs and checked the delivery files without rerunning the analysis. The supplied inputs and their SHA-256 hashes are included for reproducibility. `run_log.txt` records execution order and output status.
'''

def record(text):
    with (root / 'run_log.txt').open('a', encoding='utf-8') as handle:
        handle.write(datetime.now(timezone.utc).isoformat() + ' ' + text + '\n')

record('START code/finalize.py: assemble report from results/analysis.json; no statistical rerun.')
(root / 'final_report.md').write_text(report, encoding='utf-8')
(root / 'README.md').write_text(
    '# Reproduction\n\nRequires Python 3 and NumPy. From the directory containing '
    '`submission/`, run `python3 submission/code/run_analysis.py`, then '
    '`python3 submission/code/finalize.py`. The launcher preserves actual stdout '
    'and stderr and appends to the run log. The original session ran the analysis '
    'once. All computations use the two included inputs. No external data or '
    'internet access is required. Regression intervals describe associations '
    'only. Hypothetical counterfactual examples are expressly not observed data.\n',
    encoding='utf-8')
readback = (root / 'final_report.md').read_text(encoding='utf-8')
assert readback == report and readback.strip()
assert 'Neither the sign nor the average size' in readback
assert f"{results['crude_gain_difference_points']:.3f}" in readback
record('REPORT final_report.md read back as UTF-8, nonempty, and exactly equal to intended report; answer and numerical associations verified.')

def pack():
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                zf.write(path, path.relative_to(root.parent).as_posix())

def inspect():
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        required = ['submission/final_report.md', 'submission/run_log.txt',
                    'submission/code/analyze.py', 'submission/code/run_analysis.py',
                    'submission/code/finalize.py', 'submission/results/analysis.json',
                    'submission/results/analysis_stdout.txt',
                    'submission/results/analysis_stderr.txt',
                    'submission/results/group_summary.csv',
                    'submission/results/descriptive_regressions.csv',
                    'submission/results/score_bands.csv']
        assert all(n in names for n in required)
        assert zf.testzip() is None
        assert zf.read('submission/final_report.md').decode('utf-8') == readback
        for n in required:
            assert zf.getinfo(n).file_size > 0 or n.endswith('analysis_stderr.txt')
        return {'archive': archive.name, 'required_members_present': True,
                'zip_integrity_check': 'passed', 'archived_report_matches_readback': True,
                'members': names}

pack()
inspection = inspect()
(root / 'results' / 'delivery_verification.json').write_text(
    json.dumps(inspection, indent=2) + '\n', encoding='utf-8')
record('ARCHIVE first assembly inspected: required report, executed code, actual analysis results and run log present; CRC check passed; archived report equals local readback. Inspection -> results/delivery_verification.json.')
record('FINISH code/finalize.py: include actual delivery inspection record and updated log in refreshed archive, then inspect refreshed archive. No analysis errors, reruns, or missing statistical execution records.')
pack()
final_inspection = inspect()
assert 'submission/results/delivery_verification.json' in final_inspection['members']
print('REPORT READBACK:\n' + readback)
print('FINAL ARCHIVE INSPECTION:\n' + json.dumps(final_inspection, indent=2))
print('DELIVERY VERIFIED: report, executed code, actual results, and run log included.')
