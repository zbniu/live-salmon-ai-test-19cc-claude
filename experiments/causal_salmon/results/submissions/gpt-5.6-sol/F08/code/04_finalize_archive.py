"""Retain delivery error record and repackage; do not repeat analyses."""
from pathlib import Path
from datetime import datetime, timezone
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SUB = ROOT / 'submission'
LOG = SUB / 'run_log.txt'
with LOG.open('a', encoding='utf-8') as f:
    f.write(datetime.now(timezone.utc).isoformat()+' BEGIN code/04_finalize_archive.py.\n')
    f.write('Delivery record: after successful 03_deliver.py, the supplied persistence helper failed before any upload began because its local authentication was unavailable (exit 1). Its console error was displayed in the session and was not saved as a separate file. No research data was accessed or analysis repeated. The available host file-upload action then saved the report successfully; local file metadata was applied successfully.\n')

report = (SUB / 'final_report.md').read_text(encoding='utf-8')
assert report.strip() and '1.20' in report and '0.79 to 1.61' in report
archive = ROOT / 'submission.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as zz:
    for p in sorted(SUB.rglob('*')):
        if p.is_file() and p != LOG:
            zz.write(p, p.relative_to(ROOT))
with zipfile.ZipFile(archive) as zz:
    assert zz.testzip() is None
    assert zz.read('submission/final_report.md').decode('utf-8') == report
    assert any(n.startswith('submission/code/') for n in zz.namelist())
    assert any(n.startswith('submission/results/') for n in zz.namelist())

verification = SUB / 'results/04_final_archive_verification.json'
verification.write_text(json.dumps({'nonempty_report_readback_verified': True,
    'archive_report_matches': True, 'code_present': True, 'results_present': True,
    'crc_check_passed': True,
    'note': 'Verified archive before adding this result and the updated log; complete archive inspected again below.'}, indent=2)+'\n')
with LOG.open('a', encoding='utf-8') as f:
    f.write('04_finalize_archive.py: final_report.md read back; archive report/code/results verified with CRC check; results/04_final_archive_verification.json produced. Updated log and verification appended; final complete archive inspection output displayed in the session. No separate stdout file. No statistical analyses rerun.\n')
with zipfile.ZipFile(archive, 'a', zipfile.ZIP_DEFLATED) as zz:
    zz.write(verification, verification.relative_to(ROOT))
    zz.write(LOG, LOG.relative_to(ROOT))
with zipfile.ZipFile(archive) as zz:
    names = zz.namelist()
    assert len(names) == len(set(names))
    assert zz.testzip() is None
    assert zz.read('submission/final_report.md').decode('utf-8') == report
    assert zz.read('submission/run_log.txt') == LOG.read_bytes()
    assert all('submission/'+str(p.relative_to(SUB)) in names for p in SUB.rglob('*') if p.is_file())
    print('FINAL DELIVERY VALIDATION PASSED: report, code, results and execution record present; all '+str(len(names))+' files verified.')
    print('\n'.join(names))
print('Report read back successfully: '+str(len(report.encode('utf-8')))+' UTF-8 bytes.')
