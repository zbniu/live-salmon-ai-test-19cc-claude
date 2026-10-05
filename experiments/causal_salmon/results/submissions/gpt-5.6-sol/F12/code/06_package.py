"""Package existing results, read the report back, and inspect the ZIP.

Final archive verification is printed to the execution-tool output; that
last terminal output is deliberately not reconstructed as an archived log.
"""
from pathlib import Path
import datetime, zipfile, json

root=Path(__file__).resolve().parents[2];sub=root/'submission'
report=(sub/'final_report.md').read_text(encoding='utf-8')
assert report.strip() and '+1.24 points' in report and '0.81 to 1.66' in report
files=sorted(p for p in sub.rglob('*') if p.is_file())
code=[p for p in files if p.parent==sub/'code']
results=[p for p in files if p.parent==sub/'results']
assert code and results and (sub/'run_log.txt').stat().st_size>0
pre=dict(report_readback_success=True,report_utf8_bytes=len(report.encode('utf-8')),
         code_file_count=len(code),results_file_count=len(results),
         verification_scope='Report and source inventory checked before packaging. Final ZIP inspection printed to execution tool, not stored inside ZIP.')
(sub/'results'/'06_prepackage_checks.json').write_text(json.dumps(pre,indent=2),encoding='utf-8')
with (sub/'run_log.txt').open('a',encoding='utf-8') as log:
    log.write(f'\n{datetime.datetime.now(datetime.timezone.utc).isoformat()} code/06_package.py invoked directly. Read back final_report.md and confirmed the adopted answer; wrote results/06_prepackage_checks.json. Next creates submission.zip and inspects its report and required components. Final archive verification output is retained in the execution-tool transcript only, not as an archived result file.\n')
archive=root/'submission.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(sub.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(archive) as z:
    names=z.namelist()
    assert z.testzip() is None
    assert z.read('submission/final_report.md').decode('utf-8')==report
    assert 'submission/run_log.txt' in names
    assert any(n.startswith('submission/code/') for n in names)
    assert any(n.startswith('submission/results/') for n in names)
    assert len(names)==len(set(names))
print('READBACK OF FINAL REPORT\n'+report)
print('ARCHIVE INSPECTION\n'+json.dumps(dict(path=str(archive),bytes=archive.stat().st_size,
      integrity_check='passed',report_matches_local=True,members=names),indent=2))
