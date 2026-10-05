"""Execute a saved script, preserving stdout/stderr and an append-only run log."""
from pathlib import Path
import subprocess, sys, datetime
root = Path(__file__).resolve().parents[2]
script = Path(sys.argv[1])
label = script.stem
log = root/'submission/run_log.txt'
with log.open('a') as f:
    f.write(f'\nSTART {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n')
    f.write(f'COMMAND {sys.executable} {script}\n')
result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
stdout = root/f'submission/results/{label}.stdout.txt'
stderr = root/f'submission/results/{label}.stderr.txt'
stdout.write_text(result.stdout)
stderr.write_text(result.stderr)
with log.open('a') as f:
    f.write(f'EXIT {result.returncode}; STDOUT {stdout.relative_to(root)}; STDERR {stderr.relative_to(root)}\n')
    f.write(f'END {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n')
print(result.stdout)
if result.stderr: print(result.stderr, file=sys.stderr)
sys.exit(result.returncode)
