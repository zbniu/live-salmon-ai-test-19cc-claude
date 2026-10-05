cat 'upload/STUDY_DESCRIPTION(20261004-180712).md'
python - <<'PY'
from pathlib import Path
p=Path('upload/data(20261004-180712).csv')
print('\nCSV byte count:',p.stat().st_size)
with p.open() as f:
 for i,line in zip(range(8),f): print(line.rstrip())
PY
