"""Write the report from actual saved results, then read back and verify delivery."""
from pathlib import Path
from datetime import datetime, timezone
import json, zipfile, hashlib
import pandas as pd

root = Path(__file__).resolve().parents[1]
out = root/'results'
log = root/'run_log.txt'
def record(message):
    with log.open('a',encoding='utf-8') as f:
        f.write(datetime.now(timezone.utc).isoformat()+' '+message+'\n')

record('START code/build_delivery.py; reads actual results/analysis_summary.json, group_summary.csv and validation.json. No analyses rerun.')
s = json.loads((out/'analysis_summary.json').read_text())
g = pd.read_csv(out/'group_summary.csv').set_index('x')
v = json.loads((out/'validation.json').read_text())
report = f'''# Effect of arrangement Q on recipients' change

## Answer to the research question

**The supplied material does not establish whether receiving arrangement Q increased change `z` for the 600 units that received it, or by how much. No causal point estimate is adopted.** The positive observed differences below are associations, not answers to the causal question. This conclusion does not mean that Q had no effect.

The target is the average effect for the actual recipients:

`ATT = mean[z_i(Q) − z_i(no Q) | received Q]`.

Each recipient's change under Q is observed, but their change without Q is not. Their positive observed change alone does not show how they would have changed without Q.

## Data and executed analyses

Only the supplied study description and complete CSV were used. All {v['rows']:,} rows were analyzed, with {v['received_Q']} recipients and {v['did_not_receive_Q']:,} nonrecipients. No values were missing and no rows were excluded. The code checked column names, treatment counts, finite values, measurement ranges, baseline overlap, group summaries, and baseline-bin summaries, and fitted one descriptive linear regression.

| Observed quantity | Received Q | Did not receive Q |
|---|---:|---:|
| Number of units | {int(g.loc[1,'n'])} | {int(g.loc[0,'n'])} |
| Mean baseline `y` | {g.loc[1,'y_mean']:.3f} | {g.loc[0,'y_mean']:.3f} |
| Mean change `z` | {g.loc[1,'z_mean']:.3f} | {g.loc[0,'z_mean']:.3f} |
| Standard deviation of change | {g.loc[1,'z_sd']:.3f} | {g.loc[0,'z_sd']:.3f} |
| Mean follow-up `y + z` | {g.loc[1,'followup_mean']:.3f} | {g.loc[0,'followup_mean']:.3f} |

The **unadjusted observed difference in mean change is {s['raw_mean_change_difference']:.3f} points** (recipients minus nonrecipients). Recipients' mean baseline was {s['raw_mean_baseline_difference']:.3f} points higher. An ordinary least-squares model of `z` on an intercept, receipt indicator `x`, and centered baseline `y`, using all 2,000 rows, gave an `x` coefficient of **{s['baseline_adjusted_descriptive_x_coefficient']:.3f} points**. This is a baseline-adjusted descriptive association; its linear specification and adjustment do not identify the causal effect.

Recipients' baseline measurements ranged from {s['overlap']['treated_min_y']:.3f} to {s['overlap']['treated_max_y']:.3f}; {s['overlap']['control_count_in_treated_y_range']} nonrecipients had baselines within that range. Baseline overlap supplies potential comparisons but does not establish that their untreated changes would be comparable.

## Why the causal answer is undetermined

Candidate selection depended on baseline, unrecorded circumstances, and an independent random number. The document does not state that the unrecorded circumstances were unrelated to changes that would occur without Q. Receipt could therefore be associated with untreated potential changes even at the same baseline. Adjusting for baseline cannot establish or remove that possible confounding.

An independent random component in a selection score does not make final receipt randomly assigned. Neither the random values, selection scores, nor candidate list are available, and assignment probabilities cannot be recovered from the supplied protocol. There is no observed randomized instrument to use. The subsequent baseline ranking among candidates also does not by itself identify an effect for all recipients: a discontinuity analysis would require additional continuity assumptions and would at most address an effect near a cutoff, rather than this overall recipient effect. Those assumptions and any transport from a local effect are not established here.

The study's consistent treatment, absence of switching and interference, complete follow-up, and blinded measurement support interpretation of the observed records. They do not supply the missing counterfactual comparison or establish that assignment was independent of untreated changes.

## Numerical restriction on the causal answer

Using the stated 0–100 measurement scale as the allowable range of counterfactual follow-up measurements, the data give only the following logical bounds for the recipients' average causal effect:

**{s['ATT_logical_lower_bound_0_100']:.3f} to +{s['ATT_logical_upper_bound_0_100']:.3f} points.**

These bounds concern the research question directly, but they are not a point estimate or a confidence interval. The recipients' observed mean follow-up is {s['treated_mean_followup']:.3f}. If their average follow-up without Q could be anywhere from 0 to 100, their average effect could be anywhere from `{s['treated_mean_followup']:.3f} − 100` to `{s['treated_mean_followup']:.3f} − 0`. Baseline cancels when comparing the two potential changes for the same unit.

For illustration, assigning each recipient an unobserved follow-up without Q equal to their observed follow-up produces exactly zero effect. Assigning each a counterfactual follow-up of 100 produces the negative endpoint; assigning each 0 produces the positive endpoint. These are hypothetical completions, not observations or estimates. Each leaves the supplied observations and actual selection unchanged; the supplied material imposes no further restriction that rules them out. Thus positive, zero, and negative average effects remain compatible with the information supplied.

The uncertainty is one of causal identification, not merely sampling precision. A small regression standard error or a test of the observed group difference would not resolve it.

## Reproducibility

The accompanying submission contains the exact input copies, executed Python code, actual numerical outputs and captured stdout/stderr, and an execution log. `results/analysis_summary.json` contains the full-precision descriptive differences and logical bounds. The hypothetical completions are explicitly labeled in `results/hypothetical_counterfactual_completions.csv`. No internet resources or external datasets were used.
'''
path = root/'final_report.md'
path.write_text(report,encoding='utf-8')
# Required actual read-back of the delivered report.
readback = path.read_text(encoding='utf-8')
assert readback == report and len(readback.strip()) > 0
assert 'does not establish whether receiving arrangement Q increased' in readback
assert f"{s['raw_mean_change_difference']:.3f}" in readback
assert f"{s['ATT_logical_lower_bound_0_100']:.3f}" in readback
required = ['final_report.md','run_log.txt','code/analyze.py','code/run_analysis.py',
    'code/build_delivery.py','results/analysis_summary.json','results/analysis_stdout.txt',
    'results/analysis_stderr.txt','inputs/data.csv','inputs/STUDY_DESCRIPTION.md']
