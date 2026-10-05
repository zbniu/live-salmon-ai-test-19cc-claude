"""Write the standalone report, read it back, and package and inspect delivery."""
from datetime import datetime, timezone
from pathlib import Path
import json
import zipfile

root = Path(__file__).resolve().parents[2]
sub = root / 'submission'
summary = json.loads((sub / 'results' / 'analysis_summary.json').read_text(encoding='utf-8'))
control, treated = summary['groups']
coefs = [r['treatment_association'] for r in summary['descriptive_regressions']]
report = f'''# Final report: Did arrangement Q increase change among its recipients?

**Answer: The supplied material does not support a definite answer. Neither the sign nor the average size of Q's causal effect on its 600 recipients is identified. No numerical causal-effect estimate is adopted.**

The question asks what happened to recipients because they received Q, compared with what would have happened to those same units without Q. Its target is the average of `z(1) − z(0)` over the 600 recipients, where `z(1)` and `z(0)` are a unit's changes with and without Q. For recipients, only `z(1)` is observed. A positive observed change is not, by itself, a positive causal effect.

## Data and executed analyses

I used only the attached study description and the complete attached CSV. All 2,000 rows and all three columns (`x`, `y`, `z`) were read. Validation found 600 recipients, 1,400 nonrecipients, no missing or nonfinite values, and baseline values within 0–100. No rows were dropped. The analyses computed group summaries, baseline overlap and bins, and descriptive ordinary least squares regressions using all rows. Regression models included an intercept, receipt indicator, and baseline terms of degree one, two, or three; HC3 standard errors were saved as working-model diagnostics, not causal uncertainty measures.

| Observed quantity | Recipients | Nonrecipients |
|---|---:|---:|
| Number of units | 600 | 1,400 |
| Mean baseline `y` | {treated['baseline_mean']:.3f} | {control['baseline_mean']:.3f} |
| Mean change `z` | {treated['change_mean']:.3f} | {control['change_mean']:.3f} |
| Baseline range | {treated['baseline_min']:.3f}–{treated['baseline_max']:.3f} | {control['baseline_min']:.3f}–{control['baseline_max']:.3f} |

The **unadjusted observed difference in mean change is +{summary['unadjusted_change_difference']:.3f} points** (recipient mean minus nonrecipient mean). This is a descriptive comparison, **not the answer to the causal research question**. Recipients also had a mean baseline {summary['unadjusted_baseline_difference']:.3f} points higher.

The receipt coefficients after adjusting for baseline were +{coefs[1]:.3f} points with a linear baseline term, +{coefs[2]:.3f} with quadratic terms, and +{coefs[3]:.3f} with cubic terms. These are model-dependent associations. Their similarity does not establish that unrecorded selection factors have been removed.

## Why the causal question remains unresolved

The 900 candidates were selected using baseline, unrecorded circumstances, and an independent random component. Q was then assigned to the 600 candidates with the highest baselines. The independent component makes candidate selection partly random; it does not make actual receipt random or establish that recipients and nonrecipients have comparable untreated outcomes, even at the same baseline. The unrecorded circumstances could affect both selection and change, and the description supplies no assumption excluding this possibility. Neither the random component nor candidate status is available for analysis.

Baseline overlap alone cannot solve this problem. There were {summary['overlap']['controls_at_or_above_minimum_recipient_baseline']} nonrecipients at or above the lowest recipient baseline ({summary['overlap']['minimum_recipient_baseline']:.3f}), and {summary['overlap']['controls_below_minimum_recipient_baseline']} below it. Similar baseline values do not establish comparability on unrecorded circumstances. Having some chance of candidate status is also different from having comparable chances of actual receipt after the capacity rule.

The baseline ranking rule does not, on the supplied assumptions, identify the average effect for all recipients through a cutoff analysis. Such an analysis would need additional assumptions about outcome continuity and candidate selection near a cutoff; a local effect would additionally need assumptions to represent all 600 recipients. Those assumptions are not supplied or established here. Uniform Q, no switching, no interference, consistent measurement, blinded follow-up recording, and complete inclusion are useful safeguards, but do not supply recipients' missing untreated outcomes.

## Direct check of the ambiguity

I constructed three hypothetical completions of the missing potential outcomes. For an assumed constant effect `d`, define `z(0) = z − d*x` and `z(1) = z + d*(1 − x)`. Each completion reproduces every observed change exactly. Choosing `d = +1`, `0`, or `−1` yields, respectively, a one-point benefit, no effect, or a one-point harm for every recipient. Code verified that all potential follow-up measurements in all three examples also remain within 0–100. These are logical examples, not estimates of how the simulation actually generated outcomes. The supplied restrictions on outcomes do not distinguish them; none requires changing the observed assignment or selection rule.

Thus the positive observed comparisons are compatible with causal benefit, no benefit, or harm. **The numerical difference +{summary['unadjusted_change_difference']:.3f} points describes the observed groups; it is not an identified effect of Q. Whether Q increased recipients' change, and by how much, remains undetermined.**

## Execution record

`code/analyze.py` performed the analyses once, launched by `code/run_analysis.py`. `results/` contains the numerical tables, JSON summary, actual captured standard output and standard error, and delivery verification. `code/finalize.py` generated and checked this report and archive. `run_log.txt` records execution order and distinguishes early terminal inspections from captured analysis records. No internet or external data were used.
'''
report_path = sub / 'final_report.md'
report_path.write_text(report, encoding='utf-8')
readback = report_path.read_text(encoding='utf-8')
assert readback == report and len(readback.strip()) > 0
assert 'No numerical causal-effect estimate is adopted.' in readback
assert f'+{summary["unadjusted_change_difference"]:.3f}' in readback
print('REPORT READ-BACK:\n' + readback)
log = sub / 'run_log.txt'
stamp = lambda: datetime.now(timezone.utc).isoformat()
with log.open('a', encoding='utf-8') as f:
    f.write(f'{stamp()} code/finalize.py: generated final_report.md from executed analysis_summary.json; read back UTF-8 report and verified nonempty, exact content, conclusion, and intended numerical result.\n')

