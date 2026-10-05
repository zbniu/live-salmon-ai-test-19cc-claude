"""Preserve the delivery-attempt record in the archive; no analysis is rerun."""
from pathlib import Path
from datetime import datetime, timezone
import zipfile

ROOT=Path(__file__).resolve().parents[2]
SUB=ROOT/'submission'
with (SUB/'run_log.txt').open('a',encoding='utf-8') as f:
 f.write('\nDelivery persistence attempt after initial archive inspection:\n')
 f.write('Executed shell command preserved in code/save_deliverables.sh via exec_command.\n')
 f.write('Exit status 1. Tool output: library upload failed: could not read Codex auth from /root/.codex/auth.json\n')
 f.write('No upload was made. The actual raw delivery-attempt console output is in the session tool record, not a separate results file.\n')
 f.write('Local files remain available for the required sandbox download links.\n')
 f.write(f'\nFinal archive refresh {datetime.now(timezone.utc).isoformat()}: code/final_archive_refresh.py\n')
 f.write('Adds this record and the two delivery scripts without rerunning any analysis or replacing earlier analysis/packaging records.\n')
 f.write('Final archive inspection output is retained in the session tool record only.\n')
with zipfile.ZipFile(ROOT/'submission.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(SUB.rglob('*')):
  if p.is_file(): z.write(p,p.relative_to(ROOT))
report=(SUB/'final_report.md').read_text(encoding='utf-8')
assert report.strip() and '1.22 additional score points' in report
with zipfile.ZipFile(ROOT/'submission.zip') as z:
 names=z.namelist()
 assert z.testzip() is None
 assert z.read('submission/final_report.md').decode('utf-8')==report
 assert 'submission/run_log.txt' in names
 assert all(any(n.startswith(prefix) for n in names) for prefix in ['submission/code/','submission/results/'])
 assert 'submission/code/final_archive_refresh.py' in names
 assert 'submission/code/save_deliverables.sh' in names
 assert 'Exit status 1.' in z.read('submission/run_log.txt').decode('utf-8')
 print('Final archive inspection passed; report, code, results, and completed execution/error records included.')
 print('Members:\n'+'\n'.join(names))
print('Final report read back: nonempty UTF-8 report with adopted ATT 1.22 and intended conclusions.')
print('Available files:',SUB/'final_report.md',ROOT/'submission.zip')
