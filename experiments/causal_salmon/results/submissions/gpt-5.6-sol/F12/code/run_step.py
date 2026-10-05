"""Run a saved analysis script and retain its actual stdout, stderr and status."""
from pathlib import Path
import sys, subprocess, datetime, shlex

root = Path(__file__).resolve().parents[1]
script = root / 'code' / sys.argv[1]
label = sys.argv[2]
out = root / 'results'
out.mkdir(parents=True, exist_ok=True)
command = [sys.executable, str(script)] + sys.argv[3:]
with (root / 'run_log.txt').open('a', encoding='utf-8') as log:
    log.write(f'\nSTART {datetime.datetime.now(datetime.timezone.utc).isoformat()}\nCommand: {shlex.join(command)}\n')
    log.flush()
    p = subprocess.run(command, capture_output=True, text=True)
    (out / f'{label}_stdout.txt').write_text(p.stdout, encoding='utf-8')
    (out / f'{label}_stderr.txt').write_text(p.stderr, encoding='utf-8')
    log.write(f'END {datetime.datetime.now(datetime.timezone.utc).isoformat()} exit={p.returncode}\nstdout: results/{label}_stdout.txt\nstderr: results/{label}_stderr.txt\n')
print(p.stdout, end='')
print(p.stderr, end='', file=sys.stderr)
sys.exit(p.returncode)
