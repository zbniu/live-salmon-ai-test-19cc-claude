"""Read back the report, validate artifacts, package, and inspect the archive."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, zipfile

root=Path(__file__).resolve().parents[1]
archive=root.parent/'submission.zip'
log=root/'run_log.txt'
with log.open('a',encoding='utf-8') as f:
    f.write(f'\nSTART {datetime.now(timezone.utc).isoformat()}\nCommand: Python code/04_package.py\nOutputs: ../submission.zip, results/archive_check.json; final archive readback is returned as tool stdout.\n')
report=(root/'final_report.md').read_text(encoding='utf-8')
assert report.strip()
for expected in ['1.21 points','0.78 to 1.63 points','600 recipients','average treatment effect']:
    assert expected in report, expected
assert any((root/'code').glob('*.py'))
assert any((root/'results').glob('*.json'))
assert (root/'results/01_inspect_stdout.txt').read_text().startswith('Traceback')
assert (root/'results/01_inspect_retry_stdout.txt').stat().st_size>0
assert (root/'results/02_analysis_stdout.txt').stat().st_size>0
assert (root/'results/bootstrap_estimates.csv').stat().st_size>0

def pack():
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob('*')):
            if p.is_file():
                z.write(p,p.relative_to(root.parent))

def inspect():
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        names=z.namelist()
        assert 'submission/final_report.md' in names
        assert 'submission/run_log.txt' in names
        assert any(n.startswith('submission/code/') for n in names)
        assert any(n.startswith('submission/results/') for n in names)
        assert z.read('submission/final_report.md').decode('utf-8')==report
        return names

pack()
names=inspect()
check={'report_readback_nonempty':True,'report_bytes':len(report.encode('utf-8')),'report_sha256':hashlib.sha256(report.encode('utf-8')).hexdigest(),'initial_archive_integrity_ok':True,'initial_archive_members':names,'note':'After this actual initial archive check, the archive is repacked to include this verification record and the completed execution log, and inspected again.'}
(root/'results/archive_check.json').write_text(json.dumps(check,indent=2)+'\n',encoding='utf-8')
with log.open('a',encoding='utf-8') as f:
    f.write(f'END {datetime.now(timezone.utc).isoformat()} exit_status=0: report readback and initial archive checks passed; archive repacked below to include these records. Final archive verification is returned to the calling tool.\n')
pack()
names=inspect()
with zipfile.ZipFile(archive) as z:
    assert z.read('submission/run_log.txt')==log.read_bytes()
    assert 'submission/results/archive_check.json' in names
print('FINAL REPORT READBACK:\n'+report)
print('FINAL ARCHIVE INSPECTION: integrity OK; '+str(len(names))+' files; report, code, results, and completed execution record present.')
print('\n'.join(names))
print('Archive bytes: '+str(archive.stat().st_size))
