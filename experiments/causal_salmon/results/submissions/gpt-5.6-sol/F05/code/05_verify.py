"""Read back the report and verify numerical values and execution artifacts."""
import hashlib
import json
from pathlib import Path

report=Path('submission/final_report.md').read_text(encoding='utf-8')
assert report.strip()
for text in ['0.848 points','0.454 to 1.241 points','600 actual recipients','first inspection script failed']:
    assert text in report, text
for name in ['01_inspect','02_inspect','03_analyze','04_write_report']:
    assert Path(f'submission/results/{name}.stdout.txt').exists()
    assert Path(f'submission/results/{name}.stderr.txt').exists()
assert 'ModuleNotFoundError' in Path('submission/results/01_inspect.stderr.txt').read_text()
for name in ['02_inspect','03_analyze','04_write_report']:
    assert not Path(f'submission/results/{name}.stderr.txt').read_text()
for original,copied in [('upload/data(6).csv','submission/inputs/data.csv'),
                        ('upload/STUDY_DESCRIPTION(6).md','submission/inputs/STUDY_DESCRIPTION.md')]:
    assert Path(original).read_bytes()==Path(copied).read_bytes()
verification={'report_nonempty':True,'report_utf8_bytes':len(report.encode('utf-8')),
    'report_sha256':hashlib.sha256(report.encode('utf-8')).hexdigest(),
    'intended_answer_and_numbers_present':True,'input_copies_exact':True,
    'failure_record_preserved':True,'later_analysis_errors':False}
Path('submission/results/05_report_verification.json').write_text(json.dumps(verification,indent=2)+'\n')
print('FULL REPORT READ-BACK:')
print(report)
print('VERIFICATION:')
print(json.dumps(verification,indent=2))
