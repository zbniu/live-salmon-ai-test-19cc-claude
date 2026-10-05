"""Retain actual packaging records and finalize the archive; no analysis."""
from pathlib import Path
import datetime
import shutil
import zipfile

root=Path(__file__).resolve().parents[1]
log=root/'run_log.txt'
shutil.copyfile(root.parent/'submission_package_console.txt',root/'results/05_package_console.txt')
shutil.copyfile(root.parent/'submission_archive_check.txt',root/'results/archive_initial_inspection.txt')
with log.open('a',encoding='utf-8') as f:
    f.write('END code/05_package.py: exit=0; captured stdout: results/05_package_console.txt. Actual archive inspection: results/archive_initial_inspection.txt.\n')
    f.write(f'\nSTART {datetime.datetime.now(datetime.timezone.utc).isoformat()}: code/06_finalize.py. Copies actual packaging records into results/ and repackages; no analysis rerun.\n')
report=(root/'final_report.md').read_text(encoding='utf-8')
assert report.strip() and '1.25' in report and '0.83 to 1.67' in report
archive=root.parent/'submission.zip'
def package():
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(root.parent))
package()
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert z.read('submission/final_report.md').decode('utf-8')==report
    names=z.namelist()
    assert all(any(n.startswith('submission/'+folder+'/') for n in names) for folder in ['code','results'])
    assert 'submission/run_log.txt' in names
    checked=f'Actual archive inspection: {len(names)} entries; CRC checks passed; report content matches validated UTF-8 report.\n'+'\n'.join(names)+'\n'
(root/'results/final_archive_inspection.txt').write_text(checked,encoding='utf-8')
with log.open('a',encoding='utf-8') as f:
    f.write('Archive created and inspected successfully. Actual inspection output: results/final_archive_inspection.txt.\n')
    f.write('END code/06_finalize.py substantive work: succeeded. Final packaging below adds this completed record and its inspection output; final integrity verification follows.\n')
package()
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert z.read('submission/final_report.md').decode('utf-8')==report
    assert z.read('submission/run_log.txt')==log.read_bytes()
    assert 'submission/results/final_archive_inspection.txt' in z.namelist()
    print('FINAL ARCHIVE VERIFIED:',len(z.namelist()),'entries, report/code/results/run_log included, CRC valid')
    print('\n'.join(z.namelist()))
print('EXIT 0; no analyses repeated.')