archive = root / 'submission.zip'
def package():
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(sub.rglob('*')):
            if path.is_file():
                zf.write(path, path.relative_to(root).as_posix())

def inspect():
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        assert zf.testzip() is None
        assert zf.read('submission/final_report.md').decode('utf-8') == report
        assert 'submission/run_log.txt' in names
        assert all(f'submission/code/{n}' in names for n in ['analyze.py', 'run_analysis.py', 'finalize.py'])
        assert all(f'submission/results/{n}' in names for n in ['analysis_summary.json', 'group_summary.csv', 'baseline_bins.csv', 'descriptive_regressions.csv', 'hypothetical_counterfactual_examples.csv', 'analysis_stdout.txt', 'analysis_stderr.txt'])
        return names

package()
names = inspect()
verification = dict(report_readback_nonempty=True, report_readback_matches_intended_content=True,
    initial_archive_crc_pass=True, initial_archive_members=names,
    note='The final archive is rebuilt once to include this actual verification record and updated run log, then inspected again. No analysis is repeated.')
(sub / 'results' / 'delivery_verification.json').write_text(json.dumps(verification, indent=2) + '\n', encoding='utf-8')
with log.open('a', encoding='utf-8') as f:
    f.write(f'{stamp()} code/finalize.py: initial submission.zip created and inspected: CRC passed; report content matched; code, results, and execution record present. Actual inspection saved in results/delivery_verification.json. Rebuilding archive to include this record and updated log, followed by final inspection. No analysis rerun.\n')
package()
final_names = inspect()
assert 'submission/results/delivery_verification.json' in final_names
print('FINAL ARCHIVE INSPECTION: report, code, results, and run log present; CRC passed; report content matches.')
print('\n'.join(final_names))
