"""Execute a saved script once, preserving stdout, stderr and chronology."""
import datetime
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
script = root / 'code' / sys.argv[1]
output = root / 'results' / (script.stem + '_console.txt')
log = root / 'run_log.txt'
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
with log.open('a', encoding='utf-8') as f:
    f.write(f'\nSTART {start}: {sys.executable} {script.relative_to(root)}\n')
with output.open('w', encoding='utf-8') as f:
    p = subprocess.run([sys.executable, str(script)], cwd=root.parent,
                       stdout=f, stderr=subprocess.STDOUT, env=os.environ.copy())
with log.open('a', encoding='utf-8') as f:
    f.write(f'END exit={p.returncode}; combined stdout/stderr: {output.relative_to(root)}\n')
print(output.read_text(encoding='utf-8'))
sys.exit(p.returncode)
