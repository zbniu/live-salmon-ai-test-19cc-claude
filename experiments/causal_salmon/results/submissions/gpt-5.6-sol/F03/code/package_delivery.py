"""Build and inspect the requested delivery, preserving previous execution records."""
from pathlib import Path
import datetime, hashlib, json, shutil, zipfile

root=Path(__file__).resolve().parents[1]
archive=root.parent/'submission.zip'
log=root/'run_log.txt'
with log.open('a',encoding='utf-8') as f:
    f.write(f'\nSTART {datetime.datetime.now(datetime.timezone.utc).isoformat()} 05_package_delivery\n')
    f.write('Command: Python submission/code/package_delivery.py\n')
    f.write('Outputs: submission/inputs/, submission/results/delivery_verification.json, submission.zip\n')
text=(root/'final_report.md').read_text(encoding='utf-8')
assert text.strip() and '1.110223 points' in text and '0.705 to 1.516 points' in text
assert 'Answer to the research question' in text
(root/'inputs').mkdir(exist_ok=True)
for name in ['data(4).csv','STUDY_DESCRIPTION(4).md']:
    shutil.copyfile(root.parent/'upload'/name,root/'inputs'/name)
(root/'code'/'README.md').write_text('''Reproduction

The analysis used only the two supplied files. Copies are in submission/inputs/.
The executed scripts expect an upload/ directory next to submission/, containing
data(4).csv and STUDY_DESCRIPTION(4).md with their original names. To reproduce,
copy the supplied input copies there. Run from the directory containing submission/:

python submission/code/run_capture.py explore_reproduction python submission/code/explore.py
python submission/code/run_capture.py final_reproduction python submission/code/final_analysis.py
python submission/code/run_capture.py report_reproduction python submission/code/write_report.py

Requirements: Python, NumPy, pandas, SciPy. Versions are recorded in results/initial_results.json.
explore_v1_missing_dependency.py preserves the original failed source; do not use it
for reproduction. The original traceback remains in results/01_explore_execution.txt.
''',encoding='utf-8')

def build():
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(root.parent))

def inspect():
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        names=z.namelist()
        assert z.read('submission/final_report.md').decode('utf-8')==text
        assert 'submission/run_log.txt' in names
        assert any(n.startswith('submission/code/') and n.endswith('.py') for n in names)
        assert 'submission/results/01_explore_execution.txt' in names
        assert 'submission/results/final_results.json' in names
        assert all(n.startswith('submission/') for n in names)
    return names

build()
names=inspect()
verification={'report_nonempty':True,'report_utf8_readback_matches_intended_report':True,
              'report_sha256':hashlib.sha256(text.encode('utf-8')).hexdigest(),
              'first_archive_crc_check':'passed','first_archive_required_contents':'passed',
              'first_archive_entries':names,
              'notes':'Archive rebuilt below to include this actual verification record and completed packaging log; final inspection printed to session.'}
(root/'results'/'delivery_verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
with log.open('a',encoding='utf-8') as f:
    f.write('Report read back: nonempty UTF-8, intended answer and adopted numbers confirmed.\n')
    f.write('Initial archive inspection: CRC check passed; report, code, results, execution log all present.\n')
    f.write('Final archive rebuild includes completed log and actual delivery_verification.json. Final inspection follows in session output.\n')
    f.write(f'END {datetime.datetime.now(datetime.timezone.utc).isoformat()} 05_package_delivery exit=0 (pre-final archive inspection)\n')
build()
names=inspect()
with zipfile.ZipFile(archive) as z:
    assert z.read('submission/run_log.txt')==log.read_bytes()
    assert 'submission/results/delivery_verification.json' in z.namelist()
print('READ-BACK FINAL REPORT\n'+text)
print('FINAL ARCHIVE INSPECTION: passed; entries:')
print('\n'.join(names))
print('Archive bytes:',archive.stat().st_size)
