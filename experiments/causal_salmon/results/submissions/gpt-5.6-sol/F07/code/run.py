"""Run one script and preserve the actual stdout, stderr, exit status, and order."""
from pathlib import Path
from datetime import datetime, timezone
import subprocess, sys

root = Path(__file__).resolve().parents[1]
script, output = sys.argv[1:3]
log = root/'run_log.txt'
start = datetime.now(timezone.utc).isoformat()
with log.open('a', encoding='utf-8') as f:
    f.write(f'\nSTART {start}\nCommand: {sys.executable} {script}\nCaptured stdout and stderr: {output}\n')
p = subprocess.run([sys.executable, str(root/script)], cwd=root.parent, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
(root/output).write_text(p.stdout, encoding='utf-8')
print(p.stdout, end='')
with log.open('a', encoding='utf-8') as f:
    f.write(f'END {datetime.now(timezone.utc).isoformat()} exit_status={p.returncode}\n')
sys.exit(p.returncode)
