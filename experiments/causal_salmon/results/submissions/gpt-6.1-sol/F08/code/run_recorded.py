"""Execute one script once and retain its actual stdout, stderr, and exit status."""
from pathlib import Path
from datetime import datetime, timezone
import subprocess, sys
root=Path(__file__).resolve().parents[2]
script=Path(sys.argv[1])
stem=script.stem
out=root/'submission'/'results'/f'{stem}_stdout.txt'
err=root/'submission'/'results'/f'{stem}_stderr.txt'
log=root/'submission'/'run_log.txt'
start=datetime.now(timezone.utc).isoformat()
with log.open('a') as f:
 f.write(f'\nSTART {start}\nCommand: {sys.executable} {script}\n')
 f.write(f'Actual stdout -> {out.relative_to(root)}\nActual stderr -> {err.relative_to(root)}\n')
with out.open('w') as stdout, err.open('w') as stderr:
 result=subprocess.run([sys.executable,str(script)],cwd=root,stdout=stdout,stderr=stderr)
with log.open('a') as f:
 f.write(f'END {datetime.now(timezone.utc).isoformat()} exit_status={result.returncode}\n')
print(out.read_text())
if err.stat().st_size: print(err.read_text(),file=sys.stderr)
sys.exit(result.returncode)
