"""Execute a saved script once and retain its real stdout, stderr and exit status."""
import datetime
import pathlib
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[2]
script = pathlib.Path(sys.argv[1])
out = root / 'submission/results'
out.mkdir(parents=True, exist_ok=True)
log = root / 'submission/run_log.txt'
attempt = 1 + len(list(out.glob(f'{script.stem}*_stdout.txt')))
tag = script.stem if attempt == 1 else f'{script.stem}_attempt{attempt}'
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
with log.open('a', encoding='utf-8') as f:
    f.write(f'\nSTART {start}\nCommand: {sys.executable} {script}\n')
result = subprocess.run([sys.executable, str(script)], cwd=root, capture_output=True, text=True)
stdout = out / f'{tag}_stdout.txt'
stderr = out / f'{tag}_stderr.txt'
stdout.write_text(result.stdout, encoding='utf-8')
stderr.write_text(result.stderr, encoding='utf-8')
with log.open('a', encoding='utf-8') as f:
    f.write(f'END {datetime.datetime.now(datetime.timezone.utc).isoformat()} exit={result.returncode}\n')
    f.write(f'Actual stdout: {stdout.relative_to(root)}\nActual stderr: {stderr.relative_to(root)}\n')
print(result.stdout, end='')
print(result.stderr, file=sys.stderr, end='')
sys.exit(result.returncode)
