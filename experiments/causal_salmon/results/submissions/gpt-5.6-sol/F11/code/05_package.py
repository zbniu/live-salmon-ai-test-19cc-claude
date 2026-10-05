"""Read back final report, log validation, package, then inspect the archive."""
from pathlib import Path
import datetime
import hashlib
import json
import zipfile

root=Path(__file__).resolve().parents[1]
log=root/'run_log.txt'
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
with log.open('a',encoding='utf-8') as f:
    f.write(f'\nSTART {now()}: code/05_package.py (direct execution; no statistical analysis)\n')
report=(root/'final_report.md').read_text(encoding='utf-8')
assert report.strip() and '1.25' in report and '0.83 to 1.67' in report
assert 'average treatment effect on the treated' in report
print('READ BACK FINAL REPORT\n'+report)
checks={'report_utf8_bytes':len(report.encode('utf-8')),
        'report_sha256':hashlib.sha256(report.encode('utf-8')).hexdigest(),
        'report_nonempty':True,'intended_answer_present':True,
        'prior_executions':log.read_text(encoding='utf-8')}
(root/'results/report_validation.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
with log.open('a',encoding='utf-8') as f:
    f.write('Report was read back as UTF-8 and verified nonempty with intended ATT and confidence interval. Output: results/report_validation.json.\n')
    f.write('Packaging this directory into ../submission.zip with Python zipfile. Archive inspection output is retained alongside the archive as submission_archive_check.txt because a completed self-inspection cannot be embedded before packaging.\n')
    f.write(f'PRE-PACKAGE {now()}: all analyses and report generation complete; no analysis rerun.\n')
archive=root.parent/'submission.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file(): z.write(p,p.relative_to(root.parent))
with zipfile.ZipFile(archive) as z:
    names=z.namelist()
    assert z.testzip() is None
    assert z.read('submission/final_report.md').decode('utf-8')==report
    assert 'submission/run_log.txt' in names
    assert any(n.startswith('submission/code/') for n in names)
    assert any(n.startswith('submission/results/') for n in names)
    inspected='ARCHIVE VERIFIED '+now()+'\n'+str(archive)+'\n'+'\n'.join(names)+'\n'
(root.parent/'submission_archive_check.txt').write_text(inspected,encoding='utf-8')
print(inspected)
print('EXIT 0: report read-back and archive checks passed. Post-package verification record: submission_archive_check.txt')
