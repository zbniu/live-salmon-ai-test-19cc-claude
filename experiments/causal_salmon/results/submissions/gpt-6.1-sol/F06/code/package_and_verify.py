"""Package the already-produced report/results; do not rerun analyses."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import zipfile

root = Path(__file__).resolve().parents[2]
sub = root / 'submission'
log = sub / 'run_log.txt'
def record(message):
    with log.open('a', encoding='utf-8') as f:
        f.write(f'[{datetime.now(timezone.utc).isoformat()}] {message}\n')

record('EXECUTE code/package_and_verify.py: copy provided inputs; read back final report; verify recorded results; create and inspect submission.zip. No analyses rerun.')
inputs = sub / 'inputs'
inputs.mkdir(exist_ok=True)
results = json.loads((sub/'results/analysis.json').read_text(encoding='utf-8'))
for name, digest in results['input_sha256'].items():
    src = root / 'upload' / name
    assert hashlib.sha256(src.read_bytes()).hexdigest() == digest
    shutil.copyfile(src, inputs/name)

report_path = sub / 'final_report.md'
report = report_path.read_text(encoding='utf-8')
assert len(report.strip()) > 100
assert '0.8477' in report and '0.4275' in report and '1.2680' in report
assert '1.0139' in report and 'exact average causal effect' in report
primary = results['primary']
assert f"{primary['estimate']:.4f}" in report
assert f"{primary['ci95_low']:.4f}" in report
assert f"{primary['ci95_high']:.4f}" in report
print('READ-BACK OF FINAL REPORT\n')
print(report)
record('Final report read back as UTF-8: nonempty; intended conclusion and numerical results verified against results/analysis.json. Inputs verified against recorded SHA-256 hashes and copied to inputs/.')

archive = root / 'submission.zip'
files = sorted(p for p in sub.rglob('*') if p.is_file())
names = [str(p.relative_to(root)) for p in files]
required = ['submission/final_report.md', 'submission/run_log.txt',
    'submission/code/analyze.py', 'submission/code/analyze_attempt1.py',
    'submission/code/package_and_verify.py', 'submission/results/analysis.json',
    'submission/results/analysis_console.txt', 'submission/results/analysis_attempt1_console.txt']
assert all(name in names for name in required)
assert any(n.startswith('submission/inputs/') for n in names)
record(f'Packaging {len(files)} files; required report/code/results/run_log present. Code and numerical-output files include the failed attempt and successful attempt. No missing statistical execution records; preliminary inspection had no separately saved console file as noted above.')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in files:
        z.write(path, path.relative_to(root))
with zipfile.ZipFile(archive) as z:
    actual = z.namelist()
    assert actual == names
    assert z.testzip() is None
    assert z.read('submission/final_report.md').decode('utf-8') == report
    assert all(name in actual for name in required)
print('\nARCHIVE INSPECTION: PASS')
print('\n'.join(actual))
print(f'Archive size: {archive.stat().st_size} bytes')
