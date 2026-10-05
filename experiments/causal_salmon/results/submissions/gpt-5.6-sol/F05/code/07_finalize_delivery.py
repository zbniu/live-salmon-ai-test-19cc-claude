"""Record the actual saving failure and refresh the archive without rerunning analyses."""
from pathlib import Path
import datetime
import hashlib
import json
import zipfile

failure='library upload failed: could not read Codex auth from /root/.codex/auth.json\n'
Path('submission/results/07_save_error.txt').write_text(failure,encoding='utf-8')
with Path('submission/run_log.txt').open('a',encoding='utf-8') as f:
    f.write('\nAfter archive verification, the bundled saving helper was invoked on final_report.md and submission.zip.\n')
    f.write('Actual tool exit_code=1; tool output copied verbatim to results/07_save_error.txt. No successful persistent save was reported.\n')
    f.write(f'07_finalize_delivery.py {datetime.datetime.now(datetime.timezone.utc).isoformat()}: recorded saving error and rebuilt archive to include it.\n')
    f.write('No analyses were rerun and earlier execution streams/results were retained. Final archive inspection is in the session tool transcript.\n')
Path('submission/results/07_delivery_status.json').write_text(json.dumps({
    'local_report_created_and_read_back':True,'persistent_saving_succeeded':False,
    'session_download_paths':['submission/final_report.md','submission.zip'],
    'previous_execution_records_retained':True
},indent=2)+'\n')
with zipfile.ZipFile('submission.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in sorted(Path('submission').rglob('*')):
        if p.is_file(): z.write(p,p.as_posix())
with zipfile.ZipFile('submission.zip') as z:
    assert z.testzip() is None
    assert z.read('submission/final_report.md')==Path('submission/final_report.md').read_bytes()
    assert z.read('submission/run_log.txt')==Path('submission/run_log.txt').read_bytes()
    assert z.read('submission/final_report.md').decode('utf-8').strip()
    assert '0.848 points' in z.read('submission/final_report.md').decode('utf-8')
    for prefix in ['submission/code/','submission/results/']:
        assert any(n.startswith(prefix) for n in z.namelist())
    assert 'submission/results/01_inspect.stderr.txt' in z.namelist()
    assert 'submission/results/07_save_error.txt' in z.namelist()
    print('Final archive inspected successfully. Member count:',len(z.namelist()))
    print('\n'.join(z.namelist()))
print('Report bytes:',Path('submission/final_report.md').stat().st_size)
print('Archive bytes:',Path('submission.zip').stat().st_size)
print('Archive SHA256:',hashlib.sha256(Path('submission.zip').read_bytes()).hexdigest())
