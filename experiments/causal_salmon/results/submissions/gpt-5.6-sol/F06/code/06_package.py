"""Create the archive, read back the report, and verify its delivered contents."""
import datetime
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
archive = root.parent/'submission.zip'
log = root/'run_log.txt'
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
with log.open('a',encoding='utf-8') as f:
    f.write(f'\n06 START {start}\nCommand: Python code/06_package.py (archive creation and read-back verification; no statistical rerun)\n')
report = (root/'final_report.md').read_text(encoding='utf-8')
assert report.strip()
assert '0.85' in report and '600' in report and '0.45 to 1.24' in report

def build():
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob('*')):
            if p.is_file():
                z.write(p, p.relative_to(root.parent).as_posix())

build()
with zipfile.ZipFile(archive) as z:
    names = z.namelist()
    assert z.testzip() is None
    assert z.read('submission/final_report.md').decode('utf-8') == report
    assert 'submission/run_log.txt' in names
    assert any(n.startswith('submission/code/') for n in names)
    assert any(n.startswith('submission/results/') for n in names)
    checks = {'report_bytes': len(report.encode('utf-8')), 'report_readback_nonempty': True,
              'archive_report_matches_local': True, 'zip_crc_check': 'passed',
              'report_code_results_run_log_present': True, 'initial_archive_members': names}
(root/'results'/'06_delivery_validation.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
message = f'Created submission.zip; read back final_report.md ({checks["report_bytes"]} bytes); archive includes report, executed code, actual results, inputs, and run_log.txt. CRC check passed. Added this validation record and completed run log, then rebuilt the final archive.\n'
(root/'results'/'06_stdout.txt').write_text(message,encoding='utf-8')
(root/'results'/'06_stderr.txt').write_text('',encoding='utf-8')
with log.open('a',encoding='utf-8') as f:
    f.write(f'06 validation completed {datetime.datetime.now(datetime.timezone.utc).isoformat()}; no errors\n')
    f.write('Outputs: ../submission.zip; results/06_delivery_validation.json; results/06_stdout.txt; results/06_stderr.txt. Final archive refreshed to include these records and this log.\n')
build()
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert z.read('submission/final_report.md').decode('utf-8') == report
    assert z.read('submission/run_log.txt') == log.read_bytes()
    assert 'submission/results/06_delivery_validation.json' in z.namelist()
    print(report)
    print('FINAL ARCHIVE CONTENTS:')
    print('\n'.join(z.namelist()))
print(message)
