"""Package actual files and inspect the report and complete archive."""
from pathlib import Path
import datetime
import hashlib
import json
import zipfile

root = Path(__file__).resolve().parents[1]
archive = root.parent/'submission.zip'
log = root/'run_log.txt'
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
with log.open('a', encoding='utf-8') as f:
    f.write(f'\n{now()} START packaging: code/04_package.py\n')
report = (root/'final_report.md').read_text(encoding='utf-8')
assert report.strip()
assert 'increased change' in report and '1.11 points' in report
assert '0.70 to 1.52 points' in report
assert list((root/'code').glob('*.py'))
assert list((root/'results').glob('*'))

def build_archive():
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob('*')):
            if p.is_file():
                z.write(p, str(p.relative_to(root.parent)))

def inspect_archive():
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        names = z.namelist()
        assert len(names) == len(set(names))
        assert 'submission/final_report.md' in names
        assert 'submission/run_log.txt' in names
        assert any(n.startswith('submission/code/') for n in names)
        assert any(n.startswith('submission/results/') for n in names)
        assert z.read('submission/final_report.md').decode('utf-8') == report
        for p in root.rglob('*'):
            if p.is_file():
                assert z.read(str(p.relative_to(root.parent))) == p.read_bytes()
        return names

build_archive()
members = inspect_archive()
verification = {
 'initial_archive_integrity': 'passed',
 'report_readback_nonempty_and_intended_answer': True,
 'report_bytes': len(report.encode('utf-8')),
 'report_sha256': hashlib.sha256(report.encode('utf-8')).hexdigest(),
 'report_code_results_log_present': True,
 'initial_archive_members': members,
 'note': 'A final rebuild follows to include this verification and completed packaging log. Its integrity and byte equality are checked in this execution; final console confirmation remains in the session tool output.'
}
(root/'results'/'delivery_verification.json').write_text(json.dumps(verification, indent=2)+'\n')
with log.open('a', encoding='utf-8') as f:
    f.write(f'{now()} Initial ZIP creation and inspection passed; all files matched.\n')
    f.write('Output: results/delivery_verification.json. Report read back and confirmed nonempty with intended answer.\n')
    f.write('Final archive will now be rebuilt to include this completed record and verification.\n')
    f.write('The final archive verification console output is retained only in the session tool record, not in a separate stdout file.\n')
build_archive()
members = inspect_archive()
print('FINAL REPORT READBACK:\n'+report)
print('FINAL ARCHIVE VERIFIED; entries:')
for name in members:
    print(name)
print(f'Archive size: {archive.stat().st_size} bytes')
print('ZIP integrity, required content, and byte-for-byte agreement with local files: PASSED')
