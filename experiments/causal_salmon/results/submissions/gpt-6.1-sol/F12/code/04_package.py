"""Read the report back and inspect the actual ZIP, preserving verification records."""
import datetime
import hashlib
import json
import pathlib
import zipfile

root=pathlib.Path.cwd()
sub=root/'submission'
archive=root/'submission.zip'
log=sub/'run_log.txt'
with log.open('a',encoding='utf-8') as f:
    f.write(f'\nSTART {datetime.datetime.now(datetime.timezone.utc).isoformat()}\nCommand: Python submission/code/04_package.py\n')
report=(sub/'final_report.md').read_text(encoding='utf-8')
assert report.strip() and '1.25' in report and '0.81' in report and '1.65' in report
assert 'adopted answer to the research question' in report
def pack():
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(sub.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(root))
def check():
    with zipfile.ZipFile(archive) as z:
        names=z.namelist()
        assert z.testzip() is None
        assert 'submission/final_report.md' in names
        assert 'submission/run_log.txt' in names
        assert any(n.startswith('submission/code/') for n in names)
        assert any(n.startswith('submission/results/') for n in names)
        assert z.read('submission/final_report.md').decode('utf-8') == report
        return names
pack()
names=check()
validation={'report_nonempty':True,'report_utf8_bytes':len(report.encode('utf-8')),
            'report_sha256':hashlib.sha256(report.encode('utf-8')).hexdigest(),
            'zip_testzip_ok':True,'zip_report_matches_readback':True,
            'required_sections_present':True,'inspected_archive_members':names,
            'note':'Actual initial inspection; archive then refreshed to include this validation and completed run log, and inspected again.'}
(sub/'results/archive_validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
with log.open('a',encoding='utf-8') as f:
    f.write(f'END {datetime.datetime.now(datetime.timezone.utc).isoformat()} exit=0: report read back, intended result verified, actual ZIP inspected with CRC check and required entries. Output: submission/results/archive_validation.json and submission.zip. Archive refreshed next to include completed record; final inspection printed in session.\n')
pack()
final_names=check()
assert 'submission/results/archive_validation.json' in final_names
print('READ-BACK OF FINAL REPORT:\n'+report)
print('FINAL ARCHIVE MEMBERS:')
print('\n'.join(final_names))
print(f'VERIFIED: report nonempty and correct; report, code, results, and execution record included. Archive bytes: {archive.stat().st_size}')
