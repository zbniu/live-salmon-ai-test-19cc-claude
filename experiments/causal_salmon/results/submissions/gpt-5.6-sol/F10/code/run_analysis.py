"""Run once, retaining stdout, stderr, exit status, and execution order."""
from pathlib import Path
import datetime
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
log = root / 'run_log.txt'
def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
with log.open('a', encoding='utf-8') as f:
    f.write(f'{now()} Step 1: {sys.executable} code/analyze.py\n')
    f.flush()
    p = subprocess.run([sys.executable, str(root/'code/analyze.py')], cwd=root,
                       capture_output=True, text=True)
    (root/'results/analysis_stdout.txt').write_text(p.stdout, encoding='utf-8')
    (root/'results/analysis_stderr.txt').write_text(p.stderr, encoding='utf-8')
    f.write(f'{now()} Step 1 completed, exit={p.returncode}. stdout=results/analysis_stdout.txt; stderr=results/analysis_stderr.txt.\n')
    f.write('On success, analyze.py writes results/group_summary.csv, results/associational_regressions.csv, results/score_bins.csv, results/analysis.json.\n')
print(p.stdout)
if p.stderr:
    print(p.stderr, file=sys.stderr)
sys.exit(p.returncode)
