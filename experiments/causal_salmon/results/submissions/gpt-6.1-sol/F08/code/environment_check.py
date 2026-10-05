import os, importlib.util
print('Bundled Python:',os.environ.get('CODEX_PRIMARY_RUNTIME_PYTHON'))
for name in ['numpy','pandas','scipy','statsmodels','matplotlib','sklearn','patsy']:
 print(name, bool(importlib.util.find_spec(name)))
