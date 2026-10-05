"""Read back the actual report, package all deliverables, and inspect the ZIP.

Two packaging passes include the first pass's real inspection output and
completed run-log entry. No statistical analysis is rerun.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, zipfile
root=Path(__file__).resolve().parents[2];s=root/'submission'
log=s/'run_log.txt';archive=root/'submission.zip'
def stamp(): return datetime.now(timezone.utc).isoformat()
with log.open('a') as f:
 f.write(f'\nSTART {stamp()}\nCommand: Python submission/code/04_package.py\nOperation: read back final_report.md, package files, inspect archive; no analysis rerun.\n')
report=(s/'final_report.md').read_text(encoding='utf-8')
assert report.strip() and '1.24' in report and '0.81' in report and '1.65' in report
print('READ-BACK OF FINAL REPORT:\n'+report)
def build():
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for p in sorted(s.rglob('*')):
   if p.is_file(): z.write(p,p.relative_to(root))
def inspect():
 with zipfile.ZipFile(archive) as z:
  names=z.namelist()
  assert z.testzip() is None
  assert 'submission/final_report.md' in names
  assert z.read('submission/final_report.md').decode('utf-8')==report
  assert 'submission/run_log.txt' in names
  assert any(n.startswith('submission/code/') for n in names)
  assert any(n.startswith('submission/results/') for n in names)
  return names
build();first_names=inspect()
checks={'checked_at_UTC':stamp(),'verified_archive':'submission.zip',
 'pass':'First packaging pass, before adding this record and completion log',
 'nonempty_utf8_report_read_back':True,'archived_report_matches_local':True,
 'archive_integrity_check':'passed','includes_report_code_results_run_log':True,
 'first_pass_archive_members':first_names}
(s/'results/archive_verification.json').write_text(json.dumps(checks,indent=2)+'\n')
with log.open('a') as f:
 f.write(f'END {stamp()} exit=0; first archive passed integrity, report read-back/match, and required-entry checks.\n')
 f.write('Output: submission.zip; actual inspection record: submission/results/archive_verification.json.\n')
 f.write('Final packaging pass includes this completed log and first-pass verification record. Final integrity and required-entry inspection is also performed; its stdout is retained in the session tool record, not a separate console file.\n')
build();names=inspect()
assert 'submission/results/archive_verification.json' in names
print('FINAL ARCHIVE INSPECTION PASSED. Members:\n'+'\n'.join(names))
print(f'Archive bytes: {archive.stat().st_size}; report bytes: {(s/"final_report.md").stat().st_size}')
