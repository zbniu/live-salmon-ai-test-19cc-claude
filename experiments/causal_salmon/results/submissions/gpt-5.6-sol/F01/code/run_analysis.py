"""Execute analysis once, preserving actual stdout, stderr and exit status."""
from datetime import datetime, timezone
from pathlib import Path
import os
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
log = root / 'run_log.txt'
def record(text):
    with log.open('a', encoding='utf-8') as handle:
        handle.write(datetime.now(timezone.utc).isoformat() + ' ' + text + '\n')

record('Analysis launcher started: code/run_analysis.py. Earlier preparation: read the supplied study description and first five data rows, listed attachments, copied the two complete inputs into submission/inputs, and wrote code with apply_patch. Those previews were tool outputs, not saved statistical results. No earlier analysis runs or analysis failures.')
command = [sys.executable, str(root / 'code' / 'analyze.py')]
record('START ' + repr(command))
result = subprocess.run(command, cwd=root.parent, text=True, capture_output=True)
(root / 'results' / 'analysis_stdout.txt').write_text(result.stdout, encoding='utf-8')
(root / 'results' / 'analysis_stderr.txt').write_text(result.stderr, encoding='utf-8')
record('FINISH exit=' + str(result.returncode) + '; actual stdout -> results/analysis_stdout.txt; actual stderr -> results/analysis_stderr.txt')
for name in ['analysis.json', 'group_summary.csv', 'descriptive_regressions.csv', 'score_bands.csv']:
    path = root / 'results' / name
    record('OUTPUT ' + name + ': ' + (str(path.stat().st_size) + ' bytes' if path.exists() else 'MISSING'))
print(result.stdout, end='')
if result.stderr:
    print(result.stderr, file=sys.stderr, end='')
sys.exit(result.returncode)
