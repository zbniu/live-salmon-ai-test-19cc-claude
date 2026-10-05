"""Execute a saved script and retain real stdout, stderr, and ordered run records."""
from pathlib import Path
import datetime, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
log = ROOT / 'submission/run_log.txt'
if not log.exists():
    log.write_text('Execution record for this session.\n'
        'Before recorded analyses: study description read with cat; CSV header/first seven rows read with head; wc confirmed 2001 lines.\n'
        'Those initial inspection commands have tool-session records but no separately saved stdout files. No statistical analysis preceded the recorded steps below.\n'
        'Only the two attachments are empirical inputs. No internet access used.\n', encoding='utf-8')
script = Path(sys.argv[1])
name = script.stem
output = ROOT / 'submission/results' / (name + '_execution.txt')
if output.exists():
    raise RuntimeError(f'Refusing to overwrite an execution record: {output}')
with log.open('a', encoding='utf-8') as f:
    f.write(f'\nSTART {datetime.datetime.now(datetime.timezone.utc).isoformat()}\nCommand: {sys.executable} {script}\nCaptured stdout/stderr: {output.relative_to(ROOT)}\n')
result = subprocess.run([sys.executable, str(script)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
output.write_text(result.stdout, encoding='utf-8')
with log.open('a', encoding='utf-8') as f:
    f.write(f'END exit_code={result.returncode}\n')
print(result.stdout)
sys.exit(result.returncode)
