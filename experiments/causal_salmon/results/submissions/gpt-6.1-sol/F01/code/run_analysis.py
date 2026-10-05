"""Execute analysis once, preserving real stdout, stderr, and ordered run records."""
from pathlib import Path
from datetime import datetime, timezone
import subprocess
import sys

base = Path(__file__).resolve().parents[1]
log = base / 'run_log.txt'
results = base / 'results'
results.mkdir(parents=True, exist_ok=True)
now = lambda: datetime.now(timezone.utc).isoformat()
attempt = 1
while (results / f'analysis_stdout_attempt{attempt}.txt').exists() or (attempt == 1 and (results / 'analysis_stdout.txt').exists()):
    attempt += 1
with log.open('a', encoding='utf-8') as f:
    if attempt == 1:
        f.write(f'{now()} Preparation: read the supplied study description and CSV header using shell tools.\n')
        f.write('Those initial inspection tool outputs were not saved to files; no numerical analysis was performed in them.\n')
    else:
        f.write('Recovery: attempt 1 stopped at import because statsmodels was unavailable. Original source retained as code/analyze_attempt1.py.\n')
        f.write('Replaced that unavailable dependency with NumPy least squares and an explicit HC3 sandwich covariance; no package installation.\n')
    f.write(f'{now()} START {attempt}: {sys.executable} submission/code/analyze.py\n')
proc = subprocess.run([sys.executable, str(base / 'code' / 'analyze.py')],
                      cwd=base.parent, text=True, capture_output=True)
(results / f'analysis_stdout_attempt{attempt}.txt').write_text(proc.stdout, encoding='utf-8')
(results / f'analysis_stderr_attempt{attempt}.txt').write_text(proc.stderr, encoding='utf-8')
with log.open('a', encoding='utf-8') as f:
    f.write(f'{now()} END {attempt}: exit code {proc.returncode}.\n')
    f.write(f'Captured output: results/analysis_stdout_attempt{attempt}.txt and results/analysis_stderr_attempt{attempt}.txt.\n')
    f.write('Files actually present after execution: ' + ', '.join(p.name for p in sorted(results.iterdir())) + '\n')
    if proc.returncode:
        f.write('ERROR: analysis failed; preserve this attempt and its captured streams.\n')
    else:
        f.write('No execution error in this attempt. Earlier failed execution records retained; this run corrects the missing dependency.\n')
print(proc.stdout)
if proc.stderr:
    print('STDERR:\n' + proc.stderr, file=sys.stderr)
raise SystemExit(proc.returncode)
