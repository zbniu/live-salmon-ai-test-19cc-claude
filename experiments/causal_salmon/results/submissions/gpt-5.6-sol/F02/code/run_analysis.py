"""Capture the actual analysis execution, including errors and exit status."""
import datetime
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
(root / 'results').mkdir(parents=True, exist_ok=True)
stdout_path = root / 'results/analysis_stdout.txt'
stderr_path = root / 'results/analysis_stderr.txt'
command = [sys.executable, str(root / 'code/analyze.py')]
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
with (root / 'run_log.txt').open('a', encoding='utf-8') as log:
    log.write(f'4. Started {started}\n   Command: {command!r}\n')
with stdout_path.open('w', encoding='utf-8') as out, stderr_path.open('w', encoding='utf-8') as err:
    result = subprocess.run(command, stdout=out, stderr=err, text=True)
with (root / 'run_log.txt').open('a', encoding='utf-8') as log:
    log.write(f'   Finished {datetime.datetime.now(datetime.timezone.utc).isoformat()}. Exit code {result.returncode}.\n')
    log.write('   Actual captured stdout: results/analysis_stdout.txt\n')
    log.write('   Actual captured stderr: results/analysis_stderr.txt\n')
    log.write('   On success the analysis also writes results/analysis.json,\n')
    log.write('   results/group_summary.csv, and results/baseline_bins.csv.\n')
print(stdout_path.read_text(encoding='utf-8'))
if stderr_path.stat().st_size:
    print(stderr_path.read_text(encoding='utf-8'), file=sys.stderr)
sys.exit(result.returncode)
