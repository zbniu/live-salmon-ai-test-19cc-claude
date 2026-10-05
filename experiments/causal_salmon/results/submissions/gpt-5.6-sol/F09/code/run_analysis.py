"""Capture the actual analysis execution, including any error and return code."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
log = root / 'submission/run_log.txt'
out = root / 'submission/results'
out.mkdir(parents=True, exist_ok=True)
with log.open('a', encoding='utf-8') as f:
    f.write(f'\n{datetime.now(timezone.utc).isoformat()} START analysis\n')
    cmd = [sys.executable, str(root / 'submission/code/analyze.py')]
    f.write(f'Command: {cmd!r}; cwd={root}\n')
    f.flush()
    process = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    (out / 'analysis_stdout.txt').write_text(process.stdout, encoding='utf-8')
    (out / 'analysis_stderr.txt').write_text(process.stderr, encoding='utf-8')
    f.write(f'END analysis exit_code={process.returncode}; stdout=results/analysis_stdout.txt; stderr=results/analysis_stderr.txt\n')
    f.write('Outputs currently present: ' + ', '.join(p.name for p in sorted(out.iterdir())) + '\n')
print(process.stdout)
print(process.stderr, file=sys.stderr)
sys.exit(process.returncode)
