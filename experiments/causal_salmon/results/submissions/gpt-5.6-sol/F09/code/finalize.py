"""Write the report from executed results, preserve inputs, and verify delivery."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

root = Path(__file__).resolve().parents[2]
sub = root / 'submission'
result = json.loads((sub / 'results/analysis.json').read_text(encoding='utf-8'))
models = result['descriptive_models']
report = '''# Effect of arrangement Q on recipients' change

**Answer:** The supplied material does not establish whether receiving arrangement Q increased change `z` for the 600 recipients, or by how much. The sign and magnitude of the causal effect among recipients are not identified. No numerical causal effect is adopted.

The question concerns the average effect on the units that actually received Q: the mean, across those 600 units, of `z(1) − z(0)`, where `z(1)` is change under Q and `z(0)` is change without Q. Recipients' observed changes reveal `z(1)`, but their changes without Q are unobserved. Because baseline precedes Q, an effect on change is also an effect on the follow-up measurement with baseline held fixed.

## Analysis of the complete data

I used only the supplied study description and CSV. All 2,000 rows were read and retained: 600 recipients and 1,400 nonrecipients. The file has exactly the three stated columns, no missing or nonfinite values, no duplicate full rows, and baseline measurements within 0–100.

| Observed quantity | Q recipients | Nonrecipients |
| --- | ---: | ---: |
| Number of units | 600 | 1,400 |
| Mean baseline `y` | 66.068 | 57.350 |
| Mean change `z` | 14.104 | 8.641 |
| Standard deviation of change | 3.906 | 3.758 |

The observed difference in mean change is **{difference:.3f} points** (recipients minus nonrecipients). This is a descriptive group difference; it does not answer the causal research question. Recipients' positive mean change likewise does not establish that Q caused that change.

As descriptive adjustment checks, I fitted ordinary least squares on all 2,000 rows, with change as the outcome, a recipient indicator, and either a linear baseline term or baseline terms through degree three. The recipient coefficients were **{linear:.3f} points** and **{cubic:.3f} points**, respectively. These quantify associations under those additive regression specifications. Their similar values do not validate the causal assumptions, and neither is adopted as an effect of Q.

Baseline ranges overlap substantially: recipients span 56.995–74.988 and nonrecipients span 45.024–74.918. Of the 600 recipients, 594 lie within the observed nonrecipient baseline range and six exceed its maximum. There are 793 nonrecipients below the lowest recipient baseline. Range overlap makes some baseline comparisons possible, but does not establish comparability on unrecorded circumstances. Baseline-bin summaries and full regression coefficients are provided in the results.

## Why the causal answer is undetermined

Candidate selection depended on baseline, unrecorded circumstances, and an independent random number. Acceptance then selected the 600 highest-baseline candidates. Thus receipt of Q was not assigned independently of unit characteristics, even at a given baseline. The unrecorded circumstances could also affect the change a unit would have had without Q; the supplied description neither rules this out nor establishes it. Baseline adjustment, matching, or weighting cannot establish that this source of confounding is absent.

The independent random number does not make the entire selection value random: the other components still influence candidacy. Neither that number nor candidate status is available, so it cannot be used here as an observed randomized encouragement or instrument. Complete follow-up, blinded recording, consistent treatment, and no interference help interpret measurements, but do not supply recipients' missing outcomes without Q.

The baseline ranking also does not by itself identify the effect for all recipients through a regression discontinuity analysis. A local threshold comparison would require additional continuity and selection assumptions; extending a local effect to all 600 recipients would require further assumptions. Those are not supplied or established by this dataset.

To illustrate the missing information, the code checked three hypothetical completions of recipients' outcomes without Q: set each recipient's `z(0)` equal to their observed `z`, to `z − 1`, or to `z + 1`. These yield recipient average effects of 0, +1, and −1 point while leaving every observed row unchanged. Even their corresponding counterfactual follow-up measurements (`y + z(0)`) all lie within 0–100. These are illustrative possibilities, not estimates or simulated observations. No supplied restriction on outcome production excludes them. The unobserved outcomes of nonrecipients under Q can also be filled in without changing any observations.

Consequently, the data show larger observed changes among recipients, including after the illustrated baseline adjustments, but do not determine whether Q caused an increase. A definite causal answer would require additional justified identification assumptions or additional design information. Statistical precision around the observed associations would not resolve this identification problem.

## Reproducibility

`code/analyze.py` contains the executed analysis; `code/run_analysis.py` captured its stdout, stderr, and exit code. `code/finalize.py` generated this report and checked delivery. `results/` contains actual execution outputs, including group summaries, baseline bins, regression coefficients, illustrative counterfactual checks, source hashes, and software versions. `run_log.txt` records execution order and notes preliminary session output that was not separately captured. Copies of the two original inputs are in `inputs/`. No analysis was repeated to replace an earlier execution record.
'''.format(difference=result['naive_difference_in_mean_change'],
           linear=models[1]['x_coefficient'], cubic=models[2]['x_coefficient'])
path = sub / 'final_report.md'
path.write_text(report, encoding='utf-8')
inputs = sub / 'inputs'
inputs.mkdir(exist_ok=True)
shutil.copyfile(root / 'upload/data(10).csv', inputs / 'data.csv')
shutil.copyfile(root / 'upload/STUDY_DESCRIPTION(10).md', inputs / 'STUDY_DESCRIPTION.md')
readback = path.read_text(encoding='utf-8')
assert readback == report and len(readback.strip()) > 0
assert 'No numerical causal effect is adopted.' in readback
assert f"{result['naive_difference_in_mean_change']:.3f}" in readback
for name, expected in result['source_sha256'].items():
    assert hashlib.sha256((inputs / name).read_bytes()).hexdigest() == expected
log = sub / 'run_log.txt'
with log.open('a', encoding='utf-8') as f:
    f.write(f'\n{datetime.now(timezone.utc).isoformat()} Executed code/finalize.py with the primary Python runtime.\n')
    f.write('Read results/analysis.json; created final_report.md from those outputs; copied the two unchanged inputs.\n')
    f.write('Actual report readback: nonempty UTF-8; matches intended report; contains the conclusion and reported observed difference. Source-copy hashes matched.\n')

archive = root / 'submission.zip'
def build_archive():
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(sub.rglob('*')):
            if p.is_file():
                z.write(p, p.relative_to(root).as_posix())

def inspect_archive():
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        names = z.namelist()
        assert 'submission/final_report.md' in names
        assert 'submission/run_log.txt' in names
        assert any(n.startswith('submission/code/') for n in names)
        assert any(n.startswith('submission/results/') for n in names)
        for p in sub.rglob('*'):
            if p.is_file():
                assert z.read(p.relative_to(root).as_posix()) == p.read_bytes()
        assert z.read('submission/final_report.md').decode('utf-8') == report
    return names

build_archive()
names = inspect_archive()
checks = {'report_nonempty_utf8': True, 'report_matches_intended_text': True,
          'archive_crc_and_all_file_bytes_verified': True,
          'archive_contains_report_code_results_execution_record': True,
          'inspected_initial_archive_members': names,
          'note': 'Initial archive inspected, then rebuilt to include this verification record and the updated run log. Final archive is inspected again without rerunning analysis.'}
(sub / 'results/delivery_verification.json').write_text(json.dumps(checks, indent=2) + '\n', encoding='utf-8')
with log.open('a', encoding='utf-8') as f:
    f.write('Archive created and actually inspected: CRC checks passed, report/code/results/run_log present, every archived file matched local bytes.\n')
    f.write('Wrote results/delivery_verification.json. Rebuilding archive to include verification and this log; final inspection follows in this same execution. No statistical analysis rerun.\n')
build_archive()
final_names = inspect_archive()
print('REPORT READBACK:\n' + readback)
print('\nFINAL ARCHIVE INSPECTION: all required content present; CRC and every file byte match passed.')
print('\n'.join(final_names))
print(f'Archive size: {archive.stat().st_size} bytes')
