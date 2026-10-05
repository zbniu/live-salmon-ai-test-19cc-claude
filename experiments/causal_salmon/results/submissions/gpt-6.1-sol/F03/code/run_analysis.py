"""Execute analysis once, retaining stdout, stderr, timestamps, and status."""
from pathlib import Path
from datetime import datetime, timezone
import subprocess, sys
root=Path(__file__).resolve().parents[2]
log=root/'submission/run_log.txt'
now=lambda:datetime.now(timezone.utc).isoformat()
with log.open('a',encoding='utf-8') as f:
    f.write(f'\n{now()} BEGIN {sys.executable} submission/code/analyze.py\n')
    f.flush()
    with (root/'submission/results/analysis_attempt2_stdout.txt').open('w',encoding='utf-8') as out, (root/'submission/results/analysis_attempt2_stderr.txt').open('w',encoding='utf-8') as err:
        p=subprocess.run([sys.executable,str(root/'submission/code/analyze.py')],cwd=root,stdout=out,stderr=err)
    f.write(f'{now()} END analysis, exit={p.returncode}; stdout=results/analysis_attempt2_stdout.txt; stderr=results/analysis_attempt2_stderr.txt\n')
    for item in sorted((root/'submission/results').iterdir()):
        f.write(f'  Output: {item.relative_to(root/"submission")} ({item.stat().st_size} bytes)\n')
print((root/'submission/results/analysis_attempt2_stdout.txt').read_text())
print('STDERR:',(root/'submission/results/analysis_attempt2_stderr.txt').read_text())
sys.exit(p.returncode)
