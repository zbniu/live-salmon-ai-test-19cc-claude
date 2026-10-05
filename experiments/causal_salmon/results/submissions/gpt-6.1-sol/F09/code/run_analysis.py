"""Run analyze.py once and preserve real stdout, stderr, and execution order."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
submission = root / 'submission'
log = submission / 'run_log.txt'
stamp = lambda: datetime.now(timezone.utc).isoformat()
with log.open('a', encoding='utf-8') as f:
    f.write('Pre-analysis: source description read with cat; CSV header and first seven rows inspected with head; wc reported 2001 lines. These inspection commands succeeded. No earlier statistical analyses were executed. Their terminal output is summarized here, not reconstructed as a captured execution transcript.\n')
    cmd = [sys.executable, str(submission / 'code' / 'analyze.py'),
           str(root / 'upload' / 'data(20261004-180759).csv'), str(submission / 'results')]
    f.write(f'{stamp()} BEGIN analysis execution 1: {json.dumps(cmd)}\n')
    f.flush()
    result = subprocess.run(cmd, capture_output=True, text=True)
    (submission / 'results' / 'analysis_stdout.txt').write_text(result.stdout, encoding='utf-8')
    (submission / 'results' / 'analysis_stderr.txt').write_text(result.stderr, encoding='utf-8')
    f.write(f'{stamp()} END analysis execution 1: exit_code={result.returncode}\n')
    f.write('Captured outputs: results/analysis_stdout.txt, results/analysis_stderr.txt. Analysis writes: results/group_summary.csv, results/baseline_bins.csv, results/descriptive_regressions.csv, results/hypothetical_counterfactual_examples.csv, results/analysis_summary.json.\n')
    f.write('Errors: ' + ('none; stderr empty.\n' if not result.stderr and result.returncode == 0 else 'see captured stderr and exit code.\n'))
print(result.stdout, end='')
if result.stderr:
    print(result.stderr, file=sys.stderr, end='')
sys.exit(result.returncode)
