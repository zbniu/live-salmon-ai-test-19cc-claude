"""Run an analysis step and preserve its genuine console output and exit status."""
import datetime
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
step = Path(sys.argv[1])
label = sys.argv[2]
out = ROOT / 'submission' / 'results' / f'{label}_console.txt'
log = ROOT / 'submission' / 'run_log.txt'
out.parent.mkdir(parents=True, exist_ok=True)
with log.open('a', encoding='utf-8') as f:
    f.write(f'\n{datetime.datetime.now(datetime.timezone.utc).isoformat()} START {label}\n')
    f.write(f'Command: {sys.executable} {step}\nConsole: {out.relative_to(ROOT)}\n')
with out.open('w', encoding='utf-8') as f:
    result = subprocess.run([sys.executable, str(step)], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
with log.open('a', encoding='utf-8') as f:
    f.write(f'{datetime.datetime.now(datetime.timezone.utc).isoformat()} END {label}; exit={result.returncode}\n')
print(out.read_text(encoding='utf-8'))
sys.exit(result.returncode)
