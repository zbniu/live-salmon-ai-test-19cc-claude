"""Create the final report, package the record, and verify both deliverables.

This script reads the existing analysis output; it does not rerun analysis.
"""
import datetime
import json
import shutil
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
r = json.loads((root / 'results/analysis.json').read_text(encoding='utf-8'))
q, c = r['group_summary']
raw = r['raw_change_difference_association_only']
linear, cubic = r['descriptive_regressions']
lower, upper = r['finite_study_ATT_logical_bounds_assuming_0_100_potential_followup']

report = f'''# Arrangement Q and change: final research report

**Answer to the research question:** The supplied study description and data do not establish whether receiving arrangement Q increased change for the units who received it, or by how much. The causal effect among recipients is not identified. I adopt **no causal point estimate**. This is an absence of a definite causal answer, not evidence that Q had no effect.

The question concerns the average effect for the 600 recipients: the average difference between their change with Q and the change those same units would have had without Q. Writing these potential changes as z(1) and z(0), the target is the finite-study mean of z(1) − z(0) among recipients. Their observed change supplies z(1), but their z(0) is unobserved.

## Data and executed analysis

I used only the supplied STUDY_DESCRIPTION.md and data.csv (attached under names ending in “(3)”). All 2,000 rows were analyzed. There were exactly 600 recipients and 1,400 nonrecipients, three columns (x, y, z), and no missing or nonfinite values. No rows were excluded. I computed group summaries, baseline overlap, ordinary least-squares regressions adjusting for baseline, logical effect bounds, and explicit alternative counterfactual scenarios. Follow-up was calculated as y + z.

| Observed quantity | Received Q | Did not receive Q |
| --- | ---: | ---: |
| Number of units | 600 | 1,400 |
| Mean baseline y | {q['baseline_y_mean']:.3f} | {c['baseline_y_mean']:.3f} |
| Mean change z | {q['change_z_mean']:.3f} | {c['change_z_mean']:.3f} |
| Standard deviation of change | {q['change_z_sd']:.3f} | {c['change_z_sd']:.3f} |
| Mean follow-up y + z | {q['followup_mean']:.3f} | {c['followup_mean']:.3f} |

Recipients' mean observed change exceeded nonrecipients' by **{raw:.3f} points**. This is an observed association, **not the numerical answer to the causal research question**. Recipients also started {r['baseline_mean_difference']:.3f} points higher on average. A positive change within recipients does not itself show a positive effect of Q, since their change without Q might also have been positive.

For descriptive baseline adjustment, I fitted z on an intercept, x, and y, obtaining an x coefficient of **{linear['x_coefficient_association_only']:.3f} points**. Replacing the linear baseline term with a cubic polynomial gave **{cubic['x_coefficient_association_only']:.3f} points**. Both models used all 2,000 rows and common baseline slopes across groups. These are model-dependent adjusted associations. Their similarity does not establish that adjustment removed confounding. I do not interpret either coefficient as the effect among recipients, and do not attach a causal confidence interval or significance claim to them.

## Why the causal question remains unresolved

Selection into the candidate group depended on baseline and on unrecorded circumstances, together with an independent random number. Having an independent random component and a nonzero chance of candidacy does not make Q assignment independent of those circumstances. The supplied material does not establish whether those circumstances predict change without Q. We therefore cannot justify the assumption that recipients and nonrecipients with the same baseline would have had the same average change without Q.

Acceptance then favored candidates with higher baseline. Treated baseline values ranged from {q['baseline_y_min']:.3f} to {q['baseline_y_max']:.3f}; untreated values ranged from {c['baseline_y_min']:.3f} to {c['baseline_y_max']:.3f}. All recipients were within the observed untreated baseline range, and {r['baseline_overlap']['untreated_at_or_above_treated_min']} nonrecipients had baseline at or above the lowest recipient baseline. This observed range overlap permits descriptive comparisons, but does not resolve selection on unrecorded circumstances.

Neither candidacy nor the random selection numbers are observed, so these data cannot exploit the random component directly. A baseline cutoff alone also does not establish a valid regression-discontinuity analysis: candidacy is hidden and the required continuity assumptions are not supplied. Even a valid local cutoff effect would require additional assumptions to answer the average-effect question for all recipients. Identical treatment, no switching, no interference, consistent measurement, blinded recording, and complete data are valuable protections, but do not establish comparability of counterfactual changes. The same arrangement for every recipient also does not establish the same treatment effect for every recipient.

## What can be said about the causal quantity

If the stated 0–100 scale is a hard bound for follow-up under either arrangement, each recipient's no-Q change can lie between −y and 100 − y. Consequently the average effect among recipients is logically bounded by

**{lower:.3f} to {upper:.3f} points.**

These are assumption-light bounds on the causal quantity, not a point estimate or confidence interval. They follow from the observed recipients' mean follow-up ({upper:.3f}) minus an unknown no-Q mean follow-up between 0 and 100. They include negative, zero, and positive effects. If “0–100 scale” is not intended as a hard bound on potential follow-up, these numerical bounds should not be adopted; the nonidentification conclusion still holds.

The code also checked three concrete alternatives for recipients' unobserved no-Q changes: setting z(0) equal to observed z, observed z − 1, or observed z + 1 gives average effects of **0, +1, or −1 point**, respectively. In each case the resulting no-Q follow-up values remain within 0–100. Each alternative leaves every observed value unchanged and is not ruled out by the supplied design statements. These are illustrative counterfactual scenarios, not fitted or estimated effects.

**Conclusion:** The observed association favors Q, but the supplied material does not determine the sign or magnitude of Q's causal effect among the 600 recipients. Establishing a definite answer would require additional causal assumptions or information about the selection process and untreated potential changes.
'''

