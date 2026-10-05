"""Repair the unused statsmodels import and create the analysis script."""
from pathlib import Path
here = Path(__file__).resolve().parent
s = (here / '01_describe_failed.py').read_text(encoding='utf-8')
s = s.replace('import statsmodels\n', '')
s = s.replace(", 'statsmodels': statsmodels.__version__", '')
s = s.replace('01_', '02_')
(here / '02_describe.py').write_text(s, encoding='utf-8')
print('Preserved failed source as 01_describe_failed.py; created 02_describe.py without the unused import.')