assert all((root/p).is_file() for p in required)
checks = {'report_readback_matches_intended':True, 'report_utf8_bytes':path.stat().st_size,
    'report_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'required_files_present':required, 'analysis_exit_code':0,
    'analysis_stderr_bytes':(out/'analysis_stderr.txt').stat().st_size,
    'note':'Prearchive checks. Final archive read-back and integrity inspection printed in actual session tool output.'}
(out/'delivery_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
record('Report created -> final_report.md; actually read back as UTF-8 and checked for nonempty intended conclusion and numerical results. Staging checks -> results/delivery_checks.json. All passed.')
record('Analysis stderr is empty. No statistical execution errors and no missing analysis output records. Initial inspection stdout was not saved separately, as noted above.')
record('Final step in code/build_delivery.py: create ../submission.zip, reopen it, check CRCs, membership and report byte equality. Actual outcome is printed to the session tool transcript after archive creation; this closed archive cannot contain its own subsequent inspection record.')
archive = root.parent/'submission.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for file in sorted(root.rglob('*')):
        if file.is_file():
            z.write(file,arcname=str(Path('submission')/file.relative_to(root)))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    names = z.namelist()
    assert all('submission/'+p in names for p in required)
    assert z.read('submission/final_report.md') == path.read_bytes()
print('ACTUAL REPORT READ-BACK:')
print(readback)
print('ACTUAL FINAL ARCHIVE INSPECTION: all CRCs pass; report bytes match; required report, code, results, inputs and execution log are included.')
print('\n'.join(names))
print(f'Archive bytes: {archive.stat().st_size}; final report bytes: {path.stat().st_size}')
