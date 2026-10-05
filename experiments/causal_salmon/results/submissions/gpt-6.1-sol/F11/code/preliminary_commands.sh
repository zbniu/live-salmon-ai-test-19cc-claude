# Commands actually executed before the saved analysis scripts.
# Retained as source records, not rerun by the packaging step.
pwd && rg --files upload && cat 'upload/STUDY_DESCRIPTION(20261004-180818).md' && python - <<'PY'
from pathlib import Path
p=Path('upload/data(20261004-180818).csv')
print('CSV bytes:', p.stat().st_size)
with p.open() as f:
 for _ in range(8):
  print(f.readline().rstrip())
PY
mkdir -p submission/code submission/results && python - <<'PY'
import importlib.util
for x in ['numpy','pandas','scipy','statsmodels','sklearn','matplotlib']:
 print(x, bool(importlib.util.find_spec(x)))
PY
python - <<'PY'
import os
for k in ['CODEX_PRIMARY_RUNTIME_PYTHON','CODEX_PRIMARY_RUNTIME_ROOT']:
 print(k,os.environ.get(k))
PY
"$CODEX_PRIMARY_RUNTIME_PYTHON" - <<'PY'
import importlib.util
for m in ['statsmodels', 'patsy', 'sklearn', 'scipy']:
 print(m,bool(importlib.util.find_spec(m)))
PY
