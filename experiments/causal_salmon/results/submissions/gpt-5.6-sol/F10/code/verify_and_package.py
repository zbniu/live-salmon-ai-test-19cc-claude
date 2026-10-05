"""Read back the report, check deliverables, and create/inspect the archive."""
from pathlib import Path
import datetime
import hashlib
import json
import zipfile

root = Path(__file__).resolve().parents[1]
report = root / 'final_report.md'
body = report.read_text(encoding='utf-8')
assert body.strip()
assert 'No causal point estimate is adopted' in body
assert '5.464' in body and '−19.827 to +80.173' in body
assert len(list((root/'code').glob('*.py'))) >= 2
assert (root/'results/analysis.json').is_file()
assert (root/'results/analysis_stdout.txt').is_file()
assert (root/'results/analysis_stderr.txt').is_file()
assert (root/'run_log.txt').is_file()
verification = {'report_readback_nonempty': True, 'report_bytes': report.stat().st_size,
                'report_sha256': hashlib.sha256(report.read_bytes()).hexdigest(),
                'required_conclusion_and_numbers_present': True}
(root/'results/report_verification.json').write_text(json.dumps(verification, indent=2)+'\n', encoding='utf-8')
with (root/'run_log.txt').open('a', encoding='utf-8') as f:
    f.write(f'{datetime.datetime.now(datetime.timezone.utc).isoformat()} Step 2: code/verify_and_package.py reads final_report.md after it was authored from results/analysis.json; report readback and assertions passed. Output: results/report_verification.json.\n')
    f.write('Step 2 then creates ../submission.zip and inspects its member list, report bytes, required components, and ZIP integrity. Inspection stdout is emitted to the session tool transcript; no separate packaging stdout file is archived. Failures, if any, raise an exception to that transcript. No analysis reruns were performed.\n')
archive = root.parent / 'submission.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for p in sorted(root.rglob('*')):
        if p.is_file():
            zf.write(p, p.relative_to(root.parent))
with zipfile.ZipFile(archive) as zf:
    names = zf.namelist()
    assert zf.testzip() is None
    assert 'submission/final_report.md' in names
    assert 'submission/run_log.txt' in names
    assert any(n.startswith('submission/code/') for n in names)
    assert any(n.startswith('submission/results/') for n in names)
    assert zf.read('submission/final_report.md') == report.read_bytes()
print('REPORT READ BACK FROM DISK:\n'+body)
print('\nARCHIVE INSPECTION:')
print('\n'.join(names))
print(f'\nPASS: nonempty intended report, executed code, actual results, run log, and ZIP integrity; {archive.stat().st_size} bytes.')
