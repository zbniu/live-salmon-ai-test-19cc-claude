"""Retain the delivery-helper failure and verify the downloadable local files."""
from datetime import datetime, timezone
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SUB = ROOT/'submission'
failure = '''File-saving attempt after the analysis and first packaging verification:
The platform-supplied library_upload.py helper was executed once with a two-file
request for final_report.md and submission.zip. It exited with status 1.
Actual console error (copied from the session tool result):
library upload failed: could not read Codex auth from /root/.codex/auth.json
No successful persistence result was returned. No retry was performed.
The report and archive remain present in the session writable space and can be
delivered using supported sandbox download links. The supplied platform helper
is not vendored in submission/code/. It is not statistical analysis code.
'''
(SUB/'results'/'persistence_failure.txt').write_text(failure,encoding='utf-8')
with (SUB/'run_log.txt').open('a',encoding='utf-8') as f:
    f.write('\nFile-saving helper attempt (after 04_package): exit=1. Command: python3 /root/.codex/plugins/cache/openai-curated-remote/openai-library/0.1.61/skills/library/scripts/library_upload.py; stdin requested creation of final_report.md and submission.zip. Error and missing successful persistence record are documented in results/persistence_failure.txt, copied from the actual session tool result. No retry.\n')
    f.write(datetime.now(timezone.utc).isoformat()+' START 05_finalize_delivery; command: python submission/code/05_finalize_delivery.py; output: results/persistence_failure.txt and refreshed submission.zip. This packaging-only refresh includes the delivery failure without repeating analyses. Final report read-back and archive verification stdout remain in the session transcript.\n')
report_bytes = (SUB/'final_report.md').read_bytes()
report = report_bytes.decode('utf-8')
assert report.strip() and '+0.848 points' in report
assert '+0.454 to +1.241 points' in report
with zipfile.ZipFile(ROOT/'submission.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(SUB.rglob('*')):
        if p.is_file():
            z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ROOT/'submission.zip') as z:
    members = z.namelist()
    assert z.testzip() is None
    assert z.read('submission/final_report.md')==report_bytes
    for required in ['submission/final_report.md','submission/run_log.txt',
                     'submission/results/persistence_failure.txt']:
        assert required in members
    assert any(p.startswith('submission/code/') for p in members)
    assert any(p.startswith('submission/results/') for p in members)
    for p in SUB.rglob('*'):
        if p.is_file():
            assert z.read(p.relative_to(ROOT).as_posix())==p.read_bytes()
print('FINAL REPORT READ-BACK:\n'+report)
print('FINAL ARCHIVE INSPECTION PASSED; report, executed code, results, input copies, run log, and delivery failure record are present.')
print('\n'.join(members))
print('Download artifacts:',str(SUB/'final_report.md'),str(ROOT/'submission.zip'))
