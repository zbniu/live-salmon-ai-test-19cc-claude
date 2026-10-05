"""Execute a script once, retaining actual stdout/stderr and an ordered log."""
import datetime
import hashlib
import pathlib
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[2]
script = root / sys.argv[1]
stem = sys.argv[2]
results = root / 'submission/results'
results.mkdir(parents=True, exist_ok=True)
log = root / 'submission/run_log.txt'
with log.open('a', encoding='utf-8') as f:
    f.write(f'\nSTART {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n')
    f.write(f'Command: {sys.executable} {script.relative_to(root)}\n')
    f.write(f'Code SHA256: {hashlib.sha256(script.read_bytes()).hexdigest()}\n')
proc = subprocess.run([sys.executable, str(script)], cwd=root, text=True, capture_output=True)
(results / f'{stem}.stdout.txt').write_text(proc.stdout, encoding='utf-8')
(results / f'{stem}.stderr.txt').write_text(proc.stderr, encoding='utf-8')
with log.open('a', encoding='utf-8') as f:
    f.write(f'END {datetime.datetime.now(datetime.timezone.utc).isoformat()} exit_code={proc.returncode}\n')
    f.write(f'Actual captured streams: submission/results/{stem}.stdout.txt and {stem}.stderr.txt\n')
print(proc.stdout, end='')
print(proc.stderr, end='', file=sys.stderr)
sys.exit(proc.returncode)
