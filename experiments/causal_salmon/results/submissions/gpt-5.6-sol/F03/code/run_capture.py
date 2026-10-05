"""Capture actual command execution, stdout/stderr, exit status, and source hashes."""
from pathlib import Path
import datetime, hashlib, subprocess, sys

root = Path(__file__).resolve().parents[1]
label, *command = sys.argv[1:]
out = root / 'results' / (label + '_execution.txt')
out.parent.mkdir(parents=True, exist_ok=True)
log = root / 'run_log.txt'
with log.open('a', encoding='utf-8') as f:
    f.write(f'\nSTART {datetime.datetime.now(datetime.timezone.utc).isoformat()} {label}\n')
    f.write(f'Command: {command!r}\nCapture: results/{out.name}\n')
    for argument in command:
        p = Path(argument)
        if p.is_file():
            f.write(f'SHA256 {argument}: {hashlib.sha256(p.read_bytes()).hexdigest()}\n')
p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
out.write_text(p.stdout, encoding='utf-8')
with log.open('a', encoding='utf-8') as f:
    f.write(f'END {datetime.datetime.now(datetime.timezone.utc).isoformat()} exit={p.returncode}\n')
print(p.stdout, end='')
sys.exit(p.returncode)
