"""Read back the report and build/inspect the required submission archive.

The archive is rebuilt only to incorporate its actual first inspection record
and completed run log. No statistical analyses are repeated.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SUB = ROOT/'submission'
ARCHIVE = ROOT/'submission.zip'
LOG = SUB/'run_log.txt'

def record(message):
    with LOG.open('a',encoding='utf-8') as f:
        f.write(datetime.now(timezone.utc).isoformat()+' '+message+'\n')

def build():
    with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for path in sorted(SUB.rglob('*')):
            if path.is_file():
                z.write(path,path.relative_to(ROOT).as_posix())

def inspect(report_bytes):
    with zipfile.ZipFile(ARCHIVE) as z:
        names = z.namelist()
        assert z.testzip() is None
        assert 'submission/final_report.md' in names
        assert 'submission/run_log.txt' in names
        assert any(n.startswith('submission/code/') for n in names)
        assert any(n.startswith('submission/results/') for n in names)
        assert z.read('submission/final_report.md') == report_bytes
        for p in SUB.rglob('*'):
            if p.is_file():
                assert z.read(p.relative_to(ROOT).as_posix()) == p.read_bytes()
        return names

record('START 04_package; command: python submission/code/04_package.py; outputs: submission.zip, results/delivery_verification.json, results/04_package_console.txt')
try:
    raw = (SUB/'final_report.md').read_bytes()
    report = raw.decode('utf-8')
    assert report.strip() and 'Answer.' in report
    assert '+0.848 points' in report and '+0.454 to +1.241 points' in report
    assert 'actual 600 recipients' in report
    build()
    names = inspect(raw)
    check = {'report_read_back':True,'report_nonempty':True,'report_utf8_bytes':len(raw),
        'intended_primary_result_present':True,'archive_crc_check':'passed',
        'archive_required_categories_present':True,'archive_report_matches_readback':True,
        'all_archived_files_match_local_bytes':True,'first_inspection_members':names,
        'note':'Final packaging-only rebuild adds these actual inspection outputs and the completed log. Final verification is printed in the session tool output.'}
    (SUB/'results'/'delivery_verification.json').write_text(json.dumps(check,indent=2),encoding='utf-8')
    console = 'REPORT READ-BACK (actual file contents):\n'+report+'\nFIRST ARCHIVE INSPECTION: PASSED\n'+'\n'.join(names)+'\n'
    (SUB/'results'/'04_package_console.txt').write_text(console,encoding='utf-8')
    record('04_package first archive inspection PASSED; actual read-back and member checks saved in results/delivery_verification.json and results/04_package_console.txt. No errors. Final packaging-only rebuild and verification follow to embed these records; final stdout remains in the session transcript.')
    build()
    final_names = inspect(raw)
except Exception as e:
    record(f'ERROR 04_package: {type(e).__name__}: {e}')
    raise
print('FINAL REPORT READ-BACK:\n'+report)
print('FINAL ARCHIVE VERIFIED:',ARCHIVE.name,'bytes=',ARCHIVE.stat().st_size)
print('\n'.join(final_names))
print('Report, code, results and run log are present. All archived bytes match local files; archive integrity passed.')
