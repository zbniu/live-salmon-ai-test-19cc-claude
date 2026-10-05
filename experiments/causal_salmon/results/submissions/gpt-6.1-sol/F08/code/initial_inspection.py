import csv
from pathlib import Path
p=Path('upload/data(20261004-180753).csv')
with p.open() as f:
 r=csv.reader(f); print('HEADER:',next(r));
 for _,row in zip(range(5),r): print(row)
print('Bytes:',p.stat().st_size)
