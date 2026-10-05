"""Capture the actual analysis run, its errors, and the execution order."""
from pathlib import Path
import subprocess, sys
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[1]
out = root / 'results'
out.mkdir(parents=True,exist_ok=True)
log = root/'run_log.txt'
with log.open('a',encoding='utf-8') as f:
    f.write('Initial inspection: shell cat of the supplied study description, wc -l and head -n 6 of the supplied CSV succeeded (2001 lines including header).\n')
    f.write('That preliminary stdout exists in the session tool transcript only; no separate results file was retained. It was not a statistical analysis. No earlier statistical runs exist.\n')
    f.write(f'{datetime.now(timezone.utc).isoformat()} START code/run_analysis.py invokes code/analyze.py with {sys.executable}\n')
proc = subprocess.run([sys.executable,str(root/'code/analyze.py')],capture_output=True,text=True)
(out/'analysis_stdout.txt').write_text(proc.stdout,encoding='utf-8')
(out/'analysis_stderr.txt').write_text(proc.stderr,encoding='utf-8')
with log.open('a',encoding='utf-8') as f:
    f.write(f'{datetime.now(timezone.utc).isoformat()} END code/analyze.py exit={proc.returncode}; actual stdout -> results/analysis_stdout.txt; actual stderr -> results/analysis_stderr.txt.\n')
    if proc.returncode == 0:
        f.write('Analysis outputs, in creation order: inputs/data.csv and inputs/STUDY_DESCRIPTION.md (exact copies); results/input_manifest.json; results/validation.json; results/group_summary.csv; results/baseline_bins.csv; results/descriptive_ols.json; results/hypothetical_counterfactual_completions.csv; results/analysis_summary.json.\n')
    else:
        f.write('ERROR: analysis failed; partial files retained. See stderr.\n')
print(proc.stdout,end='')
print(proc.stderr,end='',file=sys.stderr)
sys.exit(proc.returncode)
