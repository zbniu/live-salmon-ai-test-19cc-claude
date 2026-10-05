"""Record delivery operations and refresh archive; never rerun analysis."""
from pathlib import Path
from datetime import datetime, timezone
import json
import zipfile

root = Path(__file__).resolve().parents[2]
sub = root/'submission'
with (sub/'run_log.txt').open('a', encoding='utf-8') as f:
    f.write(f'\n[{datetime.now(timezone.utc).isoformat()}] code/package_and_verify.py completed with exit 0: report read-back and ZIP member/integrity inspection PASS. Its console output was returned in the session tool transcript; no separate console file was saved.\n')
    f.write('Subsequent persistence helper invocation attempted to save final_report.md and submission.zip. Exit 1 before transfer: authentication unavailable. No persistent uploads succeeded. Local files remain available for supported sandbox download links. This was a delivery operation, not an analysis run.\n')
    f.write('EXECUTE code/finalize_archive.py: record packaging and persistence status; write results/delivery_verification.json and rebuild/inspect archive to include these records. No statistical analyses rerun.\n')
report = (sub/'final_report.md').read_text(encoding='utf-8')
assert report.strip() and '0.8477' in report
status = dict(report_readback='PASS', report_utf8_bytes=len(report.encode('utf-8')),
    initial_archive_inspection='PASS', persistent_upload='FAILED before transfer: authentication unavailable',
    local_delivery='final_report.md and submission.zip created; supported sandbox links available',
    analysis_rerun_for_delivery=False)
(sub/'results/delivery_verification.json').write_text(json.dumps(status,indent=2)+'\n',encoding='utf-8')
archive = root/'submission.zip'
files = sorted(p for p in sub.rglob('*') if p.is_file())
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for path in files:
        z.write(path,path.relative_to(root))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    names=z.namelist()
    assert z.read('submission/final_report.md').decode('utf-8')==report
    for name in ['submission/run_log.txt','submission/code/analyze.py',
                 'submission/results/analysis.json','submission/results/delivery_verification.json']:
        assert name in names
print('Final report read-back: PASS. Final archive integrity and required contents: PASS.')
print('\n'.join(names))
