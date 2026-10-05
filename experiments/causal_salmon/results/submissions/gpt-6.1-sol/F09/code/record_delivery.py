"""Preserve a failed optional persistence preflight; repackage without rerunning analyses."""
from datetime import datetime, timezone
from pathlib import Path
import zipfile
root = Path(__file__).resolve().parents[2]
sub = root / 'submission'
with (sub / 'run_log.txt').open('a', encoding='utf-8') as f:
    f.write(datetime.now(timezone.utc).isoformat() + ' Optional persistent-file upload helper preflight failed, exit 1: could not read Codex auth from /root/.codex/auth.json. No upload was initiated. Report and archive exist in the writable workspace. code/record_delivery.py records this error and repackages without rerunning analysis.\n')
with zipfile.ZipFile(root / 'submission.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    for p in sorted(sub.rglob('*')):
        if p.is_file():
            zf.write(p, p.relative_to(root).as_posix())
with zipfile.ZipFile(root / 'submission.zip') as zf:
    assert zf.testzip() is None
    report = (sub / 'final_report.md').read_text(encoding='utf-8')
    assert len(report.strip()) > 0
    assert zf.read('submission/final_report.md').decode('utf-8') == report
    assert 'submission/run_log.txt' in zf.namelist()
    assert 'submission/code/record_delivery.py' in zf.namelist()
    assert any(n.startswith('submission/results/') for n in zf.namelist())
    print('Final delivery archive verified after recording persistence preflight error. Report, code, results, and run log present; CRC passed.')
    print('\n'.join(zf.namelist()))
