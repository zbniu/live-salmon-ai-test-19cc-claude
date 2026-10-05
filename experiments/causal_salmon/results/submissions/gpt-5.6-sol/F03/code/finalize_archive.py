"""Record the observed post-packaging save failure and finalize local delivery."""
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parents[1]
log=root/'run_log.txt'
with log.open('a',encoding='utf-8') as f:
    f.write('\nPost-packaging persistent-save attempt: the Library upload helper was executed for final_report.md and submission.zip. It exited 1 before upload because it could not read Codex authentication. The actual error was displayed in the session; it was not captured to a separate output file. No statistical analysis was run or changed. Local downloadable files remain present.\n')
    f.write('06_finalize_archive: executed submission/code/finalize_archive.py to include this failure record and finalize_archive.py in the archive, then read back the report and inspect the final archive. No analyses repeated. Final verification output is displayed in session, not separately captured.\n')
report=(root/'final_report.md').read_text(encoding='utf-8')
assert report.strip() and '1.110223 points' in report and '0.705 to 1.516 points' in report
archive=root.parent/'submission.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file(): z.write(p,p.relative_to(root.parent))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert z.read('submission/final_report.md').decode('utf-8')==report
    assert z.read('submission/run_log.txt')==log.read_bytes()
    names=z.namelist()
    assert all(any(n.startswith(prefix) for n in names) for prefix in
               ['submission/code/','submission/results/','submission/run_log.txt'])
    print('Final report read back successfully:',len(report.encode('utf-8')),'UTF-8 bytes.')
    print('Final archive CRC and required-content verification passed.')
    print('\n'.join(names))
