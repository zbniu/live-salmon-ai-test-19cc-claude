"""Read back the report, package files, and inspect actual archive contents.

The first archive's actual verification is recorded and included in the final
archive. The final rebuild only incorporates those records; no analysis reruns.
"""
from pathlib import Path
import datetime, json, zipfile

ROOT=Path(__file__).resolve().parents[2]
SUB=ROOT/'submission'
OUT=SUB/'results'
LOG=SUB/'run_log.txt'
ARCHIVE=ROOT/'submission.zip'

def log(message):
    with LOG.open('a',encoding='utf-8') as f:
        f.write(message+'\n')

def build():
    with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(SUB.rglob('*')):
            if path.is_file():
                archive.write(path,path.relative_to(ROOT).as_posix())

def inspect():
    with zipfile.ZipFile(ARCHIVE,'r') as archive:
        names=archive.namelist()
        assert archive.testzip() is None
        assert 'submission/final_report.md' in names
        assert 'submission/run_log.txt' in names
        assert any(n.startswith('submission/code/') and n.endswith('.py') for n in names)
        assert any(n.startswith('submission/results/') for n in names)
        assert archive.read('submission/final_report.md').decode('utf-8') == report
        for n in names:
            assert archive.read(n) == (ROOT/n).read_bytes(),n
        return [{'name':i.filename,'bytes':i.file_size} for i in archive.infolist()]

log(f'\nSTART {datetime.datetime.now(datetime.timezone.utc).isoformat()}\nCommand: python submission/code/05_package.py')
report=(SUB/'final_report.md').read_text(encoding='utf-8')
assert report.strip()
assert '1.110 points' in report and '0.705 to 1.516 points' in report
assert 'average change' in report and '600 recipients' in report
(OUT/'report_readback.txt').write_text('Actual UTF-8 report readback; nonempty and intended numerical conclusion verified.\n\n'+report,encoding='utf-8')
print('REPORT READBACK:\n'+report)
log('Read back submission/final_report.md; saved actual readback in submission/results/report_readback.txt. Nonempty, intended answer and adopted result checked.')
build()
first=inspect()
(OUT/'archive_verification.json').write_text(json.dumps({'stage':'Actual first archive inspection before adding this verification record',
    'crc_check':'passed','report_matches_readback':True,'required_categories_present':True,'members':first},indent=2),encoding='utf-8')
log('First submission.zip built and actually inspected: CRC passed, report/code/results/log present, every archived file matched local bytes. Actual member list saved in submission/results/archive_verification.json.')
log('Final archive rebuilt to include this execution record and first-archive verification. Final inspection is printed in the tool-session output; it is not represented as a separate archived execution file.')
build()
final=inspect()
print('\nFINAL ARCHIVE INSPECTION: CRC and every file byte comparison passed.')
for item in final:
    print(f"{item['name']} ({item['bytes']} bytes)")
print(f'Archive size: {ARCHIVE.stat().st_size} bytes')
