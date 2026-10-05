"""Read back the actual report, package files, and inspect the actual ZIP."""
from pathlib import Path
from datetime import datetime,timezone
import zipfile, json
root=Path(__file__).resolve().parents[2]
folder=root/'submission'; archive=root/'submission.zip'
report=(folder/'final_report.md').read_text(encoding='utf-8')
assert report.strip() and '1.11' in report and '0.70 to 1.52' in report
assert 'adopted estimate answering the research question' in report
assert any((folder/'code').iterdir()) and any((folder/'results').iterdir())
with (folder/'run_log.txt').open('a') as f:
 f.write('\n'+datetime.now(timezone.utc).isoformat()+' BEGIN code/package_submission.py: read back full report; verified nonempty intended answer.\n')
def pack():
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(folder.rglob('*')):
   if p.is_file(): z.write(p,p.relative_to(root))
def inspect():
 with zipfile.ZipFile(archive) as z:
  names=z.namelist()
  assert z.testzip() is None
  assert z.read('submission/final_report.md').decode('utf-8')==report
  assert 'submission/run_log.txt' in names
  assert any(n.startswith('submission/code/') for n in names)
  assert any(n.startswith('submission/results/') for n in names)
  return {'archive':'submission.zip','integrity':'passed','report_matches_readback':True,'entries':names}
pack()
first=inspect()
(folder/'results/archive_inspection.json').write_text(json.dumps(first,indent=2)+'\n')
with (folder/'run_log.txt').open('a') as f:
 f.write(datetime.now(timezone.utc).isoformat()+' Inspected actual provisional ZIP: CRC passed, report matches, code/results/log present; output results/archive_inspection.json.\n')
 f.write('Repackaging to include this actual inspection record and updated log; no analysis rerun.\n')
pack()
final=inspect()
print('REPORT READBACK:\n'+report)
print('FINAL ARCHIVE INSPECTION:\n'+json.dumps(final,indent=2))
print('ZIP bytes:',archive.stat().st_size)
