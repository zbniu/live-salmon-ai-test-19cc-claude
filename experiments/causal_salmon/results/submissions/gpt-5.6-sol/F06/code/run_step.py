"""Execute one script, preserving stdout, stderr and exit status in order."""
import datetime
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
step, script, *arguments = sys.argv[1:]
out = root / 'results'
out.mkdir(parents=True, exist_ok=True)
command = [sys.executable, str(root / 'code' / script), *arguments]
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
with (root / 'run_log.txt').open('a', encoding='utf-8') as log:
    log.write(f'\n{step} START {start}\nCommand: {json.dumps(command)}\n')
proc = subprocess.run(command, capture_output=True, text=True)
stdout_path, stderr_path = out / f'{step}_stdout.txt', out / f'{step}_stderr.txt'
stdout_path.write_text(proc.stdout, encoding='utf-8')
stderr_path.write_text(proc.stderr, encoding='utf-8')
end = datetime.datetime.now(datetime.timezone.utc).isoformat()
with (root / 'run_log.txt').open('a', encoding='utf-8') as log:
    log.write(f'{step} END {end}; exit={proc.returncode}\n')
    log.write(f'Captured output: results/{stdout_path.name}; results/{stderr_path.name}\n')
    log.write('Files present after execution: '+', '.join(sorted(p.name for p in out.iterdir()))+'\n')
print(proc.stdout)
if proc.stderr:
    print(proc.stderr, file=sys.stderr)
sys.exit(proc.returncode)
