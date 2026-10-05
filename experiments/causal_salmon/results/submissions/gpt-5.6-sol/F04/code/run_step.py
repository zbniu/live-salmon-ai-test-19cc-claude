"""Execute a saved Python script, preserving stdout/stderr and an append-only log."""
from pathlib import Path
import datetime
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
script = Path(sys.argv[1]).resolve()
label = sys.argv[2]
log = root / 'run_log.txt'
outputs = root / 'results'
outputs.mkdir(parents=True, exist_ok=True)
stamp = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
with log.open('a', encoding='utf-8') as f:
    f.write(f'\n{stamp()} START {label}\nCommand: {sys.executable} {script}\n')
result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
stdout = outputs / f'{label}_stdout.txt'
stderr = outputs / f'{label}_stderr.txt'
stdout.write_text(result.stdout, encoding='utf-8')
stderr.write_text(result.stderr, encoding='utf-8')
with log.open('a', encoding='utf-8') as f:
    f.write(f'{stamp()} END {label}; exit code {result.returncode}\n')
    f.write(f'Stdout: results/{stdout.name}; stderr: results/{stderr.name}\n')
    f.write('Files present after execution: ' + ', '.join(p.name for p in sorted(outputs.iterdir())) + '\n')
print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)
sys.exit(result.returncode)
