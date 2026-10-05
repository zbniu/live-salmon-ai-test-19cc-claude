"""Archive and verify the actual report, code, outputs, and run log; no reanalysis."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

base = Path(__file__).resolve().parents[1]
root = base.parent
log = base / 'run_log.txt'
now = lambda: datetime.now(timezone.utc).isoformat()
inputs = base / 'inputs'
inputs.mkdir(exist_ok=True)
for name in ['data(20261004-180654).csv', 'STUDY_DESCRIPTION(20261004-180655).md']:
    shutil.copyfile(root / 'upload' / name, inputs / name)

report_path = base / 'final_report.md'
report = report_path.read_text(encoding='utf-8')
assert report.strip() and 'not identified' in report
assert '5.405' in report and '−20.168 to +79.832' in report
assert 'not established' in report
with log.open('a', encoding='utf-8') as f:
    f.write(f'{now()} START 3: code/package_submission.py; no numerical reanalysis.\n')
    f.write('Copied the two supplied inputs into inputs/ for reproducibility.\n')
    f.write('Read back final_report.md as UTF-8; nonempty and intended conclusion/numerical results verified.\n')
    f.write('Initial shell-inspection output was not saved; analysis stdout/stderr for both attempts are retained.\n')

archive = root / 'submission.zip'
def write_zip():
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(base.rglob('*')):
            if p.is_file():
                z.write(p, p.relative_to(root).as_posix())

write_zip()
with zipfile.ZipFile(archive) as z:
    names = z.namelist()
    assert z.testzip() is None
    assert 'submission/final_report.md' in names
    assert 'submission/run_log.txt' in names
    assert any(n.startswith('submission/code/') for n in names)
    assert any(n.startswith('submission/results/') for n in names)
    assert z.read('submission/final_report.md').decode('utf-8') == report
    for p in base.rglob('*'):
        if p.is_file():
            assert z.read(p.relative_to(root).as_posix()) == p.read_bytes()

verification = {
    'report_utf8_nonempty': True,
    'report_sha256': hashlib.sha256(report.encode('utf-8')).hexdigest(),
    'archive_contains_report_code_results_run_log': True,
    'archive_crc_check': 'passed',
    'archive_report_matches_read_back_report': True,
    'all_initial_archive_members_match_local_bytes': True,
    'archive_members_before_adding_verification_output': names
}
(base / 'results' / 'delivery_verification.json').write_text(
    json.dumps(verification, indent=2) + '\n', encoding='utf-8')
with log.open('a', encoding='utf-8') as f:
    f.write(f'{now()} END 3: initial archive integrity, required members, and exact report bytes verified.\n')
    f.write('Output: results/delivery_verification.json; submission.zip. Repackaged to include this verification output and completed log.\n')
write_zip()
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert z.read('submission/final_report.md').decode('utf-8') == report
    assert z.read('submission/run_log.txt') == log.read_bytes()
    assert 'submission/results/delivery_verification.json' in z.namelist()
    print('ARCHIVE MEMBERS:\n' + '\n'.join(z.namelist()))
print('\nREPORT READ BACK:\n' + report)
print(f'\nVERIFIED: {archive} ({archive.stat().st_size} bytes)')
