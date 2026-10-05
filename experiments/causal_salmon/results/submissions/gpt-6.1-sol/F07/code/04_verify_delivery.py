"""Read back the final report, create the ZIP, and inspect actual archive members.
This records its own execution so the completed log can be included in the ZIP.
"""
from pathlib import Path
import datetime, json, zipfile, hashlib

root = Path(__file__).resolve().parents[2]
s = root/'submission'
log = s/'run_log.txt'
def record(message):
    with log.open('a') as f:
        f.write(message+'\n')

record('\nSTART '+datetime.datetime.now(datetime.timezone.utc).isoformat()+' code/04_verify_delivery.py')
try:
    report = (s/'final_report.md').read_text(encoding='utf-8')
    assert report.strip(), 'Report is empty'
    assert '1.20 points' in report and '0.79 to 1.62 points' in report
    assert 'arrangement Q increased change' in report
    assert len(list((s/'code').glob('*.py'))) >= 4
    assert (s/'results/02_effect_summary.json').is_file()
    verification = {'report_utf8':True,'report_nonempty':True,'report_characters':len(report),
      'intended_answer_present':True,'expected_att_present':True,'expected_interval_present':True,
      'analysis_scripts_not_rerun':True}
    (s/'results/04_prearchive_checks.json').write_text(json.dumps(verification,indent=2)+'\n')
    record('Read back final_report.md as UTF-8; nonempty report and intended answer, estimate, and interval verified.')
    record('04_verify_delivery.py -> results/04_prearchive_checks.json, submission.zip (outside submission directory).')
    archive = root/'submission.zip'
    def pack():
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(s.rglob('*')):
                if p.is_file(): z.write(p,p.relative_to(root))
    pack()
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        assert z.testzip() is None
        assert 'submission/final_report.md' in names
        assert z.read('submission/final_report.md').decode('utf-8') == report
        assert 'submission/run_log.txt' in names
        assert any(n.startswith('submission/code/') for n in names)
        assert any(n.startswith('submission/results/') for n in names)
    record('Archive created and inspected: report matches read-back file; code, results, and execution record present; CRC checks passed.')
    record('EXIT 0; END '+datetime.datetime.now(datetime.timezone.utc).isoformat())
    # Refresh only the packaging so the completed verification record is archived.
    pack()
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert z.read('submission/run_log.txt') == log.read_bytes()
        assert z.read('submission/final_report.md').decode('utf-8') == report
        print('Verified archive members:')
        print('\n'.join(z.namelist()))
    print('FINAL REPORT READ-BACK:\n'+report)
    print('Report bytes:',(s/'final_report.md').stat().st_size)
    print('Archive bytes:',archive.stat().st_size)
    print('Archive sha256:',hashlib.sha256(archive.read_bytes()).hexdigest())
except Exception as e:
    record('ERROR '+repr(e))
    raise