report_path = root / 'final_report.md'
report_path.write_text(report, encoding='utf-8')
# Include unchanged source copies to permit reproduction without external data.
inputs = root / 'inputs'
inputs.mkdir(exist_ok=True)
for source, name in [(root.parent / 'upload/data(3).csv', 'data.csv'),
                     (root.parent / 'upload/STUDY_DESCRIPTION(3).md', 'STUDY_DESCRIPTION.md')]:
    shutil.copyfile(source, inputs / name)

(root / 'code/README.md').write_text('''# Reproduction

The substantive analysis was executed once successfully using Python 3.12.14
and NumPy 2.3.5. From an extracted archive, an equivalent reproduction command is:

    python submission/code/analyze.py submission/inputs/data.csv submission/inputs/STUDY_DESCRIPTION.md

This would write new outputs into submission/results; preserve the original
delivered results if comparing runs. Do not rerun merely to obtain a cleaner log.

The original execution used the uploaded inputs in the surrounding workspace.
run_analysis_initial.py preserves the failed wrapper attempt, which did not
launch analysis. run_analysis.py is its corrected version and captured the
successful analysis stdout and stderr. initial_inspection.py preserves the
first executed inspection snippet. create_report_and_archive.py creates the
report from existing results without recalculating any statistical analysis.
''', encoding='utf-8')

# User-required readback before claiming delivery.
readback = report_path.read_text(encoding='utf-8')
assert readback.strip() and readback == report
assert 'do not establish whether' in readback
assert f'{raw:.3f}' in readback and f'{lower:.3f}' in readback
archive = root.parent / 'submission.zip'
with (root / 'run_log.txt').open('a', encoding='utf-8') as log:
    log.write(f'5. {datetime.datetime.now(datetime.timezone.utc).isoformat()}: executed\n')
    log.write('   code/create_report_and_archive.py using the primary Python runtime.\n')
    log.write('   Read existing results/analysis.json without rerunning analysis.\n')
    log.write('   Wrote final_report.md, code/README.md, and unchanged input copies.\n')
    log.write('   Read final_report.md back as UTF-8; nonempty and exact intended text verified.\n')

def package():
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(root.rglob('*')):
            if p.is_file():
                zf.write(p, p.relative_to(root.parent).as_posix())

package()
with zipfile.ZipFile(archive) as zf:
    assert zf.testzip() is None
    names = zf.namelist()
    assert 'submission/final_report.md' in names
    assert 'submission/run_log.txt' in names
    assert 'submission/code/analyze.py' in names
    assert 'submission/results/analysis.json' in names
    assert zf.read('submission/final_report.md').decode('utf-8') == readback
verification = {'report_nonempty': bool(readback.strip()),
                'report_utf8_bytes': len(readback.encode('utf-8')),
                'archive_crc_check': 'passed',
                'report_in_archive_matches_readback': True,
                'inspected_archive_members': names}
(root / 'results/delivery_verification.json').write_text(json.dumps(verification, indent=2)+'\n', encoding='utf-8')
with (root / 'run_log.txt').open('a', encoding='utf-8') as log:
    log.write('   Created submission.zip and inspected its actual members and CRCs.\n')
    log.write('   Required report, code, results, and execution record were present.\n')
    log.write('   Actual verification output: results/delivery_verification.json.\n')
    log.write('   Repacked after recording verification; no statistical analysis repeated.\n')
package()
with zipfile.ZipFile(archive) as zf:
    assert zf.testzip() is None
    assert zf.read('submission/final_report.md').decode('utf-8') == readback
    assert zf.read('submission/run_log.txt') == (root / 'run_log.txt').read_bytes()
    assert 'submission/results/delivery_verification.json' in zf.namelist()
    final_names = zf.namelist()
print('REPORT READBACK:\n' + readback)
print('VERIFIED FINAL ARCHIVE MEMBERS:\n' + '\n'.join(final_names))
print(f'Archive bytes: {archive.stat().st_size}')
