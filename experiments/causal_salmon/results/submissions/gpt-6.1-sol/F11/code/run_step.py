"""Execute a saved script, capture its real output, and append an execution log."""
from pathlib import Path
import datetime, subprocess, sys
root = Path(__file__).resolve().parents[2]
script = Path(sys.argv[1])
output = root/'submission/results'/f'{script.stem}_console.txt'
log = root/'submission/run_log.txt'
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
with log.open('a') as f:
 f.write(f'\nSTART {started}\nCommand: {sys.executable} {script}\nCaptured stdout/stderr: {output.relative_to(root)}\n')
with output.open('w') as f:
 result = subprocess.run([sys.executable,str(script)],cwd=root,stdout=f,stderr=subprocess.STDOUT)
with log.open('a') as f:
 f.write(f'END {datetime.datetime.now(datetime.timezone.utc).isoformat()} exit={result.returncode}\n')
 f.write('Files now present in results/: '+', '.join(sorted(p.name for p in (root/'submission/results').iterdir()))+'\n')
print(output.read_text())
sys.exit(result.returncode)
