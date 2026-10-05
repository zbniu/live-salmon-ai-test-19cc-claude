"""Package the verified submission and inspect the actual archive."""
import datetime
import hashlib
import json
from pathlib import Path
import zipfile

root=Path.cwd()
log=Path('submission/run_log.txt')
with log.open('a',encoding='utf-8') as f:
    f.write(f'\nSTART {datetime.datetime.now(datetime.timezone.utc).isoformat()} 06_package.py\n')
    f.write('05_verify.py produced results/05_report_verification.json and captured the full report read-back in results/05_verify.stdout.txt.\n')
    f.write('06_package.py creates submission.zip using the submission/ tree; no statistical analysis is rerun.\n')

def package():
    with zipfile.ZipFile('submission.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(Path('submission').rglob('*')):
            if p.is_file(): z.write(p,p.as_posix())

package()
with zipfile.ZipFile('submission.zip') as z:
    assert z.testzip() is None
    names=z.namelist()
    assert 'submission/final_report.md' in names
    assert 'submission/run_log.txt' in names
    assert any(p.startswith('submission/code/') for p in names)
    assert any(p.startswith('submission/results/') for p in names)
    assert z.read('submission/final_report.md')==Path('submission/final_report.md').read_bytes()
    record={'initial_archive_crc_ok':True,'report_bytes_match':True,
        'includes_report_code_results_run_log':True,'inspected_member_names':names,
        'note':'Archive rebuilt once after successful inspection to include this verification record and the final packaging log entry; no analyses rerun.'}
Path('submission/results/06_archive_verification.json').write_text(json.dumps(record,indent=2)+'\n')
with log.open('a',encoding='utf-8') as f:
    f.write('Actual first archive inspection: CRC test passed; report matched local report exactly; report, code, results, and run_log all present.\n')
    f.write('Produced results/06_archive_verification.json. Repackaged to include that record and this log.\n')
    f.write('The final archive inspection result is returned in the session tool transcript; no standalone final stdout/stderr capture was made for packaging.\n')
    f.write(f'END {datetime.datetime.now(datetime.timezone.utc).isoformat()} packaging stage\n')
package()
with zipfile.ZipFile('submission.zip') as z:
    assert z.testzip() is None
    assert z.read('submission/final_report.md')==Path('submission/final_report.md').read_bytes()
    assert z.read('submission/run_log.txt')==log.read_bytes()
    assert 'submission/results/06_archive_verification.json' in z.namelist()
    print('Final archive successfully inspected, with matching report and complete log:')
    print('\n'.join(z.namelist()))
print(f'Archive bytes: {Path("submission.zip").stat().st_size}')
print(f'Archive SHA256: {hashlib.sha256(Path("submission.zip").read_bytes()).hexdigest()}')
